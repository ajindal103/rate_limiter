from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from redis.asyncio import redis

from app.config import settings
from app.services.plan_service import plan_service
from app.rate_limiter.limiter import RedisTokenBucketLimiter

app = FastAPI()

API_KEYS = {
    "free-key": "free",
    "pro-key": "pro"
}

redis_client = redis.Redis.from_url(settings.redis_url)
rate_limiter = RedisTokenBucketLimiter(redis_client) 

@app.on_event("startup")
async def startup():
    await rate_limiter.load_script(
        "app/rate_limiter/lua/token_bucket.lua"
    )


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    api_key = request.headers.get("X-API-Key")
    
    if not api_key or api_key not in API_KEYS:
        return JSONResponse(
            status_code=401,
            content={
                "detail": "Invalid API Key"
            }
        )

    plan_name = API_KEYS[api_key]
    plan = plan_service.get(plan_name)

    key = f"rate_limit:{api_key}"

    allowed, remaining, retry_after = await rate_limiter.allow(
        key, 
        plan["capacity"],
        plan["refill_rate"]
    )

    if not allowed:
        return JSONResponse(
            status_code=429,
            headers={
                "Retry-After": str(int(retry_after)),
                "X-RateLimit-Remaining": str(int(remaining)),
                "X-RateLimit-Limit": str(plan["capacity"]),
            },
            content={
                "detail": "Rate Limit Exceeded!"
            }
        )

    response = await call_next(request)

    response.headers["X-RateLimit-Remaining"] = str(int(remaining))
    response.headers["X-RateLimit-Limit"] = str(plan["capacity"])
    
    return response