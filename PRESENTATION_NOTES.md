# Final Sunum Akışı (~5 dakika)

## 1. Problem Tanımı (~45 sn)
- Genel LLM'ler dar bir domain hakkında (örn. belirli bir kartın SSS'i) soru
  sorulduğunda ya bilmez ya da uydurur.
- Hedef: **tamamen çevrimdışı**, kaynak gösteren, ESP32 hakkında soru
  yanıtlayan bir asistan — Microsoft Foundry Local ile.

## 2. Mimari & Temel Bileşenler (~90 sn)
- Akışı çiz/anlat: Soru → Embed → SQLite'ta benzerlik araması → (eşik kontrolü)
  → Chat modeli → kaynaklı cevap.
- Neden SQLite: basit, sunucusuz, küçük ölçek için yeterli.
- Neden benzerlik eşiği: modelin talimat takip etmemesine karşı güvenlik ağı.
- (`README.md`'deki mimari diyagramını ekranda gösterebilirsin.)

## 3. Canlı Demo (~90 sn)
Önerilen 3 soru (üç farklı davranışı gösterir):
1. `ESP-NOW nedir?` → kaynaklı, doğru cevap (yüksek skor)
2. `Python ile bir web sitesi nasıl yaparım?` → anında "bilmiyorum" (eşik altı,
   LLM hiç çağrılmadı — hızına dikkat çek)
3. `ESP32'de kamera modülü nasıl bağlanır?` → **bilinçli olarak** bilinen
   sınırlamayı göster: skor yüksek ama konu kapsam dışı, model halüsinasyon
   yapabilir. Bunu saklamak yerine açıkça "işte bulduğumuz gerçek bir sınır
   durumu" diye sunmak güçlü bir izlenim bırakır.

## 4. Test Süreci (~45 sn)
- 11 sorudan oluşan otomatik test seti, 10/11 doğru davranış.
- Ortalama yanıt süresi 4.24s (eşik sayesinde kapsam dışı sorularda 0.4-0.5s'ye
  düştü).

## 5. Öğrenilenler (~45 sn)
- Küçük modeller (0.5B) tekrar döngüsüne girip dil karıştırabiliyor →
  1.5B'ye geçiş + temperature/max_tokens ayarı çözdü.
- Prompt talimatı tek başına yetmiyor — ölçülebilir bir sinyal (benzerlik
  skoru) ekstra güvenlik katmanı olarak gerekli.
- Kelime örtüşmesi ile semantik alaka farklı şeyler — RAG'ın bilinen
  zorluklarından biri.

## 6. Kapanış (~15 sn)
- Kod ve dokümantasyon GitHub'da: (repo linkini söyle)
- Soru al.

---
*Not: Zamanlamalar tahminidir, kendi konuşma hızına göre ayarla. Slayt
gerekmiyorsa README'deki mimari diyagramı ve terminal ekranı yeterli.*
