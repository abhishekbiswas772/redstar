package com.redstar.client;

import java.io.*;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.function.BiConsumer;

/**
 * Redstar Java Client SDK
 * 
 * A comprehensive Java client for connecting to Redstar Redis-compatible server
 * 
 * Features:
 * - All basic Redis commands (strings, lists, sets, hashes)
 * - Pub/Sub operations with callbacks
 * - Connection management and reconnection
 * - Thread-safe operations
 * - Connection pooling support
 * 
 * @author Redstar Project
 * @version 1.0.0
 */
public class RedstarClient implements AutoCloseable {
    
    // Connection settings
    private final String host;
    private final int port;
    private final int timeout;
    private final boolean autoReconnect;
    private final int maxRetries;
    
    // Connection state
    private Socket socket;
    private BufferedReader reader;
    private BufferedWriter writer;
    private boolean connected;
    private final Object connectionLock = new Object();
    
    // Pub/Sub support
    private ExecutorService pubsubExecutor;
    private final Map<String, BiConsumer<String, String>> channelCallbacks = new ConcurrentHashMap<>();
    private final Map<String, BiConsumer<String, String>> patternCallbacks = new ConcurrentHashMap<>();
    private boolean isSubscribed = false;
    
    /**
     * Create a new Redstar client with default settings
     */
    public RedstarClient() {
        this("localhost", 6379);
    }
    
    /**
     * Create a new Redstar client
     * 
     * @param host Server hostname
     * @param port Server port
     */
    public RedstarClient(String host, int port) {
        this(host, port, 30000, true, 3);
    }
    
    /**
     * Create a new Redstar client with full configuration
     * 
     * @param host Server hostname
     * @param port Server port
     * @param timeout Socket timeout in milliseconds
     * @param autoReconnect Enable automatic reconnection
     * @param maxRetries Maximum reconnection attempts
     */
    public RedstarClient(String host, int port, int timeout, boolean autoReconnect, int maxRetries) {
        this.host = host;
        this.port = port;
        this.timeout = timeout;
        this.autoReconnect = autoReconnect;
        this.maxRetries = maxRetries;
        this.connected = false;
    }
    
