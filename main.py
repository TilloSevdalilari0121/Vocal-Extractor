"""
Vocal Extractor Pro — Giriş Noktası
Çalıştır: python main.py
Önce kurul: pip install -r requirements.txt
"""
import sys
import os

# onnxruntime PyQt6'dan ÖNCE yüklenmeli!
# DirectML DLL'leri Qt DLL'leriyle çakışıyor.
try:
    import onnxruntime as _ort_preload
    print(f"[onnxruntime] {_ort_preload.__version__} — "
          f"providers: {_ort_preload.get_available_providers()}")
except Exception as _e:
    print(f"[onnxruntime preload hata] {_e}")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from app import database
database.init_db()
database.start_session()

from app.window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Vocal Extractor Pro")
    app.setApplicationVersion("2.0")
    app.setQuitOnLastWindowClosed(False)   # tray modunda pencere kapanınca çıkmasın

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    win = MainWindow()
    win.show()

    code = app.exec()

    # Temiz çıkış
    database.end_session()
    os._exit(code)   # QThread'ler dahil tüm thread'leri zorla sonlandır


if __name__ == "__main__":
    main()
