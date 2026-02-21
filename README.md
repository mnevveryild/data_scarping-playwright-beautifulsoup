# 🏠 Ankara Emlak Veri Kazıma Projesi (Web Scraping)

Bu proje, **Playwright** ve **BeautifulSoup** kütüphaneleri kullanılarak dinamik web sayfalarından Ankara lokasyonlu satılık konut verilerini otonom bir şekilde toplamak için geliştirilmiştir. 



## 🚀 Öne Çıkan Özellikler

* **Dinamik İçerik Yönetimi:** Playwright sayesinde JavaScript tabanlı yüklenen içerikler başarıyla çekilir.
* **Anti-Bot Çözümü (CDP):** `connect_over_cdp` yöntemiyle mevcut bir Chrome oturumuna bağlanarak, web sitelerinin bot koruma mekanizmaları (anti-bot) aşılmıştır.
* **Derinlemesine Kazıma:** Sadece liste sayfaları değil, her ilanın detay sayfasına girilerek; **kat sayısı, ilan tarihi ve detaylı konum** gibi kritik veriler toplanmaktadır.
* **Hata Yönetimi:** Script, veri çekme sırasında oluşabilecek hatalara karşı (ilan silinmesi, bağlantı kopması vb.) dayanıklıdır ve işlemine kesintisiz devam eder.

## 🛠 Kullanılan Teknolojiler

* **Python 3.x**
* **Playwright:** Modern ve hızlı tarayıcı otomasyonu.
* **BeautifulSoup4:** HTML ayrıştırma (parsing) işlemleri.
* **Pandas / CSV:** Verilerin yapılandırılmış formatta saklanması.
* **Regular Expressions (re):** Metin tabanlı verilerin temizlenmesi ve düzenlenmesi.

## 📋 Proje Mimarisi

1.  **Bağlantı:** Script, `9222` portu üzerinden açık olan tarayıcıya bağlanır.(Windows+R ye basıyoruz ve chrome.exe --remote-debugging-port=9222 --user-data- kodunu yapıştırıp sayfayı açıyoruz.)
2.  **Sayfa Gezintisi:** 297 ile 750 arasındaki sayfalar sırayla taranır.
3.  **Veri Ayıklama:** Liste sayfasından temel bilgiler, ilan detay sayfasından ise spesifik özellikler çekilir.
4.  **Kayıt:** Veriler her sayfa sonunda `ankara_emlak_FINAL_FULL_KONUM_2.csv` dosyasına `UTF-8` kodlamasıyla eklenir.

## ⚙️ Kurulum ve Çalıştırma

1. Projeyi klonlayın:
   ```bash
   git clone [https://github.com/mnevveryild/data_scarpin-playwright-beautifulsoup.git](https://github.com/mnevveryild/data_scarpin-playwright-beautifulsoup.git)
