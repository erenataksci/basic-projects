import sys
import veritabani as db
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QListWidget, QListWidgetItem, QTextEdit, QLineEdit, QPushButton, # <-- QListWidgetItem eklendi
                             QSplitter, QMessageBox)
from PyQt6.QtCore import Qt


class NotepadWindow(QWidget):
    def __init__(self, kullanici_id):
        super().__init__()

        self.kullanici_id = kullanici_id
        self.mevcut_secili_not_id = None

        self.initUI()
        self.not_listesini_yenile()

    def initUI(self):
        self.setWindowTitle('Güvenli Not Defteri')
        self.setGeometry(200, 200, 700, 500)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- SOL TARAF (Not Listesi) ---
        sol_panel = QWidget()
        sol_layout = QVBoxLayout()
        sol_panel.setLayout(sol_layout)

        self.not_listesi_widget = QListWidget()
        self.not_listesi_widget.itemClicked.connect(self.listeden_not_sec)

        sol_layout.addWidget(QLabel("Not Başlıkları:"))
        sol_layout.addWidget(self.not_listesi_widget)

        # --- SAĞ TARAF (Not İçeriği) ---
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

    def not_listesini_yenile(self):
        """Veritabanından notları çeker ve sol listeyi günceller."""
        self.not_listesi_widget.clear()
        notlar = db.notlari_getir(self.kullanici_id)

        for not_id, baslik in notlar:
            # --- DOĞRU MANTIK ---
            # 1. Önce QListWidgetItem nesnesini oluştur:
            item = QListWidgetItem(baslik)
            # 2. Oluşturduğun nesnenin verisini ayarla:
            item.setData(Qt.ItemDataRole.UserRole, not_id)
            # 3. Hazır olan nesneyi listeye ekle:
            self.not_listesi_widget.addItem(item)
            # --------------------

    def listeden_not_sec(self, item):
        """Listedeki bir nota tıklandığında sağ tarafı doldurur."""
        # DOĞRU METOD: 'data' (Büyük 'D' ile)
        self.mevcut_secili_not_id = item.data(Qt.ItemDataRole.UserRole)

        detay = db.not_detay_getir(self.mevcut_secili_not_id)
        if detay:
            baslik, icerik = detay
            self.baslik_input.setText(baslik)
            self.icerik_input.setText(icerik)

    def yeni_not_arayuzu(self):
        """Sağdaki alanları temizler ve yeni not girişi için hazırlar."""
        self.mevcut_secili_not_id = None
        self.baslik_input.clear()
        self.icerik_input.clear()
        self.baslik_input.setFocus()

    def notu_kaydet(self):
        """Yeni notu veya mevcut notu günceller."""
        baslik = self.baslik_input.text().strip()
        icerik = self.icerik_input.toPlainText().strip()

        if not baslik:
            QMessageBox.warning(self, "Hata", "Not başlığı boş olamaz!")
            return

        if self.mevcut_secili_not_id is None:
            db.not_ekle(self.kullanici_id, baslik, icerik)
            self.yeni_not_arayuzu()
        else:
            db.not_guncelle(self.mevcut_secili_not_id, baslik, icerik)

        self.not_listesini_yenile()

    def notu_sil(self):
        """Seçili olan notu siler."""
        if self.mevcut_secili_not_id is None:
            QMessageBox.warning(self, "Hata", "Silmek için bir not seçmelisiniz.")
            return

        cevap = QMessageBox.question(self, "Onay",
                                     "Bu notu silmek istediğinize emin misiniz?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if cevap == QMessageBox.StandardButton.Yes:
            db.not_sil(self.mevcut_secili_not_id)
            self.yeni_not_arayuzu()
            self.not_listesini_yenile()