"""
Geçmiş sekmesi — SQLite DB üzerinden çalışır.
"""
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout, QComboBox,
)
from PyQt6.QtCore import Qt

from app import database
from app.widgets import section_label


class HistoryCard(QWidget):
    def __init__(self, entry: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("histCard")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(6)

        # Tür ikonu
        typ = entry.get("type", "")
        fmt = entry.get("fmt", "")
        if typ == "clean":
            icon = "🎛"
        elif fmt in ("mp4", "mkv", "webm"):
            icon = "🎬"
        else:
            icon = "🎵"

        title_txt = entry.get("title", "?")[:55]
        lbl_icon = QLabel(f"{icon}  {title_txt}")
        lbl_icon.setObjectName("jobTitle")
        lbl_icon.setWordWrap(True)
        lay.addWidget(lbl_icon)

        meta = QLabel(
            f"{fmt.upper() if fmt else '?'} · "
            f"{entry.get('date','?')} · "
            f"{entry.get('quality','') or entry.get('status','')}")
        meta.setObjectName("jobSub")
        lay.addWidget(meta)

        # Dizin bilgisi
        out_dir = entry.get("out_dir", "")
        if out_dir:
            dir_lbl = QLabel(f"📁 {out_dir[:50]}")
            dir_lbl.setObjectName("jobSub")
            lay.addWidget(dir_lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        path = entry.get("path", "")
        if path and os.path.exists(path):
            btn_play = QPushButton("▶ Aç")
            btn_play.setObjectName("secondaryBtn")
            btn_play.clicked.connect(lambda: os.startfile(path))
            btn_row.addWidget(btn_play)

        parent_dir = str(Path(path).parent) if path else out_dir
        if parent_dir and os.path.exists(parent_dir):
            btn_open = QPushButton("📁 Klasör")
            btn_open.setObjectName("secondaryBtn")
            btn_open.clicked.connect(lambda: os.startfile(parent_dir))
            btn_row.addWidget(btn_open)

        btn_row.addStretch()
        lay.addLayout(btn_row)


class HistoryTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Üst çubuk
        top = QWidget()
        top.setObjectName("sidePanelBg")
        top_lay = QHBoxLayout(top)
        top_lay.setContentsMargins(20, 12, 20, 12)

        lbl = section_label("Geçmiş")
        top_lay.addWidget(lbl)

        # Filtre
        self._filter = QComboBox()
        self._filter.addItems(["Tümü", "İndirme", "Temizleme"])
        self._filter.setFixedWidth(120)
        self._filter.currentIndexChanged.connect(self.reload)
        top_lay.addWidget(self._filter)

        top_lay.addStretch()

        btn_clr = QPushButton("🗑  Temizle")
        btn_clr.setObjectName("dangerBtn")
        btn_clr.clicked.connect(self._clear)
        top_lay.addWidget(btn_clr)

        btn_ref = QPushButton("↻  Yenile")
        btn_ref.setObjectName("secondaryBtn")
        btn_ref.clicked.connect(self.reload)
        top_lay.addWidget(btn_ref)

        root.addWidget(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._inner = QWidget()
        self._inner.setObjectName("panelBg")
        self._grid  = QGridLayout(self._inner)
        self._grid.setContentsMargins(20, 20, 20, 20)
        self._grid.setSpacing(14)
        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self._inner)
        root.addWidget(scroll, 1)

        self._empty = QLabel("Henüz tamamlanan işlem yok.")
        self._empty.setObjectName("jobSub")
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.reload()

    def reload(self):
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        hist = database.get_history(limit=200)

        # Filtrele
        f = self._filter.currentText()
        if f == "İndirme":
            hist = [e for e in hist if e.get("type") != "clean"]
        elif f == "Temizleme":
            hist = [e for e in hist if e.get("type") == "clean"]

        if not hist:
            self._grid.addWidget(self._empty, 0, 0, 1, 3,
                                 alignment=Qt.AlignmentFlag.AlignCenter)
            return

        cols = 3
        for i, entry in enumerate(hist):
            card = HistoryCard(entry)
            self._grid.addWidget(card, i // cols, i % cols)

    def add_entry(self, entry: dict):
        """DB'ye ekle ve listeyi yenile."""
        database.add_history(entry)
        self.reload()

    def _clear(self):
        database.clear_history()
        self.reload()
