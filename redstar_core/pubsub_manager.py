import threading
import fnmatch
from core_datastructures.hash_table import HashTable
from core_datastructures.hashset import HashSet
from core_datastructures.dynamic_array import DArray


class RedstarPubSubManager:
    """
    Manages publish/subscribe functionality for Redstar server
    Handles channel subscriptions, pattern subscriptions, and message publishing
    """
    
    def __init__(self):
        self.lock = threading.RLock()
        
        # Map: channel_name -> set of client_handlers
        self.channel_subscribers = HashTable()
        
        # Map: pattern -> set of client_handlers  
        self.pattern_subscribers = HashTable()
        
        # Map: client_handler -> set of subscribed channels
        self.client_channels = HashTable()
        
        # Map: client_handler -> set of subscribed patterns
        self.client_patterns = HashTable()
    
    def subscribe(self, client_handler, channels):
        """
        Subscribe a client to one or more channels
        Returns the number of channels the client is now subscribed to
        """
        with self.lock:
            if client_handler not in self.client_channels:
                self.client_channels[client_handler] = HashSet()
            
            client_channel_set = self.client_channels[client_handler]
            
            for channel in channels:
                # Add client to channel subscribers
                if channel not in self.channel_subscribers:
                    self.channel_subscribers[channel] = HashSet()
                
                self.channel_subscribers[channel].add(client_handler)
                client_channel_set.add(channel)
            
            # Return total subscription count for this client
            pattern_count = 0
            if client_handler in self.client_patterns:
                pattern_count = self.client_patterns[client_handler].size()
                
            return client_channel_set.size() + pattern_count
    
    def unsubscribe(self, client_handler, channels=None):
        """
        Unsubscribe a client from channels
        If channels is None, unsubscribe from all channels
        Returns array of [channel, remaining_subscription_count] pairs
        """
        with self.lock:
            result = DArray()
            
            if client_handler not in self.client_channels:
                # Not subscribed to any channels
                if channels is None:
                    return result
                
                for channel in channels:
                    result.append([channel, 0])
                return result
            
            client_channel_set = self.client_channels[client_handler]
            
            # If no specific channels provided, unsubscribe from all
            if channels is None:
                channels_to_unsub = DArray()
                for channel in client_channel_set:
                    channels_to_unsub.append(channel)
                channels = channels_to_unsub
            
            for channel in channels:
                if client_channel_set.contains(channel):
                    # Remove from client's channel set
                    client_channel_set.remove(channel)
                    
                    # Remove client from channel's subscriber set
                    if channel in self.channel_subscribers:
                        self.channel_subscribers[channel].remove(client_handler)
                        
                        # Clean up empty channel subscriber sets
                        if self.channel_subscribers[channel].size() == 0:
                            del self.channel_subscribers[channel]
                
                # Calculate remaining subscription count
                pattern_count = 0
                if client_handler in self.client_patterns:
                    pattern_count = self.client_patterns[client_handler].size()
                
                remaining_count = client_channel_set.size() + pattern_count
                result.append([channel, remaining_count])
            
            # Clean up empty client channel sets
            if client_channel_set.size() == 0:
                del self.client_channels[client_handler]
            
            return result
    
    def psubscribe(self, client_handler, patterns):
        """
        Subscribe a client to one or more channel patterns
        Returns the number of patterns the client is now subscribed to
        """
        with self.lock:
            if client_handler not in self.client_patterns:
                self.client_patterns[client_handler] = HashSet()
            
            client_pattern_set = self.client_patterns[client_handler]
            
            for pattern in patterns:
                # Add client to pattern subscribers
                if pattern not in self.pattern_subscribers:
                    self.pattern_subscribers[pattern] = HashSet()
                
                self.pattern_subscribers[pattern].add(client_handler)
                client_pattern_set.add(pattern)
            
            # Return total subscription count for this client
            channel_count = 0
            if client_handler in self.client_channels:
                channel_count = self.client_channels[client_handler].size()
                
            return client_pattern_set.size() + channel_count
    
    def punsubscribe(self, client_handler, patterns=None):
        """
        Unsubscribe a client from patterns
        If patterns is None, unsubscribe from all patterns
        Returns array of [pattern, remaining_subscription_count] pairs
        """
        with self.lock:
            result = DArray()
            
            if client_handler not in self.client_patterns:
                # Not subscribed to any patterns
                if patterns is None:
                    return result
                
                for pattern in patterns:
                    result.append([pattern, 0])
                return result
            
            client_pattern_set = self.client_patterns[client_handler]
            
            # If no specific patterns provided, unsubscribe from all
            if patterns is None:
                patterns_to_unsub = DArray()
                for pattern in client_pattern_set:
                    patterns_to_unsub.append(pattern)
                patterns = patterns_to_unsub
            
            for pattern in patterns:
                if client_pattern_set.contains(pattern):
                    # Remove from client's pattern set
                    client_pattern_set.remove(pattern)
                    
                    # Remove client from pattern's subscriber set
                    if pattern in self.pattern_subscribers:
                        self.pattern_subscribers[pattern].remove(client_handler)
                        
                        # Clean up empty pattern subscriber sets
                        if self.pattern_subscribers[pattern].size() == 0:
                            del self.pattern_subscribers[pattern]
                
                # Calculate remaining subscription count
                channel_count = 0
                if client_handler in self.client_channels:
                    channel_count = self.client_channels[client_handler].size()
                
                remaining_count = client_pattern_set.size() + channel_count
                result.append([pattern, remaining_count])
            
            # Clean up empty client pattern sets
            if client_pattern_set.size() == 0:
                del self.client_patterns[client_handler]
            
            return result
    
    def publish(self, channel, message):
        """
        Publish a message to a channel
        Returns the number of clients that received the message
        """
        with self.lock:
            recipients = HashSet()
            
            # Find direct channel subscribers
            if channel in self.channel_subscribers:
                for client_handler in self.channel_subscribers[channel]:
                    recipients.add(client_handler)
            
            # Find pattern subscribers that match this channel
            for pattern in self.pattern_subscribers:
                if fnmatch.fnmatch(channel, pattern):
                    for client_handler in self.pattern_subscribers[pattern]:
                        recipients.add(client_handler)
            
            # Send message to all recipients
            recipient_count = 0
            for client_handler in recipients:
                try:
                    if hasattr(client_handler, 'send_pubsub_message'):
                        client_handler.send_pubsub_message(channel, message)
                        recipient_count += 1
                except Exception as e:
                    # Client might be disconnected, remove it
                    self._cleanup_client(client_handler)
            
            return recipient_count
    
    def get_subscription_count(self, client_handler):
        """Get total number of subscriptions for a client"""
        with self.lock:
            channel_count = 0
            pattern_count = 0
            
            if client_handler in self.client_channels:
                channel_count = self.client_channels[client_handler].size()
            
            if client_handler in self.client_patterns:
                pattern_count = self.client_patterns[client_handler].size()
            
            return channel_count + pattern_count
    
    def is_subscribed(self, client_handler):
        """Check if client has any subscriptions"""
        return self.get_subscription_count(client_handler) > 0
    
    def get_channels(self, pattern=None):
        """
        Get list of active channels, optionally matching a pattern
        Used by PUBSUB CHANNELS command
        """
        with self.lock:
            result = DArray()
            
            for channel in self.channel_subscribers:
                if self.channel_subscribers[channel].size() > 0:
                    if pattern is None or fnmatch.fnmatch(channel, pattern):
                        result.append(channel)
            
            return result
    
    def get_channel_subscribers_count(self, channel):
        """
        Get number of subscribers for a specific channel
        Used by PUBSUB NUMSUB command
        """
        with self.lock:
            if channel in self.channel_subscribers:
                return self.channel_subscribers[channel].size()
            return 0
    
    def get_pattern_count(self):
        """
        Get number of pattern subscriptions
        Used by PUBSUB NUMPAT command
        """
        with self.lock:
            total_patterns = 0
            for pattern in self.pattern_subscribers:
                if self.pattern_subscribers[pattern].size() > 0:
                    total_patterns += 1
            return total_patterns
    
    def cleanup_client(self, client_handler):
        """Clean up all subscriptions for a disconnected client"""
        with self.lock:
            self._cleanup_client(client_handler)
    
    def _cleanup_client(self, client_handler):
        """Internal method to clean up client subscriptions"""
        # Unsubscribe from all channels
        if client_handler in self.client_channels:
            self.unsubscribe(client_handler, None)
        
        # Unsubscribe from all patterns
        if client_handler in self.client_patterns:
            self.punsubscribe(client_handler, None)