import redis
import json
import os
import time
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel

# ---------------- Redis ----------------
r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

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

# ---------------- Model ----------------
MODEL_NAME = "intfloat/multilingual-e5-large"

print("Loading model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
model.eval()

print(f"Model loaded on {device}")


def average_pool(last_hidden_state, attention_mask):
    last_hidden = last_hidden_state.masked_fill(
        ~attention_mask[..., None].bool(), 0.0
    )
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]


def embed_text(text: str):
    text = f"passage: {text}"

    batch = tokenizer(
        [text],
        max_length=512,
        padding=True,
        truncation=True,
        return_tensors="pt"
    )

    batch = {k: v.to(device) for k, v in batch.items()}

    with torch.no_grad():
        outputs = model(**batch)

    embeddings = average_pool(
        outputs.last_hidden_state,
        batch["attention_mask"]
    )

    embeddings = F.normalize(embeddings, p=2, dim=1)

    return embeddings[0].cpu().tolist()


# ---------------- Files ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHUNKS_DIR = os.path.join(BASE_DIR, "..", "chunks")

FILES = [f for f in os.listdir(CHUNKS_DIR) if f.endswith(".json")]

total_loaded = 0

# ---------------- Main ----------------
for filename in FILES:
    file_path = os.path.join(CHUNKS_DIR, filename)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
    except Exception as e:
        print(f"{filename}: ошибка чтения → {e}")
        continue

    if not chunks:
        print(f"{filename}: пустой файл")
        continue

    pipe = r.pipeline()
    loaded = 0

    for chunk in chunks:
        key = f"{filename}:chunk:{chunk['id']}"

        if r.exists(key):
            continue

        try:
            # если embedding отсутствует — считаем
            if "embedding" not in chunk or not chunk["embedding"]:
                chunk["embedding"] = embed_text(chunk["content"])

            pipe.set(key, json.dumps(chunk, ensure_ascii=False))
            loaded += 1

        except Exception as e:
            print(f"{filename} / {chunk['id']}: ошибка → {e}")

    pipe.execute()

    print(f"{filename}: добавлено {loaded} новых чанков")
    total_loaded += loaded

print(f"Всего добавлено: {total_loaded}")