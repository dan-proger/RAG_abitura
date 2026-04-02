import redis
import json

r = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

print("Redis connected:", r.ping())

keys = r.keys("chunk:*")

print(f"\nНайдено ключей: {len(keys)}\n")

for key in keys:
    raw = r.get(key)
    data = json.loads(raw)

    print(f"KEY: {key}")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("-" * 40)