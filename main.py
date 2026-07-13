import json
import math
import sqlite3

from foundry_local_sdk import Configuration, FoundryLocalManager

DB_PATH = "rag.db"
TOP_K = 2

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions about an ESP32 development board "
    "using only the provided context. Always mention which source(s) you used, e.g. "
    "'(Kaynak: X)'. If the context does not contain the answer, say you don't know instead "
    "of guessing."
)


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)


def get_top_chunks(conn, query_embedding, k=TOP_K):
    """SQLite'taki tüm chunk'ları çekip kosinüs benzerliğine göre en iyi k tanesini döndürür."""
    rows = conn.execute("SELECT source, text, embedding FROM chunks").fetchall()
    scored = []
    for source, text, embedding_json in rows:
        embedding = json.loads(embedding_json)
        score = cosine_similarity(query_embedding, embedding)
        scored.append((score, source, text))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:k]


def main():
    config = Configuration(app_name="foundry_local_rag")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    embedding_model = manager.catalog.get_model("qwen3-embedding-0.6b")
    embedding_model.load()
    embedding_client = embedding_model.get_embedding_client()

    chat_model = manager.catalog.get_model("qwen2.5-0.5b")
    chat_model.download(
        lambda p: print(f"\rChat modeli indiriliyor: {p:.1f}%", end="", flush=True)
    )
    print()
    chat_model.load()
    chat_client = chat_model.get_chat_client()

    conn = sqlite3.connect(DB_PATH)

    print("\nESP32 Asistanı hazır. Çıkmak için 'quit' yaz.\n")

    while True:
        query = input("Soru: ").strip()
        if not query or query.lower() == "quit":
            break

        query_response = embedding_client.generate_embeddings([query])
        query_embedding = query_response.data[0].embedding

        top_chunks = get_top_chunks(conn, query_embedding)
        context_text = "\n\n".join(
            f"[{source}]\n{text}" for _, source, text in top_chunks
        )

        prompt = f"Context:\n{context_text}\n\nQuestion: {query}"

        chat_response = chat_client.complete_chat(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]
        )
        print(f"\nCevap: {chat_response.choices[0].message.content}\n")

    conn.close()
    embedding_model.unload()
    chat_model.unload()
    print("Bitti!")


if __name__ == "__main__":
    main()
