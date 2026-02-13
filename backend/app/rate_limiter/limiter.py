
class RedisTokenBucketLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.script = None

    async def load_script(self, lua_code: str):
        self.script = await self.redis.register_script(lua_code)

    async def allow(self, key, capacity: int, refill_rate: float):
        return bool(
            await self.script(
                keys = [key],
                args = [capacity, refill_rate]
            )
        )