import sqlite3
import hashlib


def veritabanini_baslat():
    """
    Veritabanını ve GEREKLİ TÜM TABLOLARI oluşturur.
    (kullanicilar ve notlar tablosu)
    """
    conn = sqlite3.connect('kullanicilar.db')
    cursor = conn.cursor()

    # 1. KULLANICILAR TABLOSU
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS kullanicilar
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       kullanici_adi
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       parola_hash
                       TEXT
                       NOT
                       NULL
                   )
                   ''')

    # 2. NOTLAR TABLOSU
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS notlar
                   (
                       not_id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       baslik
                       TEXT
                       NOT
                       NULL,
                       icerik
                       TEXT,
                       kullanici_id
                       INTEGER
                       NOT
                       NULL,
                       FOREIGN
                       KEY
                   (
                       kullanici_id
                   ) REFERENCES kullanicilar
                   (
                       id
                   )
                       ON DELETE CASCADE
                       )
                   ''')
    # FOREIGN KEY (kullanici_id) REFERENCES kullanicilar (id):
    # Bu, 'notlar' tablosundaki 'kullanici_id' sütununun,
    # 'kullanicilar' tablosundaki 'id' sütununa bağlı olduğunu söyler.
    # ON DELETE CASCADE:
    # Bir kullanıcı 'kullanicilar' tablosundan silinirse,
    # o kullanıcıya ait TÜM notlar da bu tablodan otomatik olarak silinir.

    conn.commit()
    conn.close()


def hash_parola(parola):
    """Verilen parolayı SHA-256 ile hash'ler."""
    return hashlib.sha256(parola.encode('utf-8')).hexdigest()


def kullanici_kaydet(kullanici_adi, parola):
    """Yeni bir kullanıcıyı veritabanına kaydeder."""
    conn = sqlite3.connect('kullanicilar.db')
    cursor = conn.cursor()
    try:
        hashed_parola = hash_parola(parola)
        cursor.execute("INSERT INTO kullanicilar (kullanici_adi, parola_hash) VALUES (?, ?)",
                       (kullanici_adi, hashed_parola))
        conn.commit()
        print(f"Başarılı! '{kullanici_adi}' adlı kullanıcı kaydedildi.")
        return True
    except sqlite3.IntegrityError:
        print(f"Hata: '{kullanici_adi}' kullanıcı adı zaten alınmış.")
        return False
    finally:
        conn.close()


def kullanici_dogrula(kullanici_adi, parola):
    """Kullanıcı adı ve parolanın doğru olup olmadığını kontrol eder."""
    conn = sqlite3.connect('kullanicilar.db')
    cursor = conn.cursor()
    cursor.execute("SELECT parola_hash FROM kullanicilar WHERE kullanici_adi = ?", (kullanici_adi,))
    kayit = cursor.fetchone()
    conn.close()

    if kayit:
        kayitli_hash = kayit[0]
        girilen_hash = hash_parola(parola)
        return kayitli_hash == girilen_hash
    return False


def kullanici_id_getir(kullanici_adi):
    """Giriş yapan kullanıcının ID'sini döndürür."""
    conn = sqlite3.connect('kullanicilar.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM kullanicilar WHERE kullanici_adi = ?", (kullanici_adi,))
    kayit = cursor.fetchone()
    conn.close()
    if kayit:
        return kayit[0]  # Kullanıcının ID'si
    return None


def notlari_getir(kullanici_id):
    """Belirli bir kullanıcıya ait tüm notları (id, baslik) getirir."""
    conn = sqlite3.connect('kullanicilar.db')
    cursor = conn.cursor()
    cursor.execute("SELECT not_id, baslik FROM notlar WHERE kullanici_id = ? ORDER BY not_id DESC",
                   (kullanici_id,))
    notlar = cursor.fetchall()
    conn.close()
    return notlar


def not_detay_getir(not_id):
    """Tek bir notun tüm içeriğini getirir."""
    conn = sqlite3.connect('kullanicilar.db')
    cursor = conn.cursor()
    cursor.execute("SELECT baslik, icerik FROM notlar WHERE not_id = ?", (not_id,))
    detay = cursor.fetchone()
    conn.close()
    return detay


def not_ekle(kullanici_id, baslik, icerik):
    """Yeni bir not ekler."""
    conn = sqlite3.connect('kullanicilar.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notlar (baslik, icerik, kullanici_id) VALUES (?, ?, ?)",
                   (baslik, icerik, kullanici_id))
    conn.commit()
    conn.close()


def not_sil(not_id):
    """Belirli bir notu siler."""
    conn = sqlite3.connect('kullanicilar.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notlar WHERE not_id = ?", (not_id,))
    conn.commit()
    conn.close()


def not_guncelle(not_id, baslik, icerik):
    """Belirli bir notu günceller."""
    conn = sqlite3.connect('kullanicilar.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE notlar SET baslik = ?, icerik = ? WHERE not_id = ?",
                   (baslik, icerik, not_id))
    conn.commit()
    conn.close()