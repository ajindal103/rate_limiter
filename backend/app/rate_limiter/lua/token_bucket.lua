local key = KEYS[1]

local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local requested = tonumber(ARGV[3])

-- Get Redis server time
local redis_time = redis.call("TIME")
local now = tonumber(redis_time[1]) + tonumber(redis_time[2]) / 1000000

-- Fetch bucket
local data = redis.call("HMGET", key, "tokens", "last_refill")
local tokens = tonumber(data[1])
local last_refill = tonumber(data[2])

if tokens == nil then
    tokens = capacity
    last_refill = now
end

-- Refill calculation
local elapsed = now - last_refill
local refill = elapsed * refill_rate
tokens = math.min(capacity, tokens + refill)

local allowed = 0
local retry_after = 0

if tokens >= requested then
    tokens = tokens - requested
    allowed = 1
else
    retry_after = (requested - tokens) / refill_rate
end

-- Save state
redis.call("HMSET", key,
    "tokens", tokens,
    "last_refill", now
)

-- TTL = 2x full refill window
local ttl = math.ceil(capacity / refill_rate) * 2
redis.call("EXPIRE", key, ttl)

return {allowed, tokens, retry_after}
