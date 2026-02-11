import time
import threading

class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.lock = threading.Lock()
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill_time = time.monotonic()

    def allow_request(self) -> bool:
        with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_refill_time()

            refill_amount = elapsed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + refill_amount)

            self.last_refill_time = now

            if self.tokens >= 1:
                self.tokens -= 1
                return True
            
            return False