import threading
from token_bucket import TokenBucket

class InMemoryRateLimiter:
    def __init__(self, capacity: int, refill_rate: float):
        self.global_lock = threading.Lock()
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets = {}

    def _get_bucket(self, key: str) -> TokenBucket:
        with self.global_lock:
            if key not in self.buckets:
                self.buckets[key] = TokenBucket(
                    self.capacity,
                    self.refill_rate
                )
            return self.buckets[key]
        
    def allow(self, key: str) -> bool:
        bucket = self._get_bucket(key)
        return bucket.allow_request()       