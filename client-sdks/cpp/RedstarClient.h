#pragma once

#include <string>
#include <vector>
#include <map>
#include <memory>
#include <functional>
#include <thread>
#include <mutex>
#include <atomic>
#include <exception>

#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")
    typedef int socklen_t;
#else
    #include <sys/socket.h>
    #include <arpa/inet.h>
    #include <netdb.h>
    #include <unistd.h>
    typedef int SOCKET;
    #define INVALID_SOCKET -1
    #define SOCKET_ERROR -1
    #define closesocket close
#endif

/**
 * @file RedstarClient.h
 * @brief Redstar C++ Client SDK
 * 
 * A comprehensive C++ client for connecting to Redstar Redis-compatible server
 * 
 * Features:
 * - All basic Redis commands (strings, lists, sets, hashes)
 * - Pub/Sub operations with callbacks
 * - Connection management and reconnection
 * - Thread-safe operations
 * - RAII resource management
 * - Modern C++ design (C++11/14/17 compatible)
 * 
 * @author Redstar Project
 * @version 1.0.0
 */

namespace redstar {

/**
 * @brief Base exception class for Redstar client errors
 */
class RedstarException : public std::exception {
private:
    std::string message_;

public:
    explicit RedstarException(const std::string& message) : message_(message) {}
    virtual const char* what() const noexcept override {
        return message_.c_str();
    }
};

/**
 * @brief Connection related exceptions
 */
class RedstarConnectionException : public RedstarException {
public:
    explicit RedstarConnectionException(const std::string& message) 
        : RedstarException("Connection error: " + message) {}
};

/**
 * @brief Command execution exceptions
 */
class RedstarCommandException : public RedstarException {
public:
    explicit RedstarCommandException(const std::string& message) 
        : RedstarException("Command error: " + message) {}
};

/**
 * @brief RESP response variant type
 */
class RESPValue {
public:
    enum Type {
        NIL,
        STRING,
        INTEGER,
        ARRAY,
        ERROR
    };

private:
    Type type_;
    std::string string_value_;
    int64_t int_value_;
    std::vector<RESPValue> array_value_;

public:
    RESPValue() : type_(NIL), int_value_(0) {}
    explicit RESPValue(const std::string& value) : type_(STRING), string_value_(value), int_value_(0) {}
    explicit RESPValue(int64_t value) : type_(INTEGER), int_value_(value) {}
    explicit RESPValue(const std::vector<RESPValue>& value) : type_(ARRAY), array_value_(value), int_value_(0) {}

    Type getType() const { return type_; }
    const std::string& getString() const { return string_value_; }
    int64_t getInt() const { return int_value_; }
    const std::vector<RESPValue>& getArray() const { return array_value_; }

    bool isNil() const { return type_ == NIL; }
    bool isString() const { return type_ == STRING; }
    bool isInt() const { return type_ == INTEGER; }
    bool isArray() const { return type_ == ARRAY; }
    bool isError() const { return type_ == ERROR; }

    static RESPValue createError(const std::string& message) {
        RESPValue val;
        val.type_ = ERROR;
        val.string_value_ = message;
        return val;
    }
};

/**
 * @brief Redstar C++ Client SDK
 * 
 * A comprehensive client for interacting with Redstar server with support for:
 * - All basic Redis commands (strings, lists, sets, hashes)
 * - Pub/Sub operations with callbacks
 * - Connection management and reconnection
 * - Thread-safe operations
 * - RAII resource management
 */
class RedstarClient {
public:
    using PubSubCallback = std::function<void(const std::string&, const std::string&)>;

private:
    std::string host_;
    int port_;
    int timeout_ms_;
    bool auto_reconnect_;
    int max_retries_;

    SOCKET socket_;
    std::atomic<bool> connected_;
    std::mutex connection_mutex_;

    // Pub/Sub support
    std::thread pubsub_thread_;
    std::map<std::string, PubSubCallback> channel_callbacks_;
    std::map<std::string, PubSubCallback> pattern_callbacks_;
    std::atomic<bool> is_subscribed_;
    std::mutex pubsub_mutex_;

#ifdef _WIN32
    bool wsa_initialized_;
#endif

public:
    /**
     * @brief Create a new Redstar client with default settings
     */
    RedstarClient() : RedstarClient("localhost", 6379) {}

