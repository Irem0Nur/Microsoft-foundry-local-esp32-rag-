# Hafta 5: Fonksiyonel test seti
# answerable=True  -> bilgi tabanında karşılığı var, doğru/alakalı cevap beklenir
# answerable=False -> bilgi tabanında YOK, model "bilmiyorum" demeli (uydurmamalı)

TEST_CASES = [
    # --- Cevaplanabilir (bilgi tabanında var) ---
    {"query": "ESP-NOW nedir?", "answerable": True},
    {"query": "Servo motoru nasıl kontrol ederim?", "answerable": True},
    {"query": "Brownout hatası nasıl çözülür?", "answerable": True},
    {"query": "ESP32'yi hangi voltajlarla besleyebilirim?", "answerable": True},
    {"query": "Deep sleep modu ne işe yarar?", "answerable": True},
    {"query": "ESP-NOW ile iki cihazı nasıl eşleştiririm?", "answerable": True},
    # --- Cevaplanamaz (bilgi tabanı dışı, model uydurmamalı) ---
    {"query": "ESP32 geliştirme kartının fiyatı nedir?", "answerable": False},
    {"query": "Bluetooth Low Energy (BLE) nasıl kullanılır?", "answerable": False},
    {"query": "Python ile bir web sitesi nasıl yaparım?", "answerable": False},
    {"query": "ESP32'de kamera modülü nasıl bağlanır?", "answerable": False},
    # --- Uç durumlar ---
    {"query": "asdkjfh qwerty 12345", "answerable": False},  # anlamsız girdi
]
