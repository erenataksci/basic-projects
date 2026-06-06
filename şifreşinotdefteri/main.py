import veritabani as db
import getpass
import sys
from PyQt6.QtWidgets import QApplication
from notepad_gui import NotepadWindow

# Hatalı giriş deneme hakkı
HATALI_GIRIS_LIMITI = 3


def ana_menu():
    """Kullanıcıya ana menüyü gösterir."""
    db.veritabanini_baslat()

    hatali_deneme_sayisi = 0

    while True:
        print("\n--- Güvenli Not Defteri ---")
        print("1: Kayıt Ol")
        print("2: Giriş Yap")
        print("3: Çıkış")

        secim = input("Lütfen yapmak istediğiniz işlemi seçin (1-3): ")

        if secim == '1':
            kayit_ol()
        elif secim == '2':
            basarili_giris_kullanici_adi = giris_yap()

            if basarili_giris_kullanici_adi:
                print(f"Giriş başarılı. {basarili_giris_kullanici_adi} için arayüz başlatılıyor...")

                kullanici_id = db.kullanici_id_getir(basarili_giris_kullanici_adi)

                if kullanici_id:
                    arac_calistir(kullanici_id)
                    break
                else:
                    print("Kritik hata: Kullanıcı ID'si alınamadı.")

            else:
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
    """Kullanıcıdan bilgileri alıp kayıt fonksiyonunu çağırır."""
    print("\n--- Yeni Kullanıcı Kaydı ---")
    kullanici_adi = input("Kullanıcı Adı: ").strip()
    parola = getpass.getpass("Parola: ").strip()
    parola_tekrar = getpass.getpass("Parola (Tekrar): ").strip()

    if not kullanici_adi or not parola:
        print("Kullanıcı adı veya parola boş olamaz.")
        return
    if parola != parola_tekrar:
        print("Parolalar eşleşmiyor! Lütfen tekrar deneyin.")
        return
    db.kullanici_kaydet(kullanici_adi, parola)


def giris_yap():
    """Kullanıcıdan bilgileri alıp doğrular. Başarılıysa kullanıcı adını, değilse None döndürür."""
    print("\n--- Kullanıcı Girişi ---")
    kullanici_adi = input("Kullanıcı Adı: ").strip()
    parola = getpass.getpass("Parola: ").strip()

    if db.kullanici_dogrula(kullanici_adi, parola):
        return kullanici_adi
    else:
        return None


def arac_calistir(aktif_kullanici_id):
    """
    PyQt6 arayüz uygulamasını başlatır.
    """
    app = QApplication(sys.argv)
    window = NotepadWindow(aktif_kullanici_id)
    window.show()
    app.exec()


# --- Programı Başlat ---
if __name__ == "__main__":
    ana_menu()