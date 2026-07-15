# ESP32 Asistanı — Local RAG with Microsoft Foundry Local

Microsoft Foundry Local kullanarak **tamamen çevrimdışı** çalışan, ESP32 geliştirme
kartı hakkındaki soruları yanıtlayan bir RAG (Retrieval-Augmented Generation)
asistanı. Hiçbir bulut servisi, API anahtarı veya internet bağlantısı gerekmez —
embedding ve dil modeli çıkarımının tamamı cihaz üzerinde çalışır.

Bu proje, Microsoft'un ["Building Your First Local RAG Application with Foundry
Local"](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/building-your-first-local-rag-application-with-foundry-local/4501968)
blog yazısından ilham alan bir yaz stajı/proje ödevi kapsamında geliştirilmiştir.

## Problem Tanımı

Genel amaçlı LLM'ler, özel/dar bir domain hakkında (örn. belirli bir donanım
kartının SSS'i) sorulan sorularda ya yanlış cevap uydurur ya da hiç bilgisi
olmadığını söyler. RAG, modelin cevabını **kendi belge kümenizden alınan
gerçek bilgiyle** desteklediği için hem doğruluğu artırır hem de kaynak
gösterebilir hale getirir — üstelik bunu bulut bağlantısı olmadan yapabilir.

## Mimari

```
Kullanıcı Sorusu
      │
      ▼
[Embedding Modeli] ──► sorunun vektörü
      │
      ▼
[SQLite: rag.db] ──► kosinüs benzerliğiyle en alakalı chunk'lar (get_top_chunks)
      │
      ▼
En iyi skor eşiğin (0.45) altında mı?
   ├── Evet → doğrudan "bilgi bulamadım" (LLM çağrılmaz)
   └── Hayır → context + soru → [Chat Modeli] ──► kaynak belirtilmiş cevap
```

| Dosya | Görev |
|---|---|
| `knowledge_base.py` | Kaynak dökümanlar (ESP32 kurulum, ESP-NOW, güç yönetimi, vb.) |
| `ingest.py` | Dökümanları embed edip `rag.db` (SQLite) dosyasına kaydeder |
| `main.py` | Sorguyu embed eder, retrieval yapar, eşik kontrolü uygular, chat modelinden cevap alır |
| `test_cases.py` / `run_tests.py` | Otomatik test seti ve raporlama |
| `TEST_REPORT.md` | Test sonuçları, bulgular, bilinen sınırlamalar |

**Kullanılan modeller (Foundry Local kataloğundan):**
- Embedding: `qwen3-embedding-0.6b`
- Chat: `qwen2.5-1.5b` (`temperature=0.3`, `max_tokens=250`)

## Tasarım Kararları

- **SQLite tercih edildi** (harici vektör DB yerine) — tek dosya, sunucusuz,
  küçük ölçekli bir bilgi tabanı için yeterli ve kurulum gerektirmiyor.
- **Brute-force kosinüs benzerliği** kullanıldı — 8 chunk'lık bir küme için
  performans sorun değil; büyük ölçekte özel bir vektör indeksi gerekirdi.
- **Benzerlik eşiği (0.45)** eklendi çünkü küçük dil modeli (1.5B parametre)
  "sadece context'i kullan" talimatını her zaman güvenilir şekilde takip
  etmiyor; düşük alakalı sorularda LLM'e hiç gitmeden fallback dönmek hem
  halüsinasyonu azaltıyor hem de yanıt süresini kısaltıyor.
- **CLI arayüz (Streamlit/web değil)** tercih edildi — backend mantığına
  odaklanmak ve süreyi aşmamak için; mimari zaten bir web arayüzüne
  bağlanmaya uygun (retrieval ve chat mantığı UI'dan bağımsız).

## Kurulum

```bash
# Foundry Local'i kur (Windows)
winget install Microsoft.FoundryLocal

# Python ortamı
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # macOS/Linux

pip install -r requirements.txt
```

## Çalıştırma

```bash
# 1. Dökümanları indeksle (rag.db oluşturur)
python ingest.py

# 2. Asistanı başlat
python main.py
```

Örnek sorular: `ESP-NOW nedir?`, `Servo motoru nasıl kontrol ederim?`,
`Brownout hatası nasıl çözülür?`

CLI komutları: `history` (soru-cevap geçmişi), `help` (yardım), `quit` (çıkış)

### Testleri çalıştırma

```bash
python run_tests.py
```

Sonuçlar `test_results.json`'a kaydedilir; detaylı analiz için `TEST_REPORT.md`'ye bakın.

## Bilinen Sınırlamalar

- Kelime bazında örtüşen ama konu olarak alakasız sorularda (örn. bilgi
  tabanında olmayan "kamera modülü" sorusu, "PWM/pin" kelimeleri yüzünden
  yüksek skor alabiliyor) benzerlik eşiği tek başına yeterli olmuyor —
  model bazen yine de halüsinasyon yapabiliyor. Detay için `TEST_REPORT.md`.
- 1.5B parametrelik model, çok büyük modellere kıyasla daha sınırlı akıl
  yürütme yeteneğine sahip; karmaşık çok adımlı sorularda performansı düşebilir.
- Bilgi tabanı küçük (8 chunk) ve elle hazırlandı; gerçek bir kullanım
  senaryosunda otomatik chunking (uzun dökümanları parçalara bölme) gerekir.

## Öğrenilenler

- Küçük yerel modeller (0.5B) prompt talimatlarını tutarlı takip etmede
  ciddi sorun yaşayabiliyor (tekrar döngüsü, dil karışımı); model boyutu ile
  güvenilirlik arasında gözle görülür bir ilişki var.
- Sadece prompt mühendisliğine güvenmek yetersiz kalabiliyor — retrieval
  skoru gibi ölçülebilir bir sinyali güvenlik katmanı olarak kullanmak
  (eşik altında LLM'i hiç çağırmamak) hem daha güvenilir hem daha hızlı.
- Basit kosinüs benzerliği, kelime örtüşmesi ile semantik alaka arasındaki
  farkı her zaman ayırt edemiyor — bu, RAG sistemlerinin bilinen bir
  zorluğu ve daha gelişmiş re-ranking yöntemlerinin neden var olduğunu
  gösteriyor.
