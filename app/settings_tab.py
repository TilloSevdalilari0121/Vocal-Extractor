"""
Ayarlar sekmesi — artık SQLite DB üzerinden çalışır.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QScrollArea, QFrame, QCheckBox,
)
from PyQt6.QtCore import pyqtSignal

from app import database
from app.widgets import h_line, section_label
from app.themes  import THEMES


class ToggleRow(QWidget):
    def __init__(self, label: str, sub: str, checked: bool, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 8, 0, 8)
        col = QVBoxLayout()
        col.setSpacing(2)
        col.addWidget(QLabel(label))
        s = QLabel(sub)
        s.setObjectName("jobSub")
        col.addWidget(s)
        lay.addLayout(col, 1)
        self.chk = QCheckBox()
        self.chk.setChecked(checked)
        lay.addWidget(self.chk)

    def is_checked(self) -> bool:
        return self.chk.isChecked()


class SettingsTab(QWidget):
    theme_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    # ── DB yardımcıları ───────────────────────────────────────────────────────
    @staticmethod
    def _get(key: str, default: str = "") -> str:
        return database.get_setting(key, default)

    @staticmethod
    def _set(key: str, value: str):
        database.set_setting(key, value)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        inner = QWidget()
        inner.setObjectName("panelBg")
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(32, 24, 32, 24)
        lay.setSpacing(20)

        # ── Tema ──────────────────────────────────────────────────────────────
        lay.addWidget(section_label("🎨 Tema"))
        self._theme_cb = QComboBox()
        self._theme_cb.addItems(list(THEMES.keys()))
        self._theme_cb.setCurrentText(
            self._get("theme", "Tahoe Dark"))
        self._theme_cb.currentTextChanged.connect(self.theme_changed.emit)
        lay.addWidget(self._theme_cb)
        lay.addWidget(h_line())

        # ── Yapay Zeka ────────────────────────────────────────────────────────
        lay.addWidget(section_label("🧠 Yapay Zeka & İşlem"))
        self._gpu = ToggleRow(
            "GPU Hızlandırma (DirectML / CUDA)",
            "AMD / Intel / NVIDIA ekran kartı varsa etkinleştir",
            self._get("gpu", "1") == "1")
        lay.addWidget(self._gpu)
        lay.addWidget(h_line())

        par_row = QHBoxLayout()
        par_col = QVBoxLayout()
        par_col.addWidget(QLabel("Paralel İşlem"))
        ps = QLabel("Aynı anda kaç iş çalışsın")
        ps.setObjectName("jobSub")
        par_col.addWidget(ps)
        par_row.addLayout(par_col, 1)
        self._parallel = QComboBox()
        self._parallel.addItems(["1", "2", "3"])
        self._parallel.setCurrentText(self._get("parallel", "1"))
        self._parallel.setFixedWidth(80)
        par_row.addWidget(self._parallel)
        lay.addLayout(par_row)
        lay.addWidget(h_line())

        # ── Varsayılanlar ─────────────────────────────────────────────────────
        lay.addWidget(section_label("⚙ Varsayılan Ayarlar"))
        f_row = QHBoxLayout()
        fl = QVBoxLayout()
        fl.addWidget(QLabel("Varsayılan Çıktı Formatı"))
        fs = QLabel("İndirme ve temizleme için varsayılan çıktı formatı")
        fs.setObjectName("jobSub")
        fl.addWidget(fs)
        f_row.addLayout(fl, 1)
        self._def_fmt = QComboBox()
        self._def_fmt.addItems(["MP3", "WAV", "FLAC"])
        self._def_fmt.setCurrentText(self._get("default_fmt", "MP3"))
        self._def_fmt.setFixedWidth(100)
        f_row.addWidget(self._def_fmt)
        lay.addLayout(f_row)
        lay.addWidget(h_line())

        # ── Bildirimler ───────────────────────────────────────────────────────
        lay.addWidget(section_label("🔔 Bildirimler"))
        self._tray = ToggleRow(
            "Sistem Tepsisi İkonu",
            "Arka planda çalış, kapatılmasın",
            self._get("tray", "1") == "1")
        lay.addWidget(self._tray)
        lay.addWidget(h_line())
        self._notify = ToggleRow(
            "Masaüstü Bildirimi",
            "İşlem bitince Windows bildirimi gönder",
            self._get("notify", "1") == "1")
        lay.addWidget(self._notify)
        lay.addWidget(h_line())

        # ── Geçmiş ────────────────────────────────────────────────────────────
        lay.addWidget(section_label("🕒 Geçmiş"))
        self._hist = ToggleRow(
            "Geçmiş Kaydı",
            "Tamamlanan işleri Geçmiş sekmesinde listele",
            self._get("save_history", "1") == "1")
        lay.addWidget(self._hist)
        lay.addWidget(h_line())

        # ── DB yolu ───────────────────────────────────────────────────────────
        lay.addWidget(section_label("🗄 Veritabanı"))
        db_lbl = QLabel(f"Konum: {database.DB_PATH}")
        db_lbl.setObjectName("jobSub")
        db_lbl.setWordWrap(True)
        lay.addWidget(db_lbl)

        lay.addStretch()

        save_btn = QPushButton("💾  Ayarları Kaydet")
        save_btn.setObjectName("primaryBtn")
        save_btn.setFixedHeight(44)
        save_btn.clicked.connect(self._save)
        lay.addWidget(save_btn)

        scroll.setWidget(inner)
        root.addWidget(scroll)

    def set_theme_silent(self, name: str):
        self._theme_cb.blockSignals(True)
        self._theme_cb.setCurrentText(name)
        self._theme_cb.blockSignals(False)

    def _save(self):
        self._set("gpu",          "1" if self._gpu.is_checked() else "0")
        self._set("parallel",     self._parallel.currentText())
        self._set("tray",         "1" if self._tray.is_checked() else "0")
        self._set("notify",       "1" if self._notify.is_checked() else "0")
        self._set("save_history", "1" if self._hist.is_checked() else "0")
        self._set("default_fmt",  self._def_fmt.currentText())
        self._set("theme",        self._theme_cb.currentText())

        # Kaydet bilgisi için anlık mesaj
        self._theme_cb.setToolTip("✓ Kaydedildi")

    def current_theme(self) -> str:
        return self._theme_cb.currentText()
