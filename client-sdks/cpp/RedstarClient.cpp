#include "RedstarClient.h"
#include <sstream>
#include <chrono>
#include <algorithm>
#include <iostream>

namespace redstar {

RedstarClient::RedstarClient(const std::string& host, int port, int timeout_ms, bool auto_reconnect, int max_retries)
    : host_(host), port_(port), timeout_ms_(timeout_ms), auto_reconnect_(auto_reconnect), max_retries_(max_retries),
      socket_(INVALID_SOCKET), connected_(false), is_subscribed_(false)
#ifdef _WIN32
      , wsa_initialized_(false)
#endif
{
#ifdef _WIN32
    initializeWSA();
#endif
}

RedstarClient::~RedstarClient() {
    disconnect();
#ifdef _WIN32
    cleanupWSA();
#endif
}

RedstarClient::RedstarClient(RedstarClient&& other) noexcept
    : host_(std::move(other.host_)), port_(other.port_), timeout_ms_(other.timeout_ms_),
      auto_reconnect_(other.auto_reconnect_), max_retries_(other.max_retries_),
      socket_(other.socket_), connected_(other.connected_.load()),
      channel_callbacks_(std::move(other.channel_callbacks_)),
      pattern_callbacks_(std::move(other.pattern_callbacks_)),
      is_subscribed_(other.is_subscribed_.load())
#ifdef _WIN32
      , wsa_initialized_(other.wsa_initialized_)
#endif
{
    other.socket_ = INVALID_SOCKET;
    other.connected_ = false;
    other.is_subscribed_ = false;
#ifdef _WIN32
    other.wsa_initialized_ = false;
#endif
}

RedstarClient& RedstarClient::operator=(RedstarClient&& other) noexcept {
    if (this != &other) {
        disconnect();
        
        host_ = std::move(other.host_);
        port_ = other.port_;
        timeout_ms_ = other.timeout_ms_;
        auto_reconnect_ = other.auto_reconnect_;
        max_retries_ = other.max_retries_;
        socket_ = other.socket_;
        connected_ = other.connected_.load();
        channel_callbacks_ = std::move(other.channel_callbacks_);
        pattern_callbacks_ = std::move(other.pattern_callbacks_);
        is_subscribed_ = other.is_subscribed_.load();
#ifdef _WIN32
        wsa_initialized_ = other.wsa_initialized_;
        other.wsa_initialized_ = false;
#endif

        other.socket_ = INVALID_SOCKET;
        other.connected_ = false;
        other.is_subscribed_ = false;
    }
    return *this;
}

#ifdef _WIN32
void RedstarClient::initializeWSA() {
    WSADATA wsaData;
    int result = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (result != 0) {
        throw RedstarConnectionException("WSAStartup failed: " + std::to_string(result));
    }
    wsa_initialized_ = true;
}

void RedstarClient::cleanupWSA() {
    if (wsa_initialized_) {
        WSACleanup();
        wsa_initialized_ = false;
    }
}
#endif

void RedstarClient::connect() {
    std::lock_guard<std::mutex> lock(connection_mutex_);
    
    if (connected_.load()) {
        return; // Already connected
    }

    // Create socket
    socket_ = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (socket_ == INVALID_SOCKET) {
        throw RedstarConnectionException("Failed to create socket");
    }

    // Set timeout
#ifdef _WIN32
    DWORD timeout = timeout_ms_;
    setsockopt(socket_, SOL_SOCKET, SO_RCVTIMEO, (char*)&timeout, sizeof(timeout));
    setsockopt(socket_, SOL_SOCKET, SO_SNDTIMEO, (char*)&timeout, sizeof(timeout));
#else
    struct timeval tv;
    tv.tv_sec = timeout_ms_ / 1000;
    tv.tv_usec = (timeout_ms_ % 1000) * 1000;
    setsockopt(socket_, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    setsockopt(socket_, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));
#endif

    // Connect to server
    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(port_);
    
#ifdef _WIN32
    inet_pton(AF_INET, host_.c_str(), &serverAddr.sin_addr);
#else
    inet_aton(host_.c_str(), &serverAddr.sin_addr);
#endif

    int result = ::connect(socket_, (sockaddr*)&serverAddr, sizeof(serverAddr));
    if (result == SOCKET_ERROR) {
        closesocket(socket_);
        socket_ = INVALID_SOCKET;
        throw RedstarConnectionException("Failed to connect to " + host_ + ":" + std::to_string(port_));
    }

    connected_ = true;
}

void RedstarClient::disconnect() {
    std::lock_guard<std::mutex> lock(connection_mutex_);
    
    if (is_subscribed_.load()) {
        is_subscribed_ = false;
        if (pubsub_thread_.joinable()) {
            pubsub_thread_.join();
        }
    }
    
    if (socket_ != INVALID_SOCKET) {
        closesocket(socket_);
        socket_ = INVALID_SOCKET;
    }
    
    connected_ = false;
}

void RedstarClient::ensureConnected() {
    if (!connected_.load()) {
        if (auto_reconnect_) {
            for (int attempt = 0; attempt < max_retries_; ++attempt) {
                try {
                    connect();
                    return;
                } catch (const RedstarConnectionException&) {
                    if (attempt == max_retries_ - 1) {
                        throw;
                    }
                    std::this_thread::sleep_for(std::chrono::milliseconds(500 * (attempt + 1)));
                }
            }
        } else {
            throw RedstarConnectionException("Not connected to server");
        }
    }
}

std::string RedstarClient::buildRESPCommand(const std::vector<std::string>& args) {
    std::ostringstream oss;
    oss << "*" << args.size() << "\r\n";
    
    for (const auto& arg : args) {
        oss << "$" << arg.length() << "\r\n" << arg << "\r\n";
    }
    
    return oss.str();
}

RESPValue RedstarClient::sendCommand(const std::vector<std::string>& args) {
    std::lock_guard<std::mutex> lock(connection_mutex_);
    ensureConnected();

    // Build and send command
    std::string command = buildRESPCommand(args);
    int sent = send(socket_, command.c_str(), static_cast<int>(command.length()), 0);
    if (sent == SOCKET_ERROR) {
        connected_ = false;
        throw RedstarConnectionException("Failed to send command");
    }

    // Receive and parse response
    std::string response = receiveResponse();
    return parseRESPResponse(response);
}

std::string RedstarClient::receiveResponse() {
    std::string response;
    char buffer[4096];
    
    int received = recv(socket_, buffer, sizeof(buffer) - 1, 0);
    if (received == SOCKET_ERROR || received == 0) {
        connected_ = false;
        throw RedstarConnectionException("Failed to receive response");
    }
    
    buffer[received] = '\0';
    response = buffer;
    
    return response;
}

RESPValue RedstarClient::parseRESPResponse(const std::string& response) {
    if (response.empty()) {
        return RESPValue();
    }

    char type = response[0];
    std::string content = response.substr(1);
    
    switch (type) {
        case '+': // Simple string
            {
                size_t pos = content.find("\r\n");
                return RESPValue(content.substr(0, pos));
            }
        case '-': // Error
            {
                size_t pos = content.find("\r\n");
                throw RedstarCommandException(content.substr(0, pos));
            }
        case ':': // Integer
            {
                size_t pos = content.find("\r\n");
                return RESPValue(static_cast<int64_t>(std::stoll(content.substr(0, pos))));
            }
        case '$': // Bulk string
            {
                size_t pos = content.find("\r\n");
                int length = std::stoi(content.substr(0, pos));
                if (length == -1) {
                    return RESPValue(); // Nil
                }
                std::string data = content.substr(pos + 2, length);
                return RESPValue(data);
            }
        case '*': // Array
            {
                size_t pos = content.find("\r\n");
                int arrayLen = std::stoi(content.substr(0, pos));
                if (arrayLen == 0) {
                    return RESPValue(std::vector<RESPValue>());
                }
                
                std::vector<RESPValue> array;
                std::string remaining = content.substr(pos + 2);
                
                // Simplified array parsing - would need more robust implementation for production
                std::istringstream iss(remaining);
                std::string line;
                
                for (int i = 0; i < arrayLen && std::getline(iss, line); ++i) {
                    if (!line.empty() && line.back() == '\r') {
                        line.pop_back();
                    }
                    
                    if (line.empty()) continue;
                    
                    if (line[0] == '$') {
                        int len = std::stoi(line.substr(1));
                        if (len >= 0 && std::getline(iss, line)) {
                            if (!line.empty() && line.back() == '\r') {
                                line.pop_back();
                            }
                            array.emplace_back(line);
                        }
                    }
                }
                
                return RESPValue(array);
            }
        default:
            throw RedstarCommandException("Unknown RESP type: " + std::string(1, type));
    }
}

// String Operations
void RedstarClient::set(const std::string& key, const std::string& value) {
    RESPValue result = sendCommand({"SET", key, value});
    if (!result.isString() || result.getString() != "OK") {
        throw RedstarCommandException("SET command failed");
    }
}

std::string RedstarClient::get(const std::string& key) {
    RESPValue result = sendCommand({"GET", key});
    if (result.isNil()) {
        return "";
    }
    return result.getString();
}

int RedstarClient::del(const std::vector<std::string>& keys) {
    std::vector<std::string> args = {"DEL"};
    args.insert(args.end(), keys.begin(), keys.end());
    RESPValue result = sendCommand(args);
    return static_cast<int>(result.getInt());
}

int RedstarClient::exists(const std::vector<std::string>& keys) {
    std::vector<std::string> args = {"EXISTS"};
    args.insert(args.end(), keys.begin(), keys.end());
    RESPValue result = sendCommand(args);
    return static_cast<int>(result.getInt());
}

int64_t RedstarClient::incr(const std::string& key) {
    RESPValue result = sendCommand({"INCR", key});
    return result.getInt();
}

int64_t RedstarClient::decr(const std::string& key) {
    RESPValue result = sendCommand({"DECR", key});
    return result.getInt();
}

int RedstarClient::expire(const std::string& key, int seconds) {
    RESPValue result = sendCommand({"EXPIRE", key, std::to_string(seconds)});
    return static_cast<int>(result.getInt());
}

int RedstarClient::ttl(const std::string& key) {
    RESPValue result = sendCommand({"TTL", key});
    return static_cast<int>(result.getInt());
}

// List Operations
int64_t RedstarClient::lpush(const std::string& key, const std::vector<std::string>& values) {
    std::vector<std::string> args = {"LPUSH", key};
    args.insert(args.end(), values.begin(), values.end());
    RESPValue result = sendCommand(args);
    return result.getInt();
}

int64_t RedstarClient::rpush(const std::string& key, const std::vector<std::string>& values) {
    std::vector<std::string> args = {"RPUSH", key};
    args.insert(args.end(), values.begin(), values.end());
    RESPValue result = sendCommand(args);
    return result.getInt();
}

std::string RedstarClient::lpop(const std::string& key) {
    RESPValue result = sendCommand({"LPOP", key});
    if (result.isNil()) {
        return "";
    }
    return result.getString();
}

std::string RedstarClient::rpop(const std::string& key) {
    RESPValue result = sendCommand({"RPOP", key});
    if (result.isNil()) {
        return "";
    }
    return result.getString();
}

int64_t RedstarClient::llen(const std::string& key) {
    RESPValue result = sendCommand({"LLEN", key});
    return result.getInt();
}

std::vector<std::string> RedstarClient::lrange(const std::string& key, int start, int stop) {
    RESPValue result = sendCommand({"LRANGE", key, std::to_string(start), std::to_string(stop)});
    std::vector<std::string> stringArray;
    
    if (result.isArray()) {
        const auto& array = result.getArray();
        for (const auto& item : array) {
            if (item.isString()) {
                stringArray.push_back(item.getString());
            }
        }
    }
    
    return stringArray;
}

// Set Operations
int64_t RedstarClient::sadd(const std::string& key, const std::vector<std::string>& members) {
    std::vector<std::string> args = {"SADD", key};
    args.insert(args.end(), members.begin(), members.end());
    RESPValue result = sendCommand(args);
    return result.getInt();
}

int64_t RedstarClient::srem(const std::string& key, const std::vector<std::string>& members) {
    std::vector<std::string> args = {"SREM", key};
    args.insert(args.end(), members.begin(), members.end());
    RESPValue result = sendCommand(args);
    return result.getInt();
}

std::vector<std::string> RedstarClient::smembers(const std::string& key) {
    RESPValue result = sendCommand({"SMEMBERS", key});
    std::vector<std::string> stringArray;
    
    if (result.isArray()) {
        const auto& array = result.getArray();
        for (const auto& item : array) {
            if (item.isString()) {
                stringArray.push_back(item.getString());
            }
        }
    }
    
    return stringArray;
}

int64_t RedstarClient::scard(const std::string& key) {
    RESPValue result = sendCommand({"SCARD", key});
    return result.getInt();
}

int RedstarClient::sismember(const std::string& key, const std::string& member) {
    RESPValue result = sendCommand({"SISMEMBER", key, member});
    return static_cast<int>(result.getInt());
}

// Hash Operations
int RedstarClient::hset(const std::string& key, const std::string& field, const std::string& value) {
    RESPValue result = sendCommand({"HSET", key, field, value});
    return static_cast<int>(result.getInt());
}

std::string RedstarClient::hget(const std::string& key, const std::string& field) {
    RESPValue result = sendCommand({"HGET", key, field});
    if (result.isNil()) {
        return "";
    }
    return result.getString();
}

int RedstarClient::hdel(const std::string& key, const std::vector<std::string>& fields) {
    std::vector<std::string> args = {"HDEL", key};
    args.insert(args.end(), fields.begin(), fields.end());
    RESPValue result = sendCommand(args);
    return static_cast<int>(result.getInt());
}

std::map<std::string, std::string> RedstarClient::hgetall(const std::string& key) {
    RESPValue result = sendCommand({"HGETALL", key});
    std::map<std::string, std::string> hash;
    
    if (result.isArray()) {
        const auto& array = result.getArray();
        for (size_t i = 0; i < array.size() - 1; i += 2) {
            if (array[i].isString() && array[i + 1].isString()) {
                hash[array[i].getString()] = array[i + 1].getString();
            }
        }
    }
    
    return hash;
}

std::vector<std::string> RedstarClient::hkeys(const std::string& key) {
    RESPValue result = sendCommand({"HKEYS", key});
    std::vector<std::string> stringArray;
    
    if (result.isArray()) {
        const auto& array = result.getArray();
        for (const auto& item : array) {
            if (item.isString()) {
                stringArray.push_back(item.getString());
            }
        }
    }
    
    return stringArray;
}

std::vector<std::string> RedstarClient::hvals(const std::string& key) {
    RESPValue result = sendCommand({"HVALS", key});
    std::vector<std::string> stringArray;
    
    if (result.isArray()) {
        const auto& array = result.getArray();
        for (const auto& item : array) {
            if (item.isString()) {
                stringArray.push_back(item.getString());
            }
        }
    }
    
    return stringArray;
}

// Server Operations
std::string RedstarClient::ping() {
    RESPValue result = sendCommand({"PING"});
    return result.getString();
}

std::string RedstarClient::ping(const std::string& message) {
    RESPValue result = sendCommand({"PING", message});
    return result.getString();
}

std::string RedstarClient::info() {
    RESPValue result = sendCommand({"INFO"});
    return result.getString();
}

std::string RedstarClient::flushall() {
    RESPValue result = sendCommand({"FLUSHALL"});
    return result.getString();
}

std::vector<std::string> RedstarClient::keys(const std::string& pattern) {
    RESPValue result = sendCommand({"KEYS", pattern});
    std::vector<std::string> stringArray;
    
    if (result.isArray()) {
        const auto& array = result.getArray();
        for (const auto& item : array) {
            if (item.isString()) {
                stringArray.push_back(item.getString());
            }
        }
    }
    
    return stringArray;
}

// Pub/Sub Operations
void RedstarClient::subscribe(const std::string& channel, PubSubCallback callback) {
    {
        std::lock_guard<std::mutex> lock(pubsub_mutex_);
        if (!is_subscribed_.load()) {
            is_subscribed_ = true;
            pubsub_thread_ = std::thread(&RedstarClient::pubsubListener, this);
        }
        channel_callbacks_[channel] = callback;
    }
    
    sendCommand({"SUBSCRIBE", channel});
}

void RedstarClient::psubscribe(const std::string& pattern, PubSubCallback callback) {
    {
        std::lock_guard<std::mutex> lock(pubsub_mutex_);
        if (!is_subscribed_.load()) {
            is_subscribed_ = true;
            pubsub_thread_ = std::thread(&RedstarClient::pubsubListener, this);
        }
        pattern_callbacks_[pattern] = callback;
    }
    
    sendCommand({"PSUBSCRIBE", pattern});
}

void RedstarClient::unsubscribe(const std::string& channel) {
    {
        std::lock_guard<std::mutex> lock(pubsub_mutex_);
        channel_callbacks_.erase(channel);
    }
    sendCommand({"UNSUBSCRIBE", channel});
}

void RedstarClient::punsubscribe(const std::string& pattern) {
    {
        std::lock_guard<std::mutex> lock(pubsub_mutex_);
        pattern_callbacks_.erase(pattern);
    }
    sendCommand({"PUNSUBSCRIBE", pattern});
}

int64_t RedstarClient::publish(const std::string& channel, const std::string& message) {
    RESPValue result = sendCommand({"PUBLISH", channel, message});
    return result.getInt();
}

void RedstarClient::pubsubListener() {
    // Simplified pub/sub listener - would need more robust implementation
    while (is_subscribed_.load()) {
        try {
            std::string response = receiveResponse();
            // Parse pub/sub messages and call callbacks
            // This is a simplified implementation
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        } catch (const std::exception&) {
            // Handle errors or connection loss
            break;
        }
    }
}

// Utility functions
namespace utils {
    std::string quickSet(const std::string& key, const std::string& value, const std::string& host, int port) {
        RedstarClient client(host, port);
        client.connect();
        client.set(key, value);
        return "OK";
    }

    std::string quickGet(const std::string& key, const std::string& host, int port) {
        RedstarClient client(host, port);
        client.connect();
        return client.get(key);
    }
}

} // namespace redstar