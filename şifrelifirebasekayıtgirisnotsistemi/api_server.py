import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, request, jsonify
import hashlib
import os  # serviceAccountKey dosyasının varlığını kontrol etmek için

# --- Firebase Admin SDK Başlatma ---
SERVICE_ACCOUNT_KEY_PATH = "serviceAccountKey.json"
DATABASE_URL = 'https://pythonsistem-default-rtdb.europe-west1.firebasedatabase.app/'  # KENDİ URL'Nİ YAPIŞTIR!

# Anahtar dosyasının var olup olmadığını kontrol et
if not os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
    print(f"HATA: Firebase servis anahtarı dosyası bulunamadı: '{SERVICE_ACCOUNT_KEY_PATH}'")
    print("Lütfen Firebase konsolundan indirdiğiniz .json dosyasını bu isimle proje klasörüne kaydedin.")
    exit()

if 'SENIN_FIREBASE_DATABASE_URL_BURAYA' in DATABASE_URL:
    print(
        f"HATA: Lütfen api_server.py dosyasındaki DATABASE_URL değişkenini kendi Firebase Realtime Database URL'niz ile güncelleyin.")
    exit()

try:
    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
    firebase_admin.initialize_app(cred, {
        'databaseURL': DATABASE_URL
    })
    print("Firebase Admin SDK başarıyla başlatıldı.")
except Exception as e:
    print(f"Firebase Admin SDK başlatılırken HATA oluştu: {e}")
    exit()

# --- Flask Uygulamasını Başlatma ---
app = Flask(__name__)


# --- Helper Fonksiyon: Parola Hashleme ---
def hash_parola(parola):
    return hashlib.sha256(parola.encode('utf-8')).hexdigest()


# --- API Endpoint'leri (Rotalar) ---

# Test Endpoint'i
@app.route('/test', methods=['GET'])
def test_connection():
    return jsonify({"mesaj": "API Sunucusu çalışıyor!"}), 200


# === KAYIT OL ENDPOINT (DEBUG PRINT'LERİ EKLENDİ) ===
@app.route('/kayit-ol', methods=['POST'])
def kayit_ol():
    gelen_veri = request.get_json()
    print(f"\n[/kayit-ol] Gelen Veri: {gelen_veri}") # Ne geldiğini gör

    if not gelen_veri or 'kullanici_adi' not in gelen_veri or 'parola' not in gelen_veri:
        print("[/kayit-ol] Hata: Eksik bilgi.")
        return jsonify({"hata": "Eksik bilgi (kullanici_adi, parola)."}), 400

    kullanici_adi = gelen_veri['kullanici_adi'].strip()
    parola = gelen_veri['parola'].strip()
    print(f"[/kayit-ol] Alınan Kullanıcı Adı: {kullanici_adi}, Parola: {parola}")

    if not kullanici_adi or not parola:
        print("[/kayit-ol] Hata: Kullanıcı adı veya parola boş.")
        return jsonify({"hata": "Kullanıcı adı veya parola boş olamaz."}), 400

    ref = db.reference('kullanicilar')
    print(f"[/kayit-ol] Firebase referansı alındı: {ref.path}")

    try:
        mevcut_kullanici = ref.order_by_child('kullanici_adi').equal_to(kullanici_adi).get()
        print(f"[/kayit-ol] Mevcut kullanıcı sorgu sonucu: {mevcut_kullanici}")

        if mevcut_kullanici:
            print(f"[/kayit-ol] Hata: Kullanıcı adı zaten var.")
            return jsonify({"hata": f"'{kullanici_adi}' kullanıcı adı zaten alınmış."}), 409

        hashed_parola = hash_parola(parola)
        print(f"[/kayit-ol] Parola hash'lendi: {hashed_parola}")

        yeni_kullanici_verisi = {
            'kullanici_adi': kullanici_adi,
            'parola_hash': hashed_parola
        }
        print(f"[/kayit-ol] Kaydedilecek veri: {yeni_kullanici_verisi}")

        # === KRİTİK NOKTA ===
        print("[/kayit-ol] Firebase'e push işlemi deneniyor...")
        yeni_kullanici_ref = ref.push(yeni_kullanici_verisi)
        print(f"[/kayit-ol] Firebase push işlemi tamamlandı. Yeni ID: {yeni_kullanici_ref.key}")
        # =====================

        return jsonify({"mesaj": f"'{kullanici_adi}' başarıyla kaydedildi."}), 201

    except Exception as e:
        # Eğer push işlemi sırasında bir hata olursa buraya düşer
        print(f"[/kayit-ol] !!! Firebase'e yazarken KRİTİK HATA: {e}")
        return jsonify({"hata": "Sunucu hatası (kayıt)."}), 500


