SCRIPT = """
local key = KEYS[1]

local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

-- Fetch existing data
local data = redis.call("HMGET", key, "tokens", "last_refill")
local tokens = tonumber(data[1])
local last_refill = tonumber(data[2])

if tokens == nil then
    tokens = capacity
    last_refill = now
end

-- Calculate refill
local elapsed = now - last_refill
local refill = elapsed * refill_rate
tokens = math.min(capacity, tokens + refill)

local allowed = 0

if tokens >= requested then
    tokens = tokens - requested
    allowed = 1
end

-- Save updated state
redis.call("HMSET", key,
    "tokens", tokens,
    "last_refill", now
)

-- Set TTL (2x window approximation)
redis.call("EXPIRE", key, math.ceil(capacity / refill_rate) * 2)

return allowed
"""