    /**
     * @brief Create a new Redstar client
     * @param host Server hostname
     * @param port Server port
     */
    RedstarClient(const std::string& host, int port)
        : RedstarClient(host, port, 30000, true, 3) {}

    /**
     * @brief Create a new Redstar client with full configuration
     * @param host Server hostname
     * @param port Server port
     * @param timeout_ms Socket timeout in milliseconds
     * @param auto_reconnect Enable automatic reconnection
     * @param max_retries Maximum reconnection attempts
     */
    RedstarClient(const std::string& host, int port, int timeout_ms, bool auto_reconnect, int max_retries);

    /**
     * @brief Destructor - automatically disconnects
     */
    ~RedstarClient();

    // Disable copy constructor and assignment operator
    RedstarClient(const RedstarClient&) = delete;
    RedstarClient& operator=(const RedstarClient&) = delete;

    // Enable move constructor and assignment operator
    RedstarClient(RedstarClient&& other) noexcept;
    RedstarClient& operator=(RedstarClient&& other) noexcept;

    /**
     * @brief Connect to Redstar server
     * @throws RedstarConnectionException if connection fails
     */
    void connect();

    /**
     * @brief Disconnect from server
     */
    void disconnect();

    /**
     * @brief Check if client is connected
     * @return true if connected, false otherwise
     */
    bool isConnected() const { return connected_.load(); }

    // String Operations
    void set(const std::string& key, const std::string& value);
    std::string get(const std::string& key);
    int del(const std::vector<std::string>& keys);
    int exists(const std::vector<std::string>& keys);
    int64_t incr(const std::string& key);
    int64_t decr(const std::string& key);
    int expire(const std::string& key, int seconds);
    int ttl(const std::string& key);

    // List Operations
    int64_t lpush(const std::string& key, const std::vector<std::string>& values);
    int64_t rpush(const std::string& key, const std::vector<std::string>& values);
    std::string lpop(const std::string& key);
    std::string rpop(const std::string& key);
    int64_t llen(const std::string& key);
    std::vector<std::string> lrange(const std::string& key, int start, int stop);

    // Set Operations
    int64_t sadd(const std::string& key, const std::vector<std::string>& members);
    int64_t srem(const std::string& key, const std::vector<std::string>& members);
    std::vector<std::string> smembers(const std::string& key);
    int64_t scard(const std::string& key);
    int sismember(const std::string& key, const std::string& member);

    // Hash Operations
    int hset(const std::string& key, const std::string& field, const std::string& value);
    std::string hget(const std::string& key, const std::string& field);
    int hdel(const std::string& key, const std::vector<std::string>& fields);
    std::map<std::string, std::string> hgetall(const std::string& key);
    std::vector<std::string> hkeys(const std::string& key);
    std::vector<std::string> hvals(const std::string& key);

    // Server Operations
    std::string ping();
    std::string ping(const std::string& message);
    std::string info();
    std::string flushall();
    std::vector<std::string> keys(const std::string& pattern = "*");

    // Pub/Sub Operations
    void subscribe(const std::string& channel, PubSubCallback callback);
    void psubscribe(const std::string& pattern, PubSubCallback callback);
    void unsubscribe(const std::string& channel);
    void punsubscribe(const std::string& pattern);
    int64_t publish(const std::string& channel, const std::string& message);

private:
    void ensureConnected();
    RESPValue sendCommand(const std::vector<std::string>& args);
    std::string buildRESPCommand(const std::vector<std::string>& args);
    RESPValue parseRESPResponse(const std::string& response);
    std::string receiveResponse();
    void pubsubListener();

#ifdef _WIN32
    void initializeWSA();
    void cleanupWSA();
#endif
};

// Convenience functions for single operations
namespace utils {
    std::string quickSet(const std::string& key, const std::string& value, 
                        const std::string& host = "localhost", int port = 6379);
    std::string quickGet(const std::string& key, 
                        const std::string& host = "localhost", int port = 6379);
}

} // namespace redstar