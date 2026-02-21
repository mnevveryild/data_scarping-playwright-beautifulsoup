import pandas as pd
import mysql.connector
from mysql.connector import Error
import re

# Temizleme fonksiyonları
def temizle_sayi(metin):
    if pd.isna(metin) or metin == "-":
        return 0
    #sadece rakamları tut noktaları ve virgülleri temizle örn: 1.500.000 -> 1500000
    rakamlar = re.sub(r'\D', '', str(metin))
    return int(rakamlar) if rakamlar else 0

def temizle_metin(metin):
    if pd.isna(metin) or metin == "-":
        return ""
    return str(metin).strip()

#main
def main():
    dosya_yolu = "ankara_emlak_FINAL_FULL_KONUM - Kopya.csv"

    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="muni1234.",
            database="ankara_full_4"
        )

        cursor = db.cursor()
        print("DB bağlantısı başarılı.")

        # CSV dosyasını oku
        df = pd.read_csv(dosya_yolu, sep=";", encoding="utf-8-sig")
        df.columns = df.columns.str.strip().str.lower()

        # SQL Sorgusu (16 adet sütun ve tam 16 adet %s var)
        sql = """
        INSERT INTO ilanlar (
            ilan_no, baslik, fiyat, oda_sayisi, m2, bulundugu_kat,
            bina_yasi, isinma_tipi, tapu_durumu, konut_tipi,
            banyo_sayisi, kat_sayisi, krediye_uygun, esya_durumu, konum, url
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            fiyat=VALUES(fiyat),
            baslik=VALUES(baslik),
            konum=VALUES(konum);
        """

        sayac = 0
        for _, row in df.iterrows():
            # Değerleri CSV'deki sütun isimlerine göre çekiyoruz
            degerler = (
                temizle_metin(row.get("ilan_no")),
                temizle_metin(row.get("baslik")),
                temizle_sayi(row.get("fiyat")),
                temizle_metin(row.get("oda_sayisi")),
                temizle_sayi(row.get("m2")),
                temizle_metin(row.get("bulundugu_kat")),
                temizle_sayi(row.get("bina_yasi")),
                temizle_metin(row.get("isinma_tipi")),
                temizle_metin(row.get("tapu_durumu")),
                temizle_metin(row.get("konut_tipi")),
                temizle_sayi(row.get("banyo_sayisi")),
                temizle_sayi(row.get("kat_sayisi")),
                temizle_metin(row.get("krediye_uygun")),
                temizle_metin(row.get("esya_durumu")),
                temizle_metin(row.get("konum")),
                temizle_metin(row.get("url"))    
            )

            cursor.execute(sql, degerler)
            sayac += 1
            

            if sayac % 100 == 0:
                db.commit()

        db.commit()
        print(f"İşlem tamamlandı: {sayac} kayıt eklendi/güncellendi.")

    except Error as e:
        print("Bir hata oluştu:", e)

    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()
            print("Veritabanı bağlantısı kapatıldı.")

if __name__ == "__main__":
    main()