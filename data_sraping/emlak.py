import csv
import time
import random
import os
import re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

#dosya ismini güncel tutuyoruz sizdeki isim neyse onu yazıyoruz
SU_ANKI_KLASOR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_PATH = os.path.join(SU_ANKI_KLASOR, "ankara_emlak_FINAL_FULL_KONUM_2.csv")

def save_to_csv(data_list):
    fields = [
        'ilan_no', 'baslik', 'fiyat', 'konut_tipi', 'oda_sayisi', 'm2', 
        'bulundugu_kat', 'bina_yasi', 'isinma_tipi', 'tapu_durumu', 
        'banyo_sayisi', 'kat_sayisi', 'krediye_uygun', 'esya_durumu', 
        'firma_adi', 'ilan_tarihi', 'konum', 'url'
    ]
    
    file_exists = os.path.isfile(CSV_FILE_PATH)
    with open(CSV_FILE_PATH, mode='a', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=fields, delimiter=';')
        if not file_exists:
            writer.writeheader()
        writer.writerows(data_list)
        file.flush()

def get_detay_verileri(context, url):
    """
    İlan detayına girer:
    1. Kat Sayısı
    2. İlan Tarihi
    3. Detaylı Konum (İl/İlçe/Mahalle) bilgilerini çeker.
    """
    result = {'kat_sayisi': '-', 'ilan_tarihi': '-', 'konum': '-'}
    new_page = None
    try:
        new_page = context.new_page()
        new_page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        #sayfanın yüklenmesini bekle
        try:
            new_page.wait_for_selector(".spec-item", timeout=5000)
        except:
            pass 
        
        #isteğe bağlı bekleme süresi mevcut ayarı 5 sn
        time.sleep(8) 

        content = new_page.content()
        soup = BeautifulSoup(content, 'html.parser')

        #1. KAT SAYISI ayrıntılı şekilde verdik çünkü bazı ilanlarda farklı yerlerde olabiliyor
        kat_sayisi = "-"
        value_txts = soup.find_all('span', class_='value-txt')
        for span in value_txts:
            txt = span.get_text(strip=True)
            if "Katlı" in txt:
                kat_sayisi = txt.replace("Katlı", "").strip()
                break
        
        if kat_sayisi == "-":
            specs = soup.find_all('li', class_='spec-item')
            for item in specs:
                if "Kat Sayısı" in item.get_text():
                    val_span = item.find_all('span')[-1]
                    kat_sayisi = val_span.get_text(strip=True).replace("Katlı", "").strip()
                    break
        result['kat_sayisi'] = kat_sayisi

        # İLAN TARİHİ: Genellikle <time datetime="2024-05-01">1 Mayıs 2024</time> şeklinde olur, ama bazen metin içinde de olabilir
        time_tag = soup.find('time', attrs={'datetime': True})
        if time_tag:
            result['ilan_tarihi'] = time_tag['datetime']
        else:
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})|(\d{2}-\d{2}-\d{4})', soup.get_text())
            if date_match:
                result['ilan_tarihi'] = date_match.group(0)

        # DETAYLI KONUM (İl/İlçe/Mahalle): Genellikle .detail-info-location sınıfında olur, içinde div'ler olabilir
        
        addr_tag = soup.select_one('.detail-info-location')
        if addr_tag:
            # İçindeki div'leri topla: ["Ankara", "Etimesgut", "Ahi Mesut Mah."]
            loc_parts = [div.get_text(strip=True) for div in addr_tag.find_all('div')]
            # Birleştir: "Ankara / Etimesgut / Ahi Mesut Mah."
            result['konum'] = " / ".join([p for p in loc_parts if p])

    except Exception as e:
        print(f"    [Detay Hatası] Veri çekilemedi: {e}")
    finally:
        if new_page:
            new_page.close()
    
    return result

