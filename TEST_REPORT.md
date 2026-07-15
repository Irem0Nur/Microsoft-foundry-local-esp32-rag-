# Test Raporu — Hafta 5

## Yöntem

11 test sorusu içeren bir set (`test_cases.py`) hazırlandı: 6 tanesi bilgi tabanında
karşılığı olan (answerable), 4 tanesi kapsam dışı (unanswerable), 1 tanesi anlamsız
girdi (edge case). `run_tests.py` her soruyu otomatik çalıştırıp yanıt süresini,
retrieval skorunu ve cevabı `test_results.json`'a kaydeder.

## Sonuçlar (son çalıştırma)

| # | Soru | Beklenen | Skor | Süre | Sonuç |
|---|------|----------|------|------|-------|
| 1 | ESP-NOW nedir? | Cevaplanabilir | 0.765 | 4.8s | ✅ Doğru |
| 2 | Servo motoru nasıl kontrol ederim? | Cevaplanabilir | 0.511 | 7.9s | ✅ Doğru |
| 3 | Brownout hatası nasıl çözülür? | Cevaplanabilir | 0.490 | 5.7s | ✅ Doğru |
| 4 | ESP32'yi hangi voltajlarla besleyebilirim? | Cevaplanabilir | 0.757 | 4.8s | ✅ Doğru |
| 5 | Deep sleep modu ne işe yarar? | Cevaplanabilir | 0.585 | 4.7s | ✅ Doğru |
| 6 | ESP-NOW ile eşleştirme | Cevaplanabilir | 0.685 | 6.1s | ✅ Doğru |
| 7 | Kartın fiyatı nedir? | Cevaplanamaz | 0.611 | 3.0s | ✅ "Bilmiyorum" |
| 8 | BLE nasıl kullanılır? | Cevaplanamaz | 0.441 | 0.5s | ✅ Fallback (eşik altı) |
| 9 | Python ile web sitesi | Cevaplanamaz | 0.307 | 0.4s | ✅ Fallback (eşik altı) |
| 10 | Kamera modülü bağlantısı | Cevaplanamaz | 0.658 | 8.1s | ⚠️ Halüsinasyon |
| 11 | Anlamsız girdi | Cevaplanamaz | 0.399 | 0.5s | ✅ Fallback (eşik altı) |

**10/11 doğru davranış. Ortalama yanıt süresi: 4.24s.**

## Bulgular ve İyileştirmeler

1. **Tekrar döngüsü (ilk sürüm):** `qwen2.5-0.5b` modeli bazı sorularda sonsuz
   tekrara girip Korece/Çince karışık metin üretiyordu. → `qwen2.5-1.5b`'ye
   geçildi, `temperature=0.3` ve `max_tokens=250` eklendi. Sorun çözüldü.

2. **Talimat takip etmeme:** Sistem prompt'u "sadece context'i kullan, bilmiyorsan
   söyle" dese de model bazen kapsam dışı sorularda kendi (çoğu hatalı) genel
   bilgisinden cevap uydurdu (BLE, Python web, kamera soruları).
   → **Benzerlik eşiği (0.45)** eklendi: en iyi eşleşen chunk'ın kosinüs skoru
   eşiğin altındaysa LLM hiç çağrılmıyor, doğrudan "bilgi bulamadım" dönülüyor.
   Bu hem 3 sorudaki halüsinasyonu düzeltti hem de yanıt süresini ciddi
   düşürdü (0.4-0.5s, LLM çağrısı atlandığı için).

## Bilinen Sınırlama

**Kamera modülü sorusu (skor 0.658) eşiğin üzerinde kaldığı için hâlâ halüsinasyon
yapıyor.** Sebep: soru donanım bağlama/pin/kod kelimeleri içeriyor, bu kelimeler
bilgi tabanındaki *alakasız* dökümanlarla (PWM, kurulum) yüzeysel embedding
benzerliği yaratıyor — retrieval "yanlış ama yüksek skorlu" bir chunk buluyor.
Basit kosinüs benzerliği eşiği bu tür "kelime örtüşmesi var ama konu farklı"
durumlarını ayırt edemiyor.

**Olası çözümler (bu programın kapsamı dışında, ileri çalışma için not):**
- Daha büyük/yetenekli bir embedding modeli
- Skor eşiği yerine "en iyi skor ile ikinci en iyi skor arasındaki fark" (margin)
  bazlı bir güven ölçütü
- Retrieval sonrası ikinci bir LLM adımıyla "bu chunk gerçekten soruyla alakalı mı?"
  kontrolü (re-ranking)

## Sonuç

Sistem, bilgi tabanı kapsamındaki sorularda tutarlı ve kaynak belirten cevaplar
veriyor; açık kapsam dışı sorularda (düşük skor) güvenilir şekilde "bilmiyorum"
diyor. Kelime örtüşmesi yüksek ama konu alakasız sınır durumlarında halüsinasyon
riski hâlâ mevcut — bu, projenin dokümante edilmiş bilinen sınırlamasıdır.
