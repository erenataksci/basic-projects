import requests  # API istekleri için
import getpass
import sys
from PyQt6.QtWidgets import QApplication
# notepad_gui import'u aynı kalıyor, çünkü arayüzü hala başlatacağız
from notepad_gui import NotepadWindow

# Hatalı giriş deneme hakkı
HATALI_GIRIS_LIMITI = 3
# API sunucumuzun adresi (Flask varsayılan olarak 5000 portunda çalışır)
API_URL = "http://127.0.0.1:5000"


def ana_menu():
    """Kullanıcıya ana menüyü gösterir."""
    # Artık veritabanını başlatmaya gerek yok, o işi sunucu yapıyor.

    hatali_deneme_sayisi = 0

    # Sunucunun çalışıp çalışmadığını kontrol edelim (isteğe bağlı ama iyi bir pratik)
    try:
        response = requests.get(f"{API_URL}/test", timeout=3)
        if response.status_code == 200:
            print("API Sunucusuna başarıyla bağlanıldı.")
        else:
            print(f"API Sunucusuna bağlanılamadı! Durum Kodu: {response.status_code}")
            return  # Sunucu yoksa devam etme
    except requests.exceptions.RequestException as e:
        print(f"API Sunucusuna bağlanırken hata oluştu: {e}")
        print("Lütfen önce 'api_server.py' dosyasını çalıştırdığınızdan emin olun.")
        return  # Sunucu yoksa devam etme

    while True:
        print("\n--- Güvenli Not Defteri (Online) ---")
        print("1: Kayıt Ol")
        print("2: Giriş Yap")
        print("3: Çıkış")

        secim = input("Lütfen yapmak istediğiniz işlemi seçin (1-3): ")

        if secim == '1':
            kayit_ol()
        elif secim == '2':
            # giris_yap fonksiyonu başarılı olursa kullanıcı bilgilerini (örn: firebase_id), değilse None döndürür
            giris_bilgisi = giris_yap()

            if giris_bilgisi:
                # GİRİŞ BAŞARILI!
                print(f"Giriş başarılı. Arayüz başlatılıyor...")

                # Başarılı girişte API'den dönen Firebase ID'sini al
                # Bu ID'yi not defteri arayüzüne göndereceğiz
                firebase_id = giris_bilgisi.get("firebase_id")

                if firebase_id:
                    arac_calistir(firebase_id)  # GUI'yi Firebase ID ile başlat
                    break
                else:
                    print("Kritik hata: Giriş sonrası kullanıcı ID'si alınamadı.")

            else:
                # GİRİŞ BAŞARISIZ!
                hatali_deneme_sayisi += 1
                kalan_hak = HATALI_GIRIS_LIMITI - hatali_deneme_sayisi

                if kalan_hak > 0:
                    print(f"Kullanıcı adı veya parola yanlış! Kalan deneme hakkınız: {kalan_hak}")
                else:
                    print("Çok fazla hatalı deneme. Program güvenlik nedeniyle kapatılıyor.")
                    break

        elif secim == '3':
            print("Programdan çıkılıyor. Görüşmek üzere!")
            break
        else:
            print("Geçersiz seçim. Lütfen 1, 2 veya 3 girin.")


def kayit_ol():
    """Kullanıcıdan bilgileri alır ve API'ye kayıt isteği gönderir."""
    print("\n--- Yeni Kullanıcı Kaydı ---")
    kullanici_adi = input("Kullanıcı Adı: ").strip()
    parola = getpass.getpass("Parola: ").strip()
    parola_tekrar = getpass.getpass("Parola (Tekrar): ").strip()

    if not kullanici_adi or not parola:
        print("Kullanıcı adı veya parola boş bırakılamaz.")
        return
    if parola != parola_tekrar:
        print("Parolalar eşleşmiyor! Lütfen tekrar deneyin.")
        return

    # API'ye göndereceğimiz veriyi bir sözlük olarak hazırlıyoruz
    kayit_verisi = {
        "kullanici_adi": kullanici_adi,
        "parola": parola
        # Parolayı hash'lemiyoruz! Hash'leme işini sunucu yapacak.
    }

    try:
        # API'deki '/kayit-ol' endpoint'ine POST isteği gönderiyoruz
        response = requests.post(f"{API_URL}/kayit-ol", json=kayit_verisi, timeout=10)

        # Sunucudan gelen cevabı işliyoruz
        if response.status_code == 201:  # 201 Created (Başarılı Kayıt)
            print(response.json().get("mesaj", "Kayıt başarılı."))
        else:
            # Hata durumunda sunucunun gönderdiği hata mesajını yazdır
            hata_mesaji = response.json().get("hata", "Bilinmeyen bir hata oluştu.")
            print(f"Kayıt Hatası ({response.status_code}): {hata_mesaji}")

    except requests.exceptions.RequestException as e:
        print(f"API Sunucusuna bağlanırken hata oluştu: {e}")


def giris_yap():
    """Kullanıcıdan bilgileri alır ve API'ye giriş isteği gönderir."""
    print("\n--- Kullanıcı Girişi ---")
    kullanici_adi = input("Kullanıcı Adı: ").strip()
    parola = getpass.getpass("Parola: ").strip()

    giris_verisi = {
        "kullanici_adi": kullanici_adi,
        "parola": parola
    }

    try:
        response = requests.post(f"{API_URL}/giris-yap", json=giris_verisi, timeout=10)

        if response.status_code == 200:  # 200 OK (Başarılı Giriş)
            # Başarılı girişte sunucudan gelen JSON verisini (mesaj ve firebase_id içerir) döndür
            return response.json()
        else:
            # Hatalı girişte None döndür
            return None

    except requests.exceptions.RequestException as e:
        print(f"API Sunucusuna bağlanırken hata oluştu: {e}")
        return None


def arac_calistir(aktif_kullanici_firebase_id):  # Artık SQLite ID yerine Firebase ID alıyor
    """
    PyQt6 arayüz uygulamasını başlatır.
    """
    app = QApplication(sys.argv)
    # NotepadWindow'u Firebase ID ile başlatıyoruz
    # (NotepadWindow sınıfını da bu değişikliğe göre güncellememiz gerekecek)
    window = NotepadWindow(aktif_kullanici_firebase_id)
    window.show()
    app.exec()


# --- Programı Başlat ---
if __name__ == "__main__":
    ana_menu()