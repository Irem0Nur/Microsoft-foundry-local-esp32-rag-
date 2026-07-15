import json
import sqlite3
import time

from foundry_local_sdk import Configuration, FoundryLocalManager

from main import DB_PATH, FALLBACK_ANSWER, SIMILARITY_THRESHOLD, SYSTEM_PROMPT, get_top_chunks
from test_cases import TEST_CASES

# Model "bilmiyorum" dediğinde cevapta muhtemelen geçecek ifadeler (TR + EN)
UNKNOWN_MARKERS = [
    "bilmiyorum",
    "bilinmeyen",
    "bilgim yok",
    "bilgi yok",
    "bilgi bulunmamaktadır",
    "emin değilim",
    "bu bilgi verilen",
    "context içinde",
    "verilen bilgide",
    "yer almamaktadır",
    "belirtilmemiş",
    "i don't know",
    "i do not know",
    "not mentioned",
    "no information",
]


def looks_like_unknown(answer: str) -> bool:
    lowered = answer.lower()
    return any(marker in lowered for marker in UNKNOWN_MARKERS)


def main():
    config = Configuration(app_name="foundry_local_rag")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    embedding_model = manager.catalog.get_model("qwen3-embedding-0.6b")
    embedding_model.download()
    embedding_model.load()
    embedding_client = embedding_model.get_embedding_client()

    chat_model = manager.catalog.get_model("qwen2.5-1.5b")
    chat_model.download(
        lambda p: print(f"\rChat modeli indiriliyor: {p:.1f}%", end="", flush=True)
    )
    print()
    chat_model.load()
    chat_client = chat_model.get_chat_client()
    chat_client.settings.temperature = 0.3
    chat_client.settings.max_tokens = 250

    conn = sqlite3.connect(DB_PATH)

    results = []
    print(f"\n{len(TEST_CASES)} test senaryosu çalıştırılıyor...\n")

    for i, case in enumerate(TEST_CASES, 1):
        query = case["query"]
        expected_answerable = case["answerable"]

        start = time.time()

        query_response = embedding_client.generate_embeddings([query])
        query_embedding = query_response.data[0].embedding
        top_chunks = get_top_chunks(conn, query_embedding)
        sources = [source for _, source, _ in top_chunks]
        top_score = top_chunks[0][0] if top_chunks else 0.0

        context_text = "\n\n".join(f"[{s}]\n{t}" for _, s, t in top_chunks)
        prompt = f"Context:\n{context_text}\n\nQuestion: {query}"

        if top_score < SIMILARITY_THRESHOLD:
            answer = FALLBACK_ANSWER
            used_fallback = True
        else:
            used_fallback = False
            chat_response = chat_client.complete_chat(
                [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ]
            )
            answer = chat_response.choices[0].message.content
        elapsed = time.time() - start

        said_unknown = used_fallback or looks_like_unknown(answer)
        # Basit otomatik bayrak: beklenen davranışla model davranışı örtüşüyor mu?
        # (Nihai doğruluk değerlendirmesi hâlâ elle yapılmalı — bu sadece bir ipucu.)
        flag_ok = (not expected_answerable and said_unknown) or (
            expected_answerable and not said_unknown
        )

        results.append(
            {
                "query": query,
                "expected_answerable": expected_answerable,
                "sources": sources,
                "top_score": round(top_score, 3),
                "answer": answer,
                "elapsed_sec": round(elapsed, 2),
                "said_unknown": said_unknown,
                "auto_flag_ok": flag_ok,
            }
        )

        status = "✅" if flag_ok else "⚠️"
        print(f"[{i}/{len(TEST_CASES)}] {status} score={top_score:.3f} ({elapsed:.1f}s) {query}")

    conn.close()
    embedding_model.unload()
    chat_model.unload()

    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    avg_time = sum(r["elapsed_sec"] for r in results) / len(results)
    flagged_ok = sum(1 for r in results if r["auto_flag_ok"])

    print(f"\nOrtalama yanıt süresi: {avg_time:.2f}s")
    print(f"Otomatik bayrak uyumu: {flagged_ok}/{len(results)}")
    print("Detaylar 'test_results.json' dosyasına kaydedildi.")
    print("NOT: '⚠️' işaretli satırları elle incele — otomatik bayrak sadece bir ipucudur.")


if __name__ == "__main__":
    main()
