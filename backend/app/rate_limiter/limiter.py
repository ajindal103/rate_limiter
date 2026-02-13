
class RedisTokenBucketLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.script = None

    async def load_script(self, path: str):
        with open(path, "r") as f:
            lua_code = f.read()

        self.script = await self.redis.register_script(lua_code)

    async def allow(self, key, capacity: int, refill_rate: float, tokens=1):
        result = await self.script(
            keys=[key],
            args=[capacity, refill_rate, tokens],
        )

        allowed = bool(result[0])
        remaining = float(result[1])
        retry_after = float(result[2])

        return allowed, remaining, retry_after