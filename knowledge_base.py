# Bilgi tabanı: ESP32 geliştirme kartı kullanım kılavuzu / SSS
# Her giriş: (kaynak_adi, metin) - kaynak_adi citation icin kullanilir

DOCUMENTS = [
    (
        "Kurulum Kılavuzu - Bölüm 1",
        "ESP32'yi bilgisayara bağlamak için bir micro-USB veya USB-C kablo gerekir "
        "(model varyantına göre değişir). Arduino IDE kullanıyorsanız, Dosya > Tercihler "
        "menüsünden 'Ek Kart Yöneticisi URL'leri' alanına ESP32 board paket linkini eklemeniz "
        "gerekir. Ardından Araçlar > Kart > Kart Yöneticisi üzerinden 'esp32' aratıp yükleyin.",
    ),
    (
        "Kurulum Kılavuzu - Bölüm 2",
        "Kart bağlandıktan sonra Araçlar menüsünden doğru COM portunu seçmelisiniz. Windows'ta "
        "port görünmüyorsa CP2102 veya CH340 USB-seri sürücüsünün kurulu olduğundan emin olun. "
        "Kod yüklerken bazı ESP32 kartlarında BOOT butonuna basılı tutmanız gerekebilir.",
    ),
    (
        "ESP-NOW Protokolü SSS",
        "ESP-NOW, Wi-Fi router gerektirmeden iki veya daha fazla ESP32 cihazının doğrudan birbiriyle "
        "haberleşmesini sağlayan düşük gecikmeli bir Espressif protokolüdür. Maksimum tek paket "
        "boyutu 250 bayttır. Bir cihaz aynı anda hem istasyon (station) hem soft-AP modunda çalışabilir.",
    ),
    (
        "ESP-NOW Eşleştirme",
        "ESP-NOW ile haberleşmek için alıcı cihazın MAC adresini bilmeniz ve esp_now_add_peer() "
        "fonksiyonuyla eşleştirme (peer) listesine eklemeniz gerekir. MAC adresini öğrenmek için "
        "WiFi.macAddress() fonksiyonu kullanılabilir. Şifreleme opsiyoneldir ve peer bazında ayarlanır.",
    ),
    (
        "Güç Yönetimi SSS",
        "ESP32, USB üzerinden 5V ile beslenebileceği gibi VIN pininden 5-12V veya 3V3 pininden "
        "doğrudan 3.3V ile de beslenebilir. Servo motor veya röle gibi yüksek akım çeken bileşenler "
        "için ayrı bir güç kaynağı kullanılması ve ortak toprak (GND) bağlantısı önerilir.",
    ),
    (
        "Derin Uyku (Deep Sleep) Modu",
        "Pil ömrünü uzatmak için ESP32 deep sleep moduna alınabilir; bu modda RTC hariç çoğu "
        "bileşen kapanır ve akım tüketimi mikroamper seviyesine düşer. esp_sleep_enable_timer_wakeup() "
        "ile belirli bir süre sonra otomatik uyanma ayarlanabilir.",
    ),
    (
        "Sık Karşılaşılan Hatalar",
        "'Brownout detector was triggered' hatası genellikle yetersiz güç kaynağından kaynaklanır; "
        "USB hub yerine doğrudan bilgisayar portu veya harici güç kaynağı kullanmayı deneyin. "
        "'A fatal error occurred: Failed to connect to ESP32' hatası içinse BOOT butonuna basılı "
        "tutarak yükleme yapmayı deneyin.",
    ),
    (
        "PWM ve Servo Kontrolü",
        "ESP32'de PWM üretmek için LEDC (LED Control) çevre birimi kullanılır; ledcAttach() ve "
        "ledcWrite() fonksiyonlarıyla frekans, çözünürlük ve duty cycle ayarlanabilir. Servo motorlar "
        "genellikle 50Hz frekans ve 1-2ms darbe genişliğiyle kontrol edilir.",
    ),
]
