import redis
import json
import numpy as np
from scipy.spatial.distance import cdist

# импорт твоего Embedder
from assistent_class import Embedder  # <-- замени на имя файла

# -------------------------
# Redis подключение
# -------------------------
r = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

print("Redis:", r.ping())

# -------------------------
# Загружаем чанки из Redis
# -------------------------
keys = r.keys("chunk:*")

chunks = []
for key in keys:
    chunk = json.loads(r.get(key))
    chunks.append(chunk)

print(f"Загружено чанков из Redis: {len(chunks)}")

# -------------------------
# Эмбеддер
# -------------------------
embedder = Embedder()

# -------------------------
# ТЕСТОВЫЙ ВОПРОС
# -------------------------
test_question = "Какие документы нужны для поступления?"

# эмбеддинг вопроса
question_emb = embedder.embedding(test_question)
question_emb = np.array([question_emb])

# -------------------------
# Эмбеддинг чанков
# -------------------------
chunk_embeddings = []
for chunk in chunks:
    emb = embedder.embedding(chunk["content"])  # или "text"
    chunk_embeddings.append(emb)

chunk_embeddings = np.array(chunk_embeddings)

# -------------------------
# Поиск (cosine similarity)
# -------------------------
dist = cdist(question_emb, chunk_embeddings, metric="cosine")
sim = 1 - dist.flatten()

# сортировка
top_k = 3
top_indices = np.argsort(dist.flatten())[:top_k]

# -------------------------
# Вывод результатов
# -------------------------
print("\nВопрос:", test_question)
print("\nТоп ответов:\n")

for i in top_indices:
    print("----")
    print(f"chunk_id: {chunks[i]['id']}")
    print(f"score: {round(sim[i], 3)}")
    print(chunks[i]["content"])