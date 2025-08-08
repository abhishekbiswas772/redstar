from core_datastructures.dynamic_array import DArray


class RedstarPubSubCommands:
    """
    Pub/Sub command implementations for Redstar
    These commands handle subscription and publishing functionality
    """
    
    def __init__(self, pubsub_manager):
        self.pubsub_manager = pubsub_manager
    
    def cmd_subscribe(self, args, client_handler):
        """SUBSCRIBE channel [channel ...]"""
        if len(args) == 0:
            return Exception("ERR wrong number of arguments for 'subscribe' command")
        
        channels = DArray()
        for i in range(len(args)):
            channels.append(args[i])
        
        # Subscribe to channels
        total_subscriptions = self.pubsub_manager.subscribe(client_handler, channels)
        
        # Build response array - Redis returns one response per channel
        responses = DArray()
        for i in range(len(channels)):
            channel = channels[i]
            response = DArray()
            response.append("subscribe")
            response.append(channel)
            response.append(total_subscriptions - (len(channels) - 1 - i))
            responses.append(response)
        
        return responses
    
    def cmd_unsubscribe(self, args, client_handler):
        """UNSUBSCRIBE [channel [channel ...]]"""
        channels = None
        if len(args) > 0:
            channels = DArray()
            for i in range(len(args)):
                channels.append(args[i])
        
        # Unsubscribe from channels
        unsubscribe_results = self.pubsub_manager.unsubscribe(client_handler, channels)
        
        # Build response array
        responses = DArray()
        for i in range(len(unsubscribe_results)):
            channel, remaining_count = unsubscribe_results[i]
            response = DArray()
            response.append("unsubscribe")
            response.append(channel)
            response.append(remaining_count)
            responses.append(response)
        
        # If no channels specified and no subscriptions, return default response
        if len(responses) == 0:
            response = DArray()
            response.append("unsubscribe")
            response.append(None)
            response.append(0)
            responses.append(response)
        
        return responses
    
    def cmd_psubscribe(self, args, client_handler):
        """PSUBSCRIBE pattern [pattern ...]"""
        if len(args) == 0:
            return Exception("ERR wrong number of arguments for 'psubscribe' command")
        
        patterns = DArray()
        for i in range(len(args)):
            patterns.append(args[i])
        
        # Subscribe to patterns
        total_subscriptions = self.pubsub_manager.psubscribe(client_handler, patterns)
        
        # Build response array - Redis returns one response per pattern
        responses = DArray()
        for i in range(len(patterns)):
            pattern = patterns[i]
            response = DArray()
            response.append("psubscribe")
            response.append(pattern)
            response.append(total_subscriptions - (len(patterns) - 1 - i))
            responses.append(response)
        
        return responses
    
    def cmd_punsubscribe(self, args, client_handler):
        """PUNSUBSCRIBE [pattern [pattern ...]]"""
        patterns = None
        if len(args) > 0:
            patterns = DArray()
            for i in range(len(args)):
                patterns.append(args[i])
        
        # Unsubscribe from patterns
        unsubscribe_results = self.pubsub_manager.punsubscribe(client_handler, patterns)
        
        # Build response array
        responses = DArray()
        for i in range(len(unsubscribe_results)):
            pattern, remaining_count = unsubscribe_results[i]
            response = DArray()
            response.append("punsubscribe")
            response.append(pattern)
            response.append(remaining_count)
            responses.append(response)
        
        # If no patterns specified and no subscriptions, return default response
        if len(responses) == 0:
            response = DArray()
            response.append("punsubscribe")
            response.append(None)
            response.append(0)
            responses.append(response)
        
        return responses
    
    def cmd_publish(self, args, client_handler):
        """PUBLISH channel message"""
        if len(args) != 2:
            return Exception("ERR wrong number of arguments for 'publish' command")
        
        channel = args[0]
        message = args[1]
        
        # Publish message and return number of recipients
        recipient_count = self.pubsub_manager.publish(channel, message)
        return recipient_count
    
    def cmd_pubsub(self, args, client_handler):
        """PUBSUB subcommand [argument [argument ...]]"""
        if len(args) == 0:
            return Exception("ERR wrong number of arguments for 'pubsub' command")
        
        subcommand = args[0].upper()
        
        if subcommand == "CHANNELS":
            # PUBSUB CHANNELS [pattern]
            pattern = None
            if len(args) > 1:
                pattern = args[1]
            
            return self.pubsub_manager.get_channels(pattern)
        
        elif subcommand == "NUMSUB":
            # PUBSUB NUMSUB [channel [channel ...]]
            result = DArray()
            
            if len(args) == 1:
                # No channels specified, return empty array
                return result
            
            for i in range(1, len(args)):
                channel = args[i]
                count = self.pubsub_manager.get_channel_subscribers_count(channel)
                result.append(channel)
                result.append(count)
            
            return result
        
        elif subcommand == "NUMPAT":
            # PUBSUB NUMPAT
            if len(args) != 1:
                return Exception("ERR wrong number of arguments for 'pubsub numpat' command")
            
            return self.pubsub_manager.get_pattern_count()
        
        else:
            return Exception(f"ERR unknown subcommand or wrong number of arguments for 'pubsub {subcommand}'")
    
    def create_message_response(self, channel, message, pattern=None):
        """
        Create a message response for pub/sub clients
        Used when delivering published messages to subscribers
        """
        if pattern is None:
            # Regular channel message
            response = DArray()
            response.append("message")
            response.append(channel)
            response.append(message)
            return response
        else:
            # Pattern-matched message
            response = DArray()
            response.append("pmessage")
            response.append(pattern)
            response.append(channel)
            response.append(message)
            return response