# Kullanıcı Giriş Endpoint'i
@app.route('/giris-yap', methods=['POST'])
def giris_yap():
    gelen_veri = request.get_json()
    if not gelen_veri or 'kullanici_adi' not in gelen_veri or 'parola' not in gelen_veri:
        return jsonify({"hata": "Eksik bilgi."}), 400

    kullanici_adi = gelen_veri['kullanici_adi']
    parola = gelen_veri['parola']

    ref = db.reference('kullanicilar')
    kullanicilar = ref.order_by_child('kullanici_adi').equal_to(kullanici_adi).get()

    if not kullanicilar:
        print(f"Giriş denemesi başarısız (Kullanıcı bulunamadı): {kullanici_adi}")
        return jsonify({"hata": "Kullanıcı adı veya parola yanlış."}), 401

    try:
        # Firebase'den dönen {firebase_id: kullanici_verisi} yapısından ID ve veriyi al
        firebase_id = next(iter(kullanicilar))
        kullanici_verisi = kullanicilar[firebase_id]

        kayitli_hash = kullanici_verisi.get('parola_hash')
        girilen_hash = hash_parola(parola)

        if kayitli_hash == girilen_hash:
            print(f"Giriş başarılı: {kullanici_adi} (ID: {firebase_id})")
            return jsonify({"mesaj": "Giriş başarılı.", "firebase_id": firebase_id}), 200
        else:
            print(f"Giriş denemesi başarısız (Hatalı parola): {kullanici_adi}")
            return jsonify({"hata": "Kullanıcı adı veya parola yanlış."}), 401
    except StopIteration:
        # Bu durum normalde oluşmamalı ama güvenlik için ekleyelim
        print(f"Giriş denemesi kritik hata (veri yapısı bozuk?): {kullanici_adi}")
        return jsonify({"hata": "Kullanıcı adı veya parola yanlış."}), 401
    except Exception as e:
        print(f"Giriş sırasında sunucu hatası: {e}")
        return jsonify({"hata": "Sunucu hatası (giriş)."}), 500


# === NOT ENDPOINT'LERİ ===

# Kullanıcının Tüm Notlarını Getir
@app.route('/notlar/<kullanici_firebase_id>', methods=['GET'])
def kullanici_notlarini_getir(kullanici_firebase_id):
    """Belirli bir kullanıcıya ait tüm notları getirir."""
    try:
        ref = db.reference('notlar')
        # Notları kullanici_id'ye göre filtrele
        kullanici_notlari = ref.order_by_child('kullanici_id').equal_to(kullanici_firebase_id).get()

        if kullanici_notlari:
            # Firebase sadece notların verisini döndürür, ID'leri anahtar olarak verir.
            # İstemciye hem ID hem başlık lazım olduğu için formatlayalım.
            # {firebase_not_id: {'baslik': '...', 'icerik': '...', 'kullanici_id': '...'}, ...}
            print(f"Kullanıcı {kullanici_firebase_id} için {len(kullanici_notlari)} not bulundu.")
            return jsonify({"notlar": kullanici_notlari}), 200
        else:
            print(f"Kullanıcı {kullanici_firebase_id} için not bulunamadı.")
            return jsonify({"notlar": {}}), 200  # Boş not listesi için hata verme
    except Exception as e:
        print(f"Notları getirirken hata: {e}")
        return jsonify({"hata": "Sunucu hatası (not listesi)."}), 500


