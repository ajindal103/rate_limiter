from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from rate_limiter import InMemoryRateLimiter

app = FastAPI()

rate_limiter = InMemoryRateLimiter(capacity=10, refill_rate=1.0)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    key = f"ip:{client_ip}"

    if not rate_limiter.allow(key):
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate Limit Exceeded!"
            }
        )
    
    response = await call_next(request)
    return response
    