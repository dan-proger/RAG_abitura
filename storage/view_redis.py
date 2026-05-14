import redis
import json

r = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

print("Redis connected:", r.ping())

# используем SCAN вместо KEYS
pattern = "*:chunk:*"
count = 0

for key in r.scan_iter(match=pattern):
    raw = r.get(key)
    if not raw:
        continue

    try:
        data = json.loads(raw)
    except Exception as e:
        print(f"Ошибка JSON в ключе {key}: {e}")
        continue

    print(f"KEY: {key}")
    # Ограничиваем вывод embedding
    if 'embedding' in data and isinstance(data['embedding'], list):
        emb_preview = data['embedding'][:5] + ["..."] if len(data['embedding']) > 5 else data['embedding']
        data_copy = data.copy()
        data_copy['embedding'] = f"{emb_preview} (длина: {len(data['embedding'])})"
        print(json.dumps(data_copy, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    print("-" * 40)

    count += 1

print(f"\nВсего найдено: {count}")