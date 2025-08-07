
import time

class RedStarValue:
    def __init__(self, value, value_type, expiry_time = None):
        self.value = value
        self.type = value_type
        self.expiry_time = expiry_time

    def is_expired(self):
        if self.expiry_time is None:
            return False
        return time.time() > self.expiry_time