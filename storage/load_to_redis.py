import redis
import json
import os
import time

r = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

#  ожидание Redis
for i in range(10):
    try:
        if r.ping():
            print("Redis connected")
            break
    except Exception:
        print("Waiting for Redis...")
        time.sleep(1)
else:
    raise Exception("Redis not available")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "..", "chunks", "doc_id_chunks.json")

with open(FILE_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

#  проверка ДО загрузки
if r.exists(f"chunk:{chunks[0]['id']}"):
    print("Данные уже загружены")
    exit()

# загрузка
for chunk in chunks:
    key = f"chunk:{chunk['id']}"
    r.set(key, json.dumps(chunk))

print(f"Загружено чанков: {len(chunks)}")
