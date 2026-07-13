import json
import sqlite3

from foundry_local_sdk import Configuration, FoundryLocalManager

from knowledge_base import DOCUMENTS

DB_PATH = "rag.db"


def create_schema(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            text TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
        """
    )
    conn.commit()


def main():
    config = Configuration(app_name="foundry_local_rag")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    embedding_model = manager.catalog.get_model("qwen3-embedding-0.6b")
    embedding_model.download(
        lambda p: print(f"\rEmbedding modeli indiriliyor: {p:.1f}%", end="", flush=True)
    )
    print()
    embedding_model.load()
    embedding_client = embedding_model.get_embedding_client()

    conn = sqlite3.connect(DB_PATH)
    create_schema(conn)

    # Önceki verileri temizle (her ingest çalıştırmasında sıfırdan başla)
    conn.execute("DELETE FROM chunks")

    sources = [d[0] for d in DOCUMENTS]
    texts = [d[1] for d in DOCUMENTS]

    response = embedding_client.generate_embeddings(texts)
    embeddings = [item.embedding for item in response.data]

    for source, text, embedding in zip(sources, texts, embeddings):
        conn.execute(
            "INSERT INTO chunks (source, text, embedding) VALUES (?, ?, ?)",
            (source, text, json.dumps(embedding)),
        )
    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    print(f"{count} chunk '{DB_PATH}' dosyasına kaydedildi.")

    conn.close()
    embedding_model.unload()


if __name__ == "__main__":
    main()