# Tek Bir Notun Detayını Getir
@app.route('/not/<not_firebase_id>', methods=['GET'])
def not_detayi_getir(not_firebase_id):
    """Firebase ID'si verilen tek bir notun detayını getirir."""
    try:
        ref = db.reference(f'notlar/{not_firebase_id}')  # Doğrudan nota ID ile eriş
        not_verisi = ref.get()
        if not_verisi:
            return jsonify({"not": not_verisi}), 200
        else:
            return jsonify({"hata": "Not bulunamadı."}), 404  # 404 Not Found
    except Exception as e:
        print(f"Not detayı getirirken hata: {e}")
        return jsonify({"hata": "Sunucu hatası (not detayı)."}), 500


# Yeni Not Ekle
@app.route('/notlar', methods=['POST'])
def yeni_not_ekle():
    """Yeni bir notu veritabanına ekler."""
    gelen_veri = request.get_json()
    if not gelen_veri or 'baslik' not in gelen_veri or 'icerik' not in gelen_veri or 'kullanici_id' not in gelen_veri:
        return jsonify({"hata": "Eksik bilgi (baslik, icerik, kullanici_id)."}), 400

    baslik = gelen_veri['baslik'].strip()
    kullanici_id = gelen_veri['kullanici_id']  # Bu, kullanıcının Firebase ID'si olmalı

    if not baslik:
        return jsonify({"hata": "Başlık boş olamaz."}), 400
    if not kullanici_id:
        return jsonify({"hata": "Kullanıcı ID'si eksik."}), 400

    yeni_not_verisi = {
        'baslik': baslik,
        'icerik': gelen_veri.get('icerik', ''),  # İçerik boş olabilir
        'kullanici_id': kullanici_id
        # İleride buraya oluşturma/güncelleme tarihi de eklenebilir
    }

    try:
        ref = db.reference('notlar')
        yeni_not_ref = ref.push(yeni_not_verisi)
        print(f"Yeni not eklendi (ID: {yeni_not_ref.key})")
        # İstemciye yeni notun ID'sini döndürebiliriz
        return jsonify({"mesaj": "Not başarıyla eklendi.", "not_id": yeni_not_ref.key}), 201
    except Exception as e:
        print(f"Yeni not eklerken hata: {e}")
        return jsonify({"hata": "Sunucu hatası (not ekleme)."}), 500


# Not Güncelle
@app.route('/not/<not_firebase_id>', methods=['PUT'])
def notu_guncelle(not_firebase_id):
    """Mevcut bir notu günceller."""
    gelen_veri = request.get_json()
    if not gelen_veri or 'baslik' not in gelen_veri or 'icerik' not in gelen_veri:
        # kullanici_id güncellemede gelmeyebilir, sadece içeriği güncelliyoruz
        return jsonify({"hata": "Eksik bilgi (baslik, icerik)."}), 400

    baslik = gelen_veri['baslik'].strip()
    if not baslik:
        return jsonify({"hata": "Başlık boş olamaz."}), 400

    guncellenecek_veri = {
        'baslik': baslik,
        'icerik': gelen_veri.get('icerik', '')
        # kullanici_id'yi güncellemiyoruz, notun sahibi değişmez
    }

    try:
        ref = db.reference(f'notlar/{not_firebase_id}')
        # update() metodu sadece belirtilen alanları günceller
        ref.update(guncellenecek_veri)
        print(f"Not güncellendi (ID: {not_firebase_id})")
        return jsonify({"mesaj": "Not başarıyla güncellendi."}), 200
    except Exception as e:
        print(f"Not güncellerken hata: {e}")
        return jsonify({"hata": "Sunucu hatası (not güncelleme)."}), 500


# Not Sil
@app.route('/not/<not_firebase_id>', methods=['DELETE'])
def notu_sil(not_firebase_id):
    """Bir notu veritabanından siler."""
    try:
        ref = db.reference(f'notlar/{not_firebase_id}')
        # set(None) veya delete() metodu Firebase'de bir kaydı siler
        ref.delete()
        print(f"Not silindi (ID: {not_firebase_id})")
        return jsonify({"mesaj": "Not başarıyla silindi."}), 200
    except Exception as e:
        print(f"Not silerken hata: {e}")
        return jsonify({"hata": "Sunucu hatası (not silme)."}), 500


# --- Sunucuyu Başlatma ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)