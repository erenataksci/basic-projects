import sys
import requests  # API istekleri için import ekledik
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QListWidget, QListWidgetItem, QTextEdit, QLineEdit, QPushButton,
                             QSplitter, QMessageBox)
from PyQt6.QtCore import Qt

# API sunucumuzun adresi (main.py'deki ile aynı olmalı)
API_URL = "http://127.0.0.1:5000"


class NotepadWindow(QWidget):
    # Artık sqlite_id yerine firebase_id alıyoruz
    def __init__(self, aktif_kullanici_firebase_id):
        super().__init__()

        # Kullanıcının benzersiz Firebase ID'sini saklıyoruz
        self.kullanici_firebase_id = aktif_kullanici_firebase_id
        # Seçili olan notun Firebase tarafından atanmış ID'sini saklayacağız
        self.mevcut_secili_not_firebase_id = None

        self.initUI()
        self.not_listesini_yenile()

    def initUI(self):
        # Arayüzün görsel kısmı (butonlar, listeler vb.) aynı kalıyor
        self.setWindowTitle('Güvenli Not Defteri (Online)')
        self.setGeometry(200, 200, 700, 500)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        sol_panel = QWidget()
        sol_layout = QVBoxLayout()
        sol_panel.setLayout(sol_layout)

        self.not_listesi_widget = QListWidget()
        self.not_listesi_widget.itemClicked.connect(self.listeden_not_sec)

        sol_layout.addWidget(QLabel("Not Başlıkları:"))
        sol_layout.addWidget(self.not_listesi_widget)

        sag_panel = QWidget()
        sag_layout = QVBoxLayout()
        sag_panel.setLayout(sag_layout)

        self.baslik_input = QLineEdit()
        self.baslik_input.setPlaceholderText("Not Başlığı...")

        self.icerik_input = QTextEdit()
        self.icerik_input.setPlaceholderText("Notunuzu buraya yazın...")

        buton_layout = QHBoxLayout()
        self.yeni_not_btn = QPushButton("Yeni Not")
        self.yeni_not_btn.clicked.connect(self.yeni_not_arayuzu)

        self.kaydet_btn = QPushButton("Kaydet")
        self.kaydet_btn.clicked.connect(self.notu_kaydet)

        self.sil_btn = QPushButton("Sil")
        self.sil_btn.clicked.connect(self.notu_sil)

        buton_layout.addWidget(self.yeni_not_btn)
        buton_layout.addWidget(self.kaydet_btn)
        buton_layout.addWidget(self.sil_btn)

        sag_layout.addWidget(QLabel("Detay:"))
        sag_layout.addWidget(self.baslik_input)
        sag_layout.addWidget(self.icerik_input)
        sag_layout.addLayout(buton_layout)

        splitter.addWidget(sol_panel)
        splitter.addWidget(sag_panel)
        splitter.setSizes([200, 500])

        ana_layout = QHBoxLayout()
        ana_layout.addWidget(splitter)
        self.setLayout(ana_layout)

    # === VERİTABANI İŞLEMLERİ ARTIK API İSTEKLERİNE DÖNÜŞTÜ ===

    def not_listesini_yenile(self):
        """API'den notları çeker ve sol listeyi günceller."""
        self.not_listesi_widget.clear()
        try:
            # API'ye GET isteği: /notlar/{kullanici_firebase_id}
            response = requests.get(f"{API_URL}/notlar/{self.kullanici_firebase_id}", timeout=5)

            if response.status_code == 200:
                # Sunucudan gelen notlar {firebase_not_id: {'baslik': '...'}, ...} formatında
                notlar_dict = response.json().get("notlar", {})

                # Sözlüğü listeye ekleyelim (Firebase ID'yi de alarak)
                for not_fb_id, not_verisi in notlar_dict.items():
                    baslik = not_verisi.get("baslik", "Başlıksız")
                    item = QListWidgetItem(baslik)
                    # Saklı veri olarak artık Firebase not ID'sini kullanıyoruz
                    item.setData(Qt.ItemDataRole.UserRole, not_fb_id)
                    self.not_listesi_widget.addItem(item)
            else:
                QMessageBox.warning(self, "Hata",
                                    f"Notlar alınamadı: {response.json().get('hata', 'Bilinmeyen API hatası')}")

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Bağlantı Hatası", f"API Sunucusuna bağlanılamadı: {e}")

    def listeden_not_sec(self, item):
        """Listedeki bir nota tıklandığında API'den detayını çeker."""
        self.mevcut_secili_not_firebase_id = item.data(Qt.ItemDataRole.UserRole)

        if not self.mevcut_secili_not_firebase_id: return

        try:
            # API'ye GET isteği: /not/{firebase_not_id}
            response = requests.get(f"{API_URL}/not/{self.mevcut_secili_not_firebase_id}", timeout=5)

            if response.status_code == 200:
                detay = response.json().get("not")
                if detay:
                    self.baslik_input.setText(detay.get("baslik", ""))
                    self.icerik_input.setText(detay.get("icerik", ""))
            else:
                QMessageBox.warning(self, "Hata",
                                    f"Not detayı alınamadı: {response.json().get('hata', 'Bilinmeyen API hatası')}")

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Bağlantı Hatası", f"API Sunucusuna bağlanılamadı: {e}")

    def yeni_not_arayuzu(self):
        """Sağdaki alanları temizler."""
        self.mevcut_secili_not_firebase_id = None
        self.baslik_input.clear()
        self.icerik_input.clear()
        self.baslik_input.setFocus()

    def notu_kaydet(self):
        """Yeni notu API'ye gönderir veya mevcut notu günceller."""
        baslik = self.baslik_input.text().strip()
        icerik = self.icerik_input.toPlainText().strip()

        if not baslik:
            QMessageBox.warning(self, "Hata", "Not başlığı boş olamaz!")
            return

        # API'ye gönderilecek veri
        not_verisi = {
            "baslik": baslik,
            "icerik": icerik,
            "kullanici_id": self.kullanici_firebase_id  # Hangi kullanıcıya ait olduğu bilgisi
        }

        try:
            if self.mevcut_secili_not_firebase_id is None:
                # YENİ NOT EKLEME: POST isteği /notlar
                response = requests.post(f"{API_URL}/notlar", json=not_verisi, timeout=10)
                if response.status_code == 201:
                    self.yeni_not_arayuzu()  # Başarılıysa alanları temizle
                else:
                    QMessageBox.warning(self, "Hata",
                                        f"Not kaydedilemedi: {response.json().get('hata', 'Bilinmeyen API hatası')}")
            else:
                # NOT GÜNCELLEME: PUT isteği /not/{firebase_not_id}
                response = requests.put(f"{API_URL}/not/{self.mevcut_secili_not_firebase_id}", json=not_verisi,
                                        timeout=10)
                if response.status_code != 200:
                    QMessageBox.warning(self, "Hata",
                                        f"Not güncellenemedi: {response.json().get('hata', 'Bilinmeyen API hatası')}")

            # Her iki durumda da (başarılı/başarısız fark etmez) listeyi yenilemeye çalış
            self.not_listesini_yenile()

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Bağlantı Hatası", f"API Sunucusuna bağlanılamadı: {e}")

    def notu_sil(self):
        """Seçili olan notu API üzerinden siler."""
        if self.mevcut_secili_not_firebase_id is None:
            QMessageBox.warning(self, "Hata", "Silmek için bir not seçmelisiniz.")
            return

        cevap = QMessageBox.question(self, "Onay",
                                     "Bu notu silmek istediğinize emin misiniz?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if cevap == QMessageBox.StandardButton.Yes:
            try:
                # NOT SİLME: DELETE isteği /not/{firebase_not_id}
                response = requests.delete(f"{API_URL}/not/{self.mevcut_secili_not_firebase_id}", timeout=10)

                if response.status_code == 200:
                    self.yeni_not_arayuzu()
                    self.not_listesini_yenile()
                else:
                    QMessageBox.warning(self, "Hata",
                                        f"Not silinemedi: {response.json().get('hata', 'Bilinmeyen API hatası')}")

            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Bağlantı Hatası", f"API Sunucusuna bağlanılamadı: {e}")


# Bu dosya doğrudan çalıştırılırsa bir şey yapmasın diye kontrol
if __name__ == '__main__':
    print("Bu dosya ana program değildir. Lütfen main.py dosyasını çalıştırın.")