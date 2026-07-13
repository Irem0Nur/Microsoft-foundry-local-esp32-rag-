import json
import math
import sqlite3

from colorama import Fore, Style, init as colorama_init
from foundry_local_sdk import Configuration, FoundryLocalManager

colorama_init(autoreset=True)

DB_PATH = "rag.db"
TOP_K = 2

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions about an ESP32 development board "
    "using only the provided context. Always answer in Turkish, in plain prose (no code "
    "blocks unless the context itself contains code). Always mention which source(s) you "
    "used, e.g. '(Kaynak: X)'. If the context does not contain the answer, say in Turkish "
    "that you don't know instead of guessing."
)

BANNER = f"""{Fore.CYAN}{Style.BRIGHT}
╔══════════════════════════════════════════╗
║        ESP32 Asistanı — Local RAG         ║
║      (Microsoft Foundry Local ile)        ║
╚══════════════════════════════════════════╝{Style.RESET_ALL}
Komutlar: {Fore.YELLOW}quit{Style.RESET_ALL} çık | {Fore.YELLOW}history{Style.RESET_ALL} geçmişi göster | {Fore.YELLOW}help{Style.RESET_ALL} yardım
"""


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


def print_history(history):
    if not history:
        print(f"{Fore.YELLOW}Henüz soru sormadın.{Style.RESET_ALL}\n")
        return
    print(f"\n{Fore.CYAN}{Style.BRIGHT}--- Geçmiş ---{Style.RESET_ALL}")
    for i, (q, a) in enumerate(history, 1):
        print(f"{Fore.GREEN}{i}. Soru:{Style.RESET_ALL} {q}")
        print(f"{Fore.MAGENTA}   Cevap:{Style.RESET_ALL} {a}\n")


def print_help():
    print(f"""
{Fore.CYAN}Kullanılabilir komutlar:{Style.RESET_ALL}
  {Fore.YELLOW}quit{Style.RESET_ALL}     - Programdan çık
  {Fore.YELLOW}history{Style.RESET_ALL}  - Bu oturumdaki tüm soru-cevapları göster
  {Fore.YELLOW}help{Style.RESET_ALL}     - Bu yardım mesajını göster
Herhangi bir ESP32 sorusu yazıp Enter'a basman yeterli.
""")


def main():
    config = Configuration(app_name="foundry_local_rag")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    print(f"{Fore.YELLOW}Modeller yükleniyor...{Style.RESET_ALL}")

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
    history = []

    print(BANNER)

    while True:
        query = input(f"{Fore.GREEN}{Style.BRIGHT}Soru: {Style.RESET_ALL}").strip()

        if not query:
            continue
        if query.lower() == "quit":
            break
        if query.lower() == "history":
            print_history(history)
            continue
        if query.lower() == "help":
            print_help()
            continue

        query_response = embedding_client.generate_embeddings([query])
        query_embedding = query_response.data[0].embedding

        top_chunks = get_top_chunks(conn, query_embedding)

        # Kullanılan kaynakları önce göster
        source_list = ", ".join(source for _, source, _ in top_chunks)
        print(f"{Fore.BLUE}  ↳ Kullanılan kaynaklar: {source_list}{Style.RESET_ALL}")

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
        answer = chat_response.choices[0].message.content
        print(f"{Fore.MAGENTA}{Style.BRIGHT}Cevap:{Style.RESET_ALL} {answer}\n")

        history.append((query, answer))

    conn.close()
    embedding_model.unload()
    chat_model.unload()
    print(f"{Fore.CYAN}Görüşürüz!{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
