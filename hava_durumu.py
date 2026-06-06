import sys
import os # Bu import'u ekle
import json
import requests
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QGridLayout, QLabel,
                             QComboBox, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

# === YENİ HELPER FONKSİYONU ===
def resource_path(relative_path):
    """
    Paketlenmiş uygulamada ve normal modda dosya yolunu doğru şekilde alır.
    """
    try:
        # PyInstaller geçici bir klasör oluşturur ve yolu _MEIPASS'ta saklar
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# === YENİ FONKSİYON: API İÇİN METNİ TEMİZLE ===
def sanitize_for_api(text):
    """
    Türkçe karakterleri API'nin daha iyi anlayabileceği
    İngilizce karşılıkları ile değiştirir.
    """
    return text.replace('ğ', 'g').replace('Ğ', 'G') \
        .replace('ü', 'u').replace('Ü', 'U') \
        .replace('ş', 's').replace('Ş', 'S') \
        .replace('ı', 'i').replace('İ', 'I') \
        .replace('ö', 'o').replace('Ö', 'O') \
        .replace('ç', 'c').replace('Ç', 'C')


# --- API FONKSİYONUNDA DEĞİŞİKLİK YOK ---
def get_weather(location_query):
    # ... (Bu fonksiyon tamamen aynı kalıyor)
    API_KEY = "89989ca2a9ce30f18b4faf4939f94b8a"
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    # ... (geri kalanı aynı)
    try:
        response = requests.get(BASE_URL,
                                params={"q": location_query, "appid": API_KEY, "units": "metric", "lang": "tr"},
                                proxies={"http": None, "https": None}, timeout=10)
        response.raise_for_status()
        data = response.json()
        weather_data = {
            "yer_adi": data.get('name', location_query.split(',')[0]),  # Sorgudaki temiz adı kullan
            "sicaklik": int(data['main']['temp']),
            "hissedilen": int(data['main']['feels_like']),
            "nem": data['main']['humidity'],
            "aciklama": data['weather'][0]['description'].capitalize(),
            "ikon_kodu": data['weather'][0]['icon']
        }
        return weather_data
    except requests.exceptions.HTTPError:
        return {"hata": "Konum bulunamadı veya geçersiz."}
    except requests.exceptions.RequestException:
        return {"hata": "Ağ bağlantısı sorunu."}


class WeatherApp(QWidget):
    # ... (__init__, load_city_data, initUI, update_districts metodları aynı) ...
    def __init__(self):
        super().__init__()
        self.load_city_data()
        self.initUI()

    def load_city_data(self):
        try:
            with open('il-ilce.json', 'r', encoding='utf-8') as f:
                data_list = json.load(f)
                self.city_data = {}
                for item in data_list:
                    city = item['sehir_adi']
                    district = item['ilce_adi']
                    if city not in self.city_data:
                        self.city_data[city] = []
                    self.city_data[city].append(district)
                for city in self.city_data:
                    self.city_data[city].sort()
        except (FileNotFoundError, KeyError):
            self.city_data = {"Hata": ["Veri dosyası hatalı!"]}

    def initUI(self):
        self.setWindowTitle('Hava Durumu')
        self.setGeometry(300, 300, 450, 450)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        top_layout = QGridLayout()
        top_layout.setSpacing(10)
        self.city_combo = QComboBox()
        self.district_combo = QComboBox()
        self.button = QPushButton('Hava Durumunu Getir')
        top_layout.addWidget(QLabel("İl Seçin:"), 0, 0)
        top_layout.addWidget(self.city_combo, 0, 1)
        top_layout.addWidget(QLabel("İlçe Seçin:"), 1, 0)
        top_layout.addWidget(self.district_combo, 1, 1)
        top_layout.addWidget(self.button, 2, 0, 1, 2)
        self.icon_label = QLabel()
        self.location_label = QLabel("Lütfen bir konum seçin")
        self.temp_label = QLabel("--°C")
        self.desc_label = QLabel("...")
        self.details_label = QLabel("")
        self.main_layout.addLayout(top_layout)
        self.main_layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.location_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.temp_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.desc_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.details_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addStretch()
        self.city_combo.addItems(sorted(self.city_data.keys()))
        self.city_combo.currentIndexChanged.connect(self.update_districts)
        self.button.clicked.connect(self.display_weather)
        self.update_districts()

    def update_districts(self):
        selected_city = self.city_combo.currentText()
        if selected_city in self.city_data:
            self.district_combo.clear()
            self.district_combo.addItems(self.city_data[selected_city])

    # === BU METOD GÜNCELLENDİ ===
    def display_weather(self):
        city = self.city_combo.currentText()
        district = self.district_combo.currentText()

        # 1. API'ye göndermeden önce ilçe adını temizle
        sanitized_district = sanitize_for_api(district)

        # 2. Sorguyu temizlenmiş veri ile oluştur
        location_query = f"{sanitized_district},{city},TR"

        self.desc_label.setText(f"'{district}' için veri alınıyor...")  # Arayüzde hala orijinal adı göster
        self.temp_label.setText("")
        self.location_label.setText("")
        self.details_label.setText("")
        self.icon_label.clear()

        weather_data = get_weather(location_query)

        if "hata" in weather_data:
            self.desc_label.setText(weather_data["hata"])
            return

        # API'den gelen yer adı bazen temizlenmiş adı (Bagcilar gibi) döndürebilir.
        # Bu yüzden biz arayüzde kullanıcının seçtiği orijinal adı gösterelim.
        self.location_label.setText(f"📍 {district}, {city}")
        self.temp_label.setText(f"{weather_data['sicaklik']}°C")
        self.desc_label.setText(weather_data['aciklama'])
        self.details_label.setText(f"Hissedilen: {weather_data['hissedilen']}°C  |  Nem: %{weather_data['nem']}")

        icon_path = self.get_icon_path(weather_data['ikon_kodu'])
        pixmap = QPixmap(icon_path)
        self.icon_label.setPixmap(pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio))

    def get_icon_path(self, icon_code):
        if "01" in icon_code: return "icons/clear.png"
        if "02" in icon_code: return "icons/few_clouds.png"
        if "03" in icon_code or "04" in icon_code: return "icons/clouds.png"
        if "09" in icon_code or "10" in icon_code: return "icons/rain.png"
        if "11" in icon_code: return "icons/thunderstorm.png"
        if "13" in icon_code: return "icons/snow.png"
        if "50" in icon_code: return "icons/mist.png"
        return "icons/unknown.png"


# ... (STYLESHEET ve if __name__ == '__main__': bloğu aynı) ...
STYLESHEET = """
QWidget {
    background-color: #2E3440;
    color: #ECEFF4;
    font-family: Helvetica;
}
QComboBox {
    border: 1px solid #4C566A;
    border-radius: 4px;
    padding: 5px;
    background-color: #3B4252;
}
QComboBox::drop-down {
    border: none;
}
QPushButton {
    background-color: #5E81AC;
    color: #ECEFF4;
    border: none;
    padding: 10px;
    border-radius: 5px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #81A1C1;
}
QLabel {
    background-color: transparent;
}
#location_label {
    font-size: 24px;
    font-weight: bold;
}
#temp_label {
    font-size: 48px;
    font-weight: bold;
    color: #88C0D0;
}
#desc_label {
    font-size: 16px;
    font-style: italic;
    color: #D8DEE9;
}
"""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    ex = WeatherApp()
    ex.location_label.setObjectName("location_label")
    ex.temp_label.setObjectName("temp_label")
    ex.desc_label.setObjectName("desc_label")
    ex.show()
    sys.exit(app.exec())