def main():
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = context.pages[0]
            print(f"Bağlantı kuruldu. Veriler şuraya kaydedilecek: {CSV_FILE_PATH}")
        except:
            print("HATA: Chrome portu (9222) açık değil!")
            return

        for page_num in range(297, 750): 
            target_url = f"https://www.hepsiemlak.com/ankara-satilik?page={page_num}"
            print(f"\n>>> Sayfa {page_num} işleniyor...")
            
            try:
                page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(5)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(5)
                
                soup = BeautifulSoup(page.content(), 'html.parser')
                listings = soup.select('.listing-item')
                
                print(f"    Bu sayfada {len(listings)} ilan bulundu.")

                final_data = []
                for index, listing in enumerate(listings):
                    try:
                        # Temel Link ve ID
                        link_tag = listing.select_one('a.card-link')
                        url = "https://www.hepsiemlak.com" + link_tag['href'] if link_tag else "-"
                        ilan_no = url.split('/')[-1] if '/' in url else "-"
                        
                        # Fiyat
                        fiyat_ham = listing.select_one('.list-view-price').get_text(strip=True) if listing.select_one('.list-view-price') else "0"
                        fiyat = fiyat_ham.replace("TL", "").replace(".", "").strip()

                        # Liste sayfasından yedek veriler
                        oda = listing.select_one('.houseRoomCount').get_text(strip=True).replace("\n", "").strip() if listing.select_one('.houseRoomCount') else "-"
                        m2 = listing.select_one('.squareMeter').get_text(strip=True).replace("m²", "").strip() if listing.select_one('.squareMeter') else "-"
                        yas = listing.select_one('.buildingAge').get_text(strip=True).replace(" Yaşında", "").strip() if listing.select_one('.buildingAge') else "-"
                        bulundugu_kat = listing.select_one('.floortype').get_text(strip=True) if listing.select_one('.floortype') else "-"
                        firma = listing.select_one('.listing-card--owner-info__firm-name').get_text(strip=True) if listing.select_one('.listing-card--owner-info__firm-name') else "-"
                        konut_tipi = listing.select_one('.left').get_text(strip=True) if listing.select_one('.left') else "Daire"
                        
                        # Liste sayfasındaki konum (Yedek olarak tutuyoruz)
                        konum_liste = listing.select_one('address').get_text(strip=True) if listing.select_one('address') else "-"

                        # DETAY SAYFASINA GİDİŞ VE ORADAN VERİ ÇEKME ---
                        detay_verileri = {'kat_sayisi': '-', 'ilan_tarihi': '-', 'konum': '-'}
                        
                        if url != "-":
                            detay_verileri = get_detay_verileri(context, url)
                            
                            # Eğer detaydan konum geldiyse onu kullan, gelmediyse listedekini kullan
                            final_konum = detay_verileri['konum'] if detay_verileri['konum'] != '-' else konum_liste
                            
                            print(f"    [{index+1}/{len(listings)}] {ilan_no} | Kat:{detay_verileri['kat_sayisi']} | Tarih:{detay_verileri['ilan_tarihi']} | Yer:{final_konum}")
                        else:
                            final_konum = konum_liste

                        final_data.append({
                            'ilan_no': ilan_no,
                            'baslik': f"{konut_tipi} - {final_konum}",
                            'fiyat': fiyat,
                            'konut_tipi': konut_tipi,
                            'oda_sayisi': oda,
                            'm2': m2,
                            'bulundugu_kat': bulundugu_kat,
                            'bina_yasi': yas,
                            'isinma_tipi': "Kombi (Doğalgaz)", 
                            'tapu_durumu': "Kat Mülkiyeti",
                            'banyo_sayisi': "1",
                            'kat_sayisi': detay_verileri['kat_sayisi'],
                            'krediye_uygun': "Evet",
                            'esya_durumu': "Boş",
                            'firma_adi': firma,
                            'ilan_tarihi': detay_verileri['ilan_tarihi'],
                            'konum': final_konum, # Detaylı konum buraya yazılıyor
                            'url': url
                        })
                        
                        time.sleep(3)

                    except Exception as inner_e: 
                        print(f"    İlan işleme hatası: {inner_e}")
                        continue

                if final_data:
                    save_to_csv(final_data)
                    print(f"Sayfa {page_num}: {len(final_data)} ilan diske yazıldı.")
                
            except Exception as e:
                print(f"Sayfa hatası: {e}")
                continue

        print(f"\nİşlem Tamamlandı. Dosya: {CSV_FILE_PATH}")

if __name__ == "__main__":
    main()