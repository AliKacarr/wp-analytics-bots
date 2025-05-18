# 📊 Selenium WhatsApp Otomatik Mesajlaşma ve Analiz Botu

Bu repo, WhatsApp gruplarında **otomatik mesaj gönderme**, **anket oluşturma** ve **istatistik toplama** işlemlerini kolaylaştırmak amacıyla geliştirilmiştir.

## 🚀 Özellikler

- WhatsApp Web veya masaüstü istemcisi üzerinde çalıştırabilirsiniz.
- Botlar mesaj gönderme, mesajları analiz etme, anket gönderme, anket sonuçlarını analiz etme özelliklerini sunar.
- Botlar seçilen Whatsapp grubunu açıp belirtilen işlemleri gerçekleştirir. Ardından oturumu sonlandırıp güvenli çıkış sağlar.

## 💻 Kullanım ve Yapılandırma

Botları kullanmadan önce aşağıdaki değişkenleri kendi kullanımınıza göre ayarlamanız gerekir:

```python
group_name = "Grup Adı"
options = {
    "seçenek1": ["varyant1", "varyant2"],
    "seçenek2": ["varyant1", "varyant2"]
}
start_datetime_str = "21:00 4/5/2025"  # saat:dakika gün/ay/yıl
end_datetime_str = "22:10 30/5/2025"
poll_topic = "Anket Başlığı"  # Anket analiz botu için
message_text = "Merhaba"  # Gönderilecek mesaj
```

## 🛠️ Gereksinimler

- Python 3.7+
- Chrome tarayıcısı ve `chromedriver`
- Selenium

Kurulum:

```bash
pip install -r requirements.txt
```

> Not: `chromedriver` sistem PATH'ine eklenmiş olmalıdır.

## 📁 Dosyalar

### `wp-bot-web-istatistikleri.py`
WhatsApp Web üzerinde belirtilen gruptaki mesajları analiz eder, tarih aralığı ve anahtar kelimelere göre sınıflandırır.

### `wp-bot-desktop.py`
Kullanıcının masaüstü uygulamasından kopyaladığı mesajları analiz eder.

### `wp-bot-oto-mesaj.py`
Belirtilen gruba istediğiniz mesajı gönderir.

### `wp-bot-anket-olusturucu.py`
Belirtilen gruba anket gönderir.

### `wp-bot-anket-istatistikleri.py`
Gruptaki anketi bulup ankete oy verenleri analiz eder.

### `logout_whatsapp.py`
WhatsApp Web oturumunu güvenli şekilde sonlandırmak için kullanılır.

## 📌 Notlar

- Scriptler Selenium kullanır. WhatsApp Web arayüzü değişirse bazı bölümlerde ufak güncellemeler gerekebilir.
- Botun çalışabilmesi için WhatsApp Web ana sayfasındaki QR kodun telefonla taratılması gerekmektedir. Tarama işleminden sonra bot ilgili sohbeti bulup otomatik olarak analiz işlemine devam eder. 
- Her script çalışmasını tamamladıktan sonra WhatsApp Web oturumunu kapatır.
- Bu işlemlerin başarıyla gerçekleşmesi, internet bağlantı hızınıza bağlı olarak yaklaşık 2 dakika sürebilir. Lütfen bu süreçte tarayıcıyı kapatmadan bekleyiniz.


## 🔐 Uyarı

Kendi sohbet verileriniz dışında kullanımda gizlilik kurallarına uymanız gerekmektedir. Bu araç yalnızca kişisel kullanım için tasarlanmıştır.
