#include "RedstarClient.h"
#include <iostream>
#include <thread>
#include <chrono>

using namespace redstar;

void basicOperationsExample() {
    std::cout << "=== Basic Operations Example ===" << std::endl;
    
    try {
        RedstarClient client("localhost", 6379);
        client.connect();
        
        // String operations
        std::cout << "String operations:" << std::endl;
        client.set("hello", "world");
        std::string value = client.get("hello");
        std::cout << "GET hello: " << value << std::endl;
        
        // Increment operations
        int64_t counter = client.incr("counter");
        std::cout << "INCR counter: " << counter << std::endl;
        
        // List operations
        std::cout << "\nList operations:" << std::endl;
        client.lpush("mylist", {"item1", "item2", "item3"});
        int64_t length = client.llen("mylist");
        std::cout << "List length: " << length << std::endl;
        
        auto items = client.lrange("mylist", 0, -1);
        std::cout << "List items: ";
        for (const auto& item : items) {
            std::cout << item << " ";
        }
        std::cout << std::endl;
        
        // Hash operations
        std::cout << "\nHash operations:" << std::endl;
        client.hset("user:1", "name", "Alice");
        client.hset("user:1", "age", "30");
        client.hset("user:1", "city", "New York");
        
        auto hash = client.hgetall("user:1");
        std::cout << "User hash: ";
        for (const auto& pair : hash) {
            std::cout << pair.first << "=" << pair.second << " ";
        }
        std::cout << std::endl;
        
        // Set operations
        std::cout << "\nSet operations:" << std::endl;
        client.sadd("myset", {"member1", "member2", "member3"});
        auto members = client.smembers("myset");
        std::cout << "Set members: ";
        for (const auto& member : members) {
            std::cout << member << " ";
        }
        std::cout << std::endl;
        
        // Server operations
        std::cout << "\nServer operations:" << std::endl;
        std::string pong = client.ping();
        std::cout << "PING: " << pong << std::endl;
        
        std::string pingMsg = client.ping("Hello Server!");
        std::cout << "PING with message: " << pingMsg << std::endl;
        
    } catch (const RedstarException& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }
}

void pubsubExample() {
    std::cout << "\n=== Pub/Sub Example ===" << std::endl;
    
    try {
        // Subscriber
        RedstarClient subscriber("localhost", 6379);
        subscriber.connect();
        
        // Publisher 
        RedstarClient publisher("localhost", 6379);
        publisher.connect();
        
        // Subscribe with callback
        std::cout << "Subscribing to 'news' channel..." << std::endl;
        subscriber.subscribe("news", [](const std::string& channel, const std::string& message) {
            std::cout << "[" << channel << "] " << message << std::endl;
        });
        
        // Give subscription time to register
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        
        // Publish messages
        std::cout << "Publishing messages..." << std::endl;
        for (int i = 1; i <= 3; i++) {
            std::string message = "Breaking news #" + std::to_string(i);
            int64_t subscribers = publisher.publish("news", message);
            std::cout << "Published to " << subscribers << " subscribers: " << message << std::endl;
            std::this_thread::sleep_for(std::chrono::milliseconds(500));
        }
        
        // Allow time for message processing
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));
        
    } catch (const RedstarException& e) {
        std::cerr << "Pub/Sub Error: " << e.what() << std::endl;
    }
}

void performanceExample() {
    std::cout << "\n=== Performance Example ===" << std::endl;
    
    try {
        RedstarClient client("localhost", 6379);
        client.connect();
        
        const int numOperations = 1000;
        
        // Measure SET operations
        auto start = std::chrono::high_resolution_clock::now();
        
        for (int i = 0; i < numOperations; i++) {
            client.set("key:" + std::to_string(i), "value:" + std::to_string(i));
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        
        std::cout << "SET " << numOperations << " keys in " << duration.count() << "ms" << std::endl;
        std::cout << "Rate: " << (numOperations * 1000.0) / duration.count() << " ops/sec" << std::endl;
        
        // Measure GET operations
        start = std::chrono::high_resolution_clock::now();
        
        for (int i = 0; i < numOperations; i++) {
            std::string value = client.get("key:" + std::to_string(i));
            (void)value; // Suppress unused variable warning
        }
        
        end = std::chrono::high_resolution_clock::now();
        duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        
        std::cout << "GET " << numOperations << " keys in " << duration.count() << "ms" << std::endl;
        std::cout << "Rate: " << (numOperations * 1000.0) / duration.count() << " ops/sec" << std::endl;
        
        // Cleanup
        client.flushall();
        std::cout << "Database cleared." << std::endl;
        
    } catch (const RedstarException& e) {
        std::cerr << "Performance Error: " << e.what() << std::endl;
    }
}

void errorHandlingExample() {
    std::cout << "\n=== Error Handling Example ===" << std::endl;
    
    // Connection error example
    try {
        RedstarClient client("nonexistent-host", 6379);
        client.connect();
    } catch (const RedstarConnectionException& e) {
        std::cout << "Expected connection error: " << e.what() << std::endl;
    }
    
    // Command error example
    try {
        RedstarClient client("localhost", 6379);
        client.connect();
        
        // Set a string value
        client.set("stringkey", "stringvalue");
        
        // Try to perform list operation on string key (should fail)
        client.lpush("stringkey", {"item"});
        
    } catch (const RedstarCommandException& e) {
        std::cout << "Expected command error: " << e.what() << std::endl;
    } catch (const RedstarConnectionException& e) {
        std::cout << "Connection error: " << e.what() << std::endl;
    }
}

void utilityFunctionsExample() {
    std::cout << "\n=== Utility Functions Example ===" << std::endl;
    
    try {
        // Quick operations without managing connection
        std::cout << "Using utility functions..." << std::endl;
        
        utils::quickSet("quickkey", "quickvalue");
        std::string value = utils::quickGet("quickkey");
        
        std::cout << "Quick GET quickkey: " << value << std::endl;
        
    } catch (const RedstarException& e) {
        std::cerr << "Utility Error: " << e.what() << std::endl;
    }
}

int main() {
    std::cout << "Redstar C++ Client SDK Examples" << std::endl;
    std::cout << "================================" << std::endl;
    
    // Run all examples
    basicOperationsExample();
    pubsubExample();
    performanceExample();
    errorHandlingExample();
    utilityFunctionsExample();
    
    std::cout << "\nAll examples completed!" << std::endl;
    return 0;
}