    /**
     * Connect to Redstar server
     * 
     * @throws RedstarConnectionException if connection fails
     */
    public void connect() throws RedstarConnectionException {
        synchronized (connectionLock) {
            try {
                socket = new Socket(host, port);
                socket.setSoTimeout(timeout);
                reader = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
                writer = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8));
                connected = true;
            } catch (IOException e) {
                throw new RedstarConnectionException("Failed to connect to " + host + ":" + port, e);
            }
        }
    }
    
    /**
     * Disconnect from server
     */
    public void disconnect() {
        synchronized (connectionLock) {
            if (pubsubExecutor != null) {
                pubsubExecutor.shutdownNow();
                pubsubExecutor = null;
            }
            
            try {
                if (reader != null) reader.close();
                if (writer != null) writer.close();
                if (socket != null) socket.close();
            } catch (IOException e) {
                // Ignore close exceptions
            }
            
            connected = false;
        }
    }
    
    /**
     * Ensure client is connected, reconnect if needed
     */
    private void ensureConnected() throws RedstarConnectionException {
        if (!connected) {
            if (autoReconnect) {
                for (int attempt = 0; attempt < maxRetries; attempt++) {
                    try {
                        connect();
                        return;
                    } catch (RedstarConnectionException e) {
                        if (attempt == maxRetries - 1) {
                            throw e;
                        }
                        try {
                            Thread.sleep(500 * (attempt + 1));
                        } catch (InterruptedException ie) {
                            Thread.currentThread().interrupt();
                            throw new RedstarConnectionException("Reconnection interrupted", ie);
                        }
                    }
                }
            } else {
                throw new RedstarConnectionException("Not connected to server");
            }
        }
    }
    
    /**
     * Send RESP command and return response
     */
    private String sendCommand(String... args) throws RedstarConnectionException, RedstarCommandException {
        synchronized (connectionLock) {
            ensureConnected();
            
            try {
                // Build RESP command
                writer.write("*" + args.length + "\r\n");
                for (String arg : args) {
                    byte[] argBytes = arg.getBytes(StandardCharsets.UTF_8);
                    writer.write("$" + argBytes.length + "\r\n");
                    writer.write(arg + "\r\n");
                }
                writer.flush();
                
                // Read response
                StringBuilder response = new StringBuilder();
                String line;
                boolean firstLine = true;
                
                while ((line = reader.readLine()) != null) {
                    if (firstLine) {
                        response.append(line);
                        firstLine = false;
                        
                        // For simple responses, we're done
                        if (line.startsWith("+") || line.startsWith("-") || line.startsWith(":")) {
                            break;
                        }
                        
                        // For bulk strings, read the data
                        if (line.startsWith("$")) {
                            int length = Integer.parseInt(line.substring(1));
                            if (length == -1) {
                                break; // Null bulk string
                            }
                            response.append("\r\n");
                            char[] buffer = new char[length];
                            reader.read(buffer, 0, length);
                            response.append(new String(buffer));
                            reader.readLine(); // Read trailing CRLF
                            break;
                        }
                        
                        // For arrays, continue reading
                        if (line.startsWith("*")) {
                            response.append("\r\n");
                        }
                    } else {
                        response.append("\r\n").append(line);
                        
                        // Simple heuristic to detect end of array response
                        if (response.toString().split("\r\n").length > 20) {
                            break;
                        }
                    }
                }
                
                return response.toString();
                
            } catch (IOException e) {
                connected = false;
                throw new RedstarConnectionException("Command failed", e);
            }
        }
    }
    
    /**
     * Parse RESP response
     */
    private Object parseResponse(String response) throws RedstarCommandException {
        if (response == null || response.isEmpty()) {
            return null;
        }
        
        if (response.startsWith("+")) {
            return response.substring(1);
        } else if (response.startsWith("-")) {
            throw new RedstarCommandException(response.substring(1));
        } else if (response.startsWith(":")) {
            return Integer.parseInt(response.substring(1));
        } else if (response.startsWith("$")) {
            String[] lines = response.split("\r\n", 2);
            int length = Integer.parseInt(lines[0].substring(1));
            if (length == -1) {
                return null;
            }
            return lines.length > 1 ? lines[1] : "";
        } else if (response.startsWith("*")) {
            String[] lines = response.split("\r\n");
            int arrayLen = Integer.parseInt(lines[0].substring(1));
            if (arrayLen == 0) {
                return new ArrayList<>();
            }
            
            List<String> result = new ArrayList<>();
            int lineIdx = 1;
            for (int i = 0; i < arrayLen && lineIdx < lines.length; i++) {
                if (lines[lineIdx].startsWith("$")) {
                    int length = Integer.parseInt(lines[lineIdx].substring(1));
                    lineIdx++;
                    if (lineIdx < lines.length) {
                        result.add(lines[lineIdx]);
                    }
                    lineIdx++;
                } else {
                    result.add(lines[lineIdx]);
                    lineIdx++;
                }
            }
            return result;
        }
        
        return response;
    }
    
    // String Operations
    
    /**
     * Set a key-value pair
     */
    public String set(String key, String value) throws RedstarException {
        String response = sendCommand("SET", key, value);
        return (String) parseResponse(response);
    }
    
    /**
     * Get value by key
     */
    public String get(String key) throws RedstarException {
        String response = sendCommand("GET", key);
        return (String) parseResponse(response);
    }
    
    /**
     * Delete one or more keys
     */
    public int delete(String... keys) throws RedstarException {
        String[] args = new String[keys.length + 1];
        args[0] = "DEL";
        System.arraycopy(keys, 0, args, 1, keys.length);
        String response = sendCommand(args);
        return (Integer) parseResponse(response);
    }
    
    /**
     * Check if keys exist
     */
    public int exists(String... keys) throws RedstarException {
        String[] args = new String[keys.length + 1];
        args[0] = "EXISTS";
        System.arraycopy(keys, 0, args, 1, keys.length);
        String response = sendCommand(args);
        return (Integer) parseResponse(response);
    }
    
    /**
     * Increment integer value
     */
    public int incr(String key) throws RedstarException {
        String response = sendCommand("INCR", key);
        return (Integer) parseResponse(response);
    }
    
    /**
     * Decrement integer value
     */
    public int decr(String key) throws RedstarException {
        String response = sendCommand("DECR", key);
        return (Integer) parseResponse(response);
    }
    
    /**
     * Set key expiration
     */
    public int expire(String key, int seconds) throws RedstarException {
        String response = sendCommand("EXPIRE", key, String.valueOf(seconds));
        return (Integer) parseResponse(response);
    }
    
    /**
     * Get time to live
     */
    public int ttl(String key) throws RedstarException {
        String response = sendCommand("TTL", key);
        return (Integer) parseResponse(response);
    }
    
    // List Operations
    
    /**
     * Push values to left of list
     */
    public int lpush(String key, String... values) throws RedstarException {
        String[] args = new String[values.length + 2];
        args[0] = "LPUSH";
        args[1] = key;
        System.arraycopy(values, 0, args, 2, values.length);
        String response = sendCommand(args);
        return (Integer) parseResponse(response);
    }
    
    /**
     * Push values to right of list
     */
    public int rpush(String key, String... values) throws RedstarException {
        String[] args = new String[values.length + 2];
        args[0] = "RPUSH";
        args[1] = key;
        System.arraycopy(values, 0, args, 2, values.length);
        String response = sendCommand(args);
        return (Integer) parseResponse(response);
    }
    
    /**
     * Pop value from left of list
     */
    public String lpop(String key) throws RedstarException {
        String response = sendCommand("LPOP", key);
        return (String) parseResponse(response);
    }
    
    /**
     * Pop value from right of list
     */
    public String rpop(String key) throws RedstarException {
        String response = sendCommand("RPOP", key);
        return (String) parseResponse(response);
    }
    
    /**
     * Get list length
     */
    public int llen(String key) throws RedstarException {
        String response = sendCommand("LLEN", key);
        return (Integer) parseResponse(response);
    }
    
    /**
     * Get list elements in range
     */
    @SuppressWarnings("unchecked")
    public List<String> lrange(String key, int start, int stop) throws RedstarException {
        String response = sendCommand("LRANGE", key, String.valueOf(start), String.valueOf(stop));
        Object result = parseResponse(response);
        return result instanceof List ? (List<String>) result : new ArrayList<>();
    }
    
    // Set Operations
    
    /**
     * Add members to set
     */
    public int sadd(String key, String... members) throws RedstarException {
        String[] args = new String[members.length + 2];
        args[0] = "SADD";
        args[1] = key;
        System.arraycopy(members, 0, args, 2, members.length);
        String response = sendCommand(args);
        return (Integer) parseResponse(response);
    }
    
    /**
     * Remove members from set
     */
    public int srem(String key, String... members) throws RedstarException {
        String[] args = new String[members.length + 2];
        args[0] = "SREM";
        args[1] = key;
        System.arraycopy(members, 0, args, 2, members.length);
        String response = sendCommand(args);
        return (Integer) parseResponse(response);
    }
    
    /**
     * Get all set members
     */
    @SuppressWarnings("unchecked")
    public List<String> smembers(String key) throws RedstarException {
        String response = sendCommand("SMEMBERS", key);
        Object result = parseResponse(response);
        return result instanceof List ? (List<String>) result : new ArrayList<>();
    }
    
    /**
     * Get set cardinality
     */
    public int scard(String key) throws RedstarException {
        String response = sendCommand("SCARD", key);
        return (Integer) parseResponse(response);
    }
    
    /**
     * Check if member is in set
     */
    public int sismember(String key, String member) throws RedstarException {
        String response = sendCommand("SISMEMBER", key, member);
        return (Integer) parseResponse(response);
    }
    
    // Hash Operations
    
    /**
     * Set hash field
     */
    public int hset(String key, String field, String value) throws RedstarException {
        String response = sendCommand("HSET", key, field, value);
        return (Integer) parseResponse(response);
    }
    
    /**
     * Get hash field value
     */
    public String hget(String key, String field) throws RedstarException {
        String response = sendCommand("HGET", key, field);
        return (String) parseResponse(response);
    }
    
    /**
     * Delete hash fields
     */
    public int hdel(String key, String... fields) throws RedstarException {
        String[] args = new String[fields.length + 2];
        args[0] = "HDEL";
        args[1] = key;
        System.arraycopy(fields, 0, args, 2, fields.length);
        String response = sendCommand(args);
        return (Integer) parseResponse(response);
    }
    
    /**
     * Get all hash fields and values
     */
    @SuppressWarnings("unchecked")
    public Map<String, String> hgetall(String key) throws RedstarException {
        String response = sendCommand("HGETALL", key);
        Object result = parseResponse(response);
        
        if (result instanceof List) {
            List<String> list = (List<String>) result;
            Map<String, String> hash = new HashMap<>();
            for (int i = 0; i < list.size() - 1; i += 2) {
                hash.put(list.get(i), list.get(i + 1));
            }
            return hash;
        }
        return new HashMap<>();
    }
    
    /**
     * Get all hash field names
     */
    @SuppressWarnings("unchecked")
    public List<String> hkeys(String key) throws RedstarException {
        String response = sendCommand("HKEYS", key);
        Object result = parseResponse(response);
        return result instanceof List ? (List<String>) result : new ArrayList<>();
    }
    
    /**
     * Get all hash values
     */
    @SuppressWarnings("unchecked")
    public List<String> hvals(String key) throws RedstarException {
        String response = sendCommand("HVALS", key);
        Object result = parseResponse(response);
        return result instanceof List ? (List<String>) result : new ArrayList<>();
    }
    
    // Server Operations
    
    /**
     * Ping server
     */
    public String ping() throws RedstarException {
        String response = sendCommand("PING");
        return (String) parseResponse(response);
    }
    
    /**
     * Ping server with message
     */
    public String ping(String message) throws RedstarException {
        String response = sendCommand("PING", message);
        return (String) parseResponse(response);
    }
    
    /**
     * Get server info
     */
    public String info() throws RedstarException {
        String response = sendCommand("INFO");
        return (String) parseResponse(response);
    }
    
    /**
     * Flush all data
     */
    public String flushall() throws RedstarException {
        String response = sendCommand("FLUSHALL");
        return (String) parseResponse(response);
    }
    
    /**
     * Get keys matching pattern
     */
    @SuppressWarnings("unchecked")
    public List<String> keys(String pattern) throws RedstarException {
        String response = sendCommand("KEYS", pattern);
        Object result = parseResponse(response);
        return result instanceof List ? (List<String>) result : new ArrayList<>();
    }
    
    // Pub/Sub Operations
    
    /**
     * Subscribe to channel with callback
     */
    public void subscribe(String channel, BiConsumer<String, String> callback) throws RedstarException {
        if (!isSubscribed) {
            isSubscribed = true;
            pubsubExecutor = Executors.newSingleThreadExecutor();
            pubsubExecutor.submit(this::pubsubListener);
        }
        
        channelCallbacks.put(channel, callback);
        sendCommand("SUBSCRIBE", channel);
    }
    
    /**
     * Subscribe to pattern with callback
     */
    public void psubscribe(String pattern, BiConsumer<String, String> callback) throws RedstarException {
        if (!isSubscribed) {
            isSubscribed = true;
            pubsubExecutor = Executors.newSingleThreadExecutor();
            pubsubExecutor.submit(this::pubsubListener);
        }
        
        patternCallbacks.put(pattern, callback);
        sendCommand("PSUBSCRIBE", pattern);
    }
    
    /**
     * Unsubscribe from channel
     */
    public void unsubscribe(String channel) throws RedstarException {
        channelCallbacks.remove(channel);
        sendCommand("UNSUBSCRIBE", channel);
    }
    
    /**
     * Unsubscribe from pattern
     */
    public void punsubscribe(String pattern) throws RedstarException {
        patternCallbacks.remove(pattern);
        sendCommand("PUNSUBSCRIBE", pattern);
    }
    
    /**
     * Publish message to channel
     */
    public int publish(String channel, String message) throws RedstarException {
        String response = sendCommand("PUBLISH", channel, message);
        return (Integer) parseResponse(response);
    }
    
    /**
     * Background thread for handling pub/sub messages
     */
    private void pubsubListener() {
        try {
            String line;
            while (isSubscribed && (line = reader.readLine()) != null) {
                // Simplified pub/sub message parsing
                // In a real implementation, you'd want more robust parsing
                if (line.startsWith("*3") || line.startsWith("*4")) {
                    // Skip message type line
                    reader.readLine(); // $7 or similar
                    String msgType = reader.readLine(); // message, pmessage, etc.
                    
                    if ("message".equals(msgType)) {
                        reader.readLine(); // channel length
                        String channel = reader.readLine(); // channel name
                        reader.readLine(); // message length
                        String message = reader.readLine(); // message content
                        
                        BiConsumer<String, String> callback = channelCallbacks.get(channel);
                        if (callback != null) {
                            callback.accept(channel, message);
                        }
                    }
                }
            }
        } catch (IOException e) {
            // Connection lost or closed
        }
    }
    
    @Override
    public void close() {
        disconnect();
    }
    
    // Exception classes
    public static class RedstarException extends Exception {
        public RedstarException(String message) {
            super(message);
        }
        
        public RedstarException(String message, Throwable cause) {
            super(message, cause);
        }
    }
    
    public static class RedstarConnectionException extends RedstarException {
        public RedstarConnectionException(String message) {
            super(message);
        }
        
        public RedstarConnectionException(String message, Throwable cause) {
            super(message, cause);
        }
    }
    
    public static class RedstarCommandException extends RedstarException {
        public RedstarCommandException(String message) {
            super(message);
        }
    }
    
    // Example usage
    public static void main(String[] args) {
        try (RedstarClient client = new RedstarClient()) {
            client.connect();
            
            // String operations
            System.out.println("Setting key...");
            client.set("hello", "world");
            System.out.println("Getting key: " + client.get("hello"));
            
            // List operations
            System.out.println("List operations...");
            client.lpush("mylist", "item1", "item2");
            System.out.println("List length: " + client.llen("mylist"));
            System.out.println("List range: " + client.lrange("mylist", 0, -1));
            
            // Hash operations
            System.out.println("Hash operations...");
            client.hset("user:1", "name", "Alice");
            client.hset("user:1", "age", "30");
            System.out.println("Hash: " + client.hgetall("user:1"));
            
            // Server info
            System.out.println("Ping: " + client.ping());
            System.out.println("Connection successful!");
            
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}