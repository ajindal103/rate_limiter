import time
from lua_script import SCRIPT

class RedisTokenBucketRateLimiter:
    def __init__(self, redis_client, capacity: int, refill_rate: float):
        self.redis = redis_client
        self.capacity = capacity
        self.refill_rate = refill_rate

        self.script = self.redis.register_script(SCRIPT)

    async def allow(self, key: str, tokens: int = 1)-> bool:
        now = time.monotonic()

        allowed = await self.script(
            keys=[key],
            args=[
                self.capacity,
                self.refill_rate,
                now, 
                tokens
            ]
        )

        return bool(allowed)