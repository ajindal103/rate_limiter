from fastapi import FastAPI, Request
from fastapi.responses import Response
import redis.asyncio as redis
from redis_rate_limiter import RedisTokenBucketRateLimiter

app = FastAPI()

redis_client = redis.Redis(host="localhost", port=6379)

rate_limiter = RedisTokenBucketRateLimiter(
    redis_client,
    capacity=10,
    refill_rate=1.0
)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    key = f"ip:{client_ip}"

    allowed = await rate_limiter.allow(key)

    if not allowed:
        return Response(
            status_code=429,
            content={
                "detail": "Rate Limit Exceeded!"
            }
        )

    response = await call_next(request)
    return response