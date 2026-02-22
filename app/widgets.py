"""
Ortak özel widget'lar.
"""
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QVBoxLayout,
    QPushButton, QFrame, QProgressBar, QSizePolicy,
    QTextEdit, QLineEdit, QFileDialog,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen


# ── Yardımcılar ───────────────────────────────────────────────────────────────
def h_line(parent=None) -> QFrame:
    line = QFrame(parent)
    line.setObjectName("separator")
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFixedHeight(1)
    return line


def section_label(text: str, parent=None) -> QLabel:
    lbl = QLabel(text.upper(), parent)
    lbl.setObjectName("sectionLabel")
    return lbl


# ── Renk noktası (tema seçici) ────────────────────────────────────────────────
class ColorDot(QWidget):
    clicked_sig = pyqtSignal(str)

    def __init__(self, theme_name: str, color: str, parent=None):
        super().__init__(parent)
        self.theme_name = theme_name
        self._color  = QColor(color)
        self._active = False
        self.setFixedSize(18, 18)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(theme_name)

    def set_active(self, v: bool):
        self._active = v
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(self._color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(2, 2, 14, 14)
        if self._active:
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(self._color.lighter(170), 2))
            p.drawEllipse(0, 0, 17, 17)

    def mousePressEvent(self, e):
        self.clicked_sig.emit(self.theme_name)


# ── Durum rozeti ─────────────────────────────────────────────────────────────
class StatusBadge(QLabel):
    _MAP = {
        "waiting": ("BEKLE",     "badgeWaiting"),
        "running": ("ÇALIŞIYOR", "badgeRunning"),
        "done":    ("TAMAM",     "badgeDone"),
        "error":   ("HATA",      "badgeError"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set("waiting")

    def set(self, state: str):
        text, obj = self._MAP.get(state, ("?", "badgeWaiting"))
        self.setText(text)
        self.setObjectName(obj)
        self.style().unpolish(self)
        self.style().polish(self)


# ── Adım göstergesi ──────────────────────────────────────────────────────────
class StepBar(QWidget):
    def __init__(self, steps: list[str], parent=None):
        super().__init__(parent)
        self._labels: list[QLabel] = []
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        for s in steps:
            lbl = QLabel(s)
            lbl.setObjectName("stepWait")
            self._labels.append(lbl)
            lay.addWidget(lbl)
        lay.addStretch()

    def set_active(self, idx: int):
        for i, lbl in enumerate(self._labels):
            obj = "stepDone" if i < idx else ("stepActive" if i == idx else "stepWait")
            lbl.setObjectName(obj)
            lbl.style().unpolish(lbl)
            lbl.style().polish(lbl)

    def set_done(self):
        for lbl in self._labels:
            lbl.setObjectName("stepDone")
            lbl.style().unpolish(lbl)
            lbl.style().polish(lbl)


# ── İş kartı ─────────────────────────────────────────────────────────────────
class JobCard(QWidget):
    def __init__(self, title: str, sub: str,
                 step_names: list[str], parent=None):
        super().__init__(parent)
        self.setObjectName("jobCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        # Üst satır
        top = QHBoxLayout()
        top.setSpacing(12)

        # İkon — artık objectName ile tema tarafından stilize edilir
        icon_lbl = QLabel("🎵")
        icon_lbl.setObjectName("jobIconBg")
        icon_lbl.setFixedSize(44, 44)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top.addWidget(icon_lbl)

        meta = QVBoxLayout()
        meta.setSpacing(2)
        self.title_lbl = QLabel(title)
        self.title_lbl.setObjectName("jobTitle")
        self.sub_lbl   = QLabel(sub)
        self.sub_lbl.setObjectName("jobSub")
        meta.addWidget(self.title_lbl)
        meta.addWidget(self.sub_lbl)
        top.addLayout(meta, 1)

        self.badge = StatusBadge()
        top.addWidget(self.badge)
        root.addLayout(top)

        # İlerleme satırı
        prog_row = QHBoxLayout()
        prog_row.setSpacing(10)
        self.step_lbl = QLabel("Başlatılıyor...")
        self.step_lbl.setObjectName("jobSub")
        prog_row.addWidget(self.step_lbl, 1)
        self.pct_lbl = QLabel("0%")
        self.pct_lbl.setObjectName("jobSub")
        prog_row.addWidget(self.pct_lbl)
        root.addLayout(prog_row)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        root.addWidget(self.bar)

        self.steps_bar = StepBar(step_names)
        root.addWidget(self.steps_bar)

    def update_progress(self, pct: int):
        self.bar.setValue(pct)
        self.pct_lbl.setText(f"{pct}%")

    def update_step(self, idx: int, text: str):
        self.step_lbl.setText(text)
        self.steps_bar.set_active(idx)

    def set_title(self, t: str):
        self.title_lbl.setText(t)

    def set_sub(self, s: str):
        self.sub_lbl.setText(s)

    def set_done(self):
        self.badge.set("done")
        self.steps_bar.set_done()
        self.bar.setValue(100)
        self.pct_lbl.setText("100%")

    def set_error(self):
        self.badge.set("error")

    def set_running(self):
        self.badge.set("running")


# ── Log paneli ────────────────────────────────────────────────────────────────
class LogPanel(QWidget):
    appended = pyqtSignal(str, str)   # (level, message) — DB log bağlantısı için

    _COLORS = {
        "ok":   "#4ADE80",
        "err":  "#F87171",
        "warn": "#FBBF24",
        "info": "#A67CFF",
        "":     "#808090",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("logPanel")
        self.setFixedHeight(150)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Başlık — objectName ile tema stilize eder (hardcoded color yok!)
        hdr_w = QWidget()
        hdr_w.setObjectName("logHeader")
        hdr = QHBoxLayout(hdr_w)
        hdr.setContentsMargins(14, 8, 14, 8)

        self._dot = QLabel("●")
        self._dot.setObjectName("logDot")
        hdr.addWidget(self._dot)

        lbl = QLabel("CANLI LOG")
        lbl.setObjectName("logTitle")
        hdr.addWidget(lbl)
        hdr.addStretch()

        clear_btn = QPushButton("Temizle")
        clear_btn.setObjectName("iconBtn")
        clear_btn.setFixedHeight(22)
        hdr.addWidget(clear_btn)
        lay.addWidget(hdr_w)

        self._text = QTextEdit()
        self._text.setReadOnly(True)
        lay.addWidget(self._text)

        clear_btn.clicked.connect(self._text.clear)

        # Yanıp sönen nokta
        self._blink_state = True
        self._blink_color_on  = "#4ADE80"
        self._blink_color_off = "transparent"
        timer = QTimer(self)
        timer.timeout.connect(self._blink)
        timer.start(1000)
        self._update_dot()

    def _blink(self):
        self._blink_state = not self._blink_state
        self._update_dot()

    def _update_dot(self):
        color = self._blink_color_on if self._blink_state else self._blink_color_off
        self._dot.setStyleSheet(f"color:{color};font-size:10px;background:transparent;")

    def append(self, msg: str, level: str = ""):
        color = self._COLORS.get(level, self._COLORS[""])
        t = datetime.now().strftime("%H:%M:%S")
        html = (
            f'<span style="color:#606080;font-family:Consolas;font-size:11px;">[{t}]</span> '
            f'<span style="color:{color};font-family:Consolas;font-size:11px;">{msg}</span>')
        self._text.append(html)
        sb = self._text.verticalScrollBar()
        sb.setValue(sb.maximum())
        # Dinleyicilere sinyal gönder (DB log için)
        self.appended.emit(level, msg)


# ── Klasör seçici ─────────────────────────────────────────────────────────────
class FolderRow(QWidget):
    changed = pyqtSignal(str)

    def __init__(self, default: str, db_key: str = "", parent=None):
        """
        db_key: veritabanından son kullanılan klasörü yüklemek için anahtar.
                Boşsa DB kullanılmaz.
        """
        super().__init__(parent)
        self._db_key = db_key

        # DB'den son klasörü yükle (varsa)
        initial = default
        if db_key:
            try:
                from app import database
                saved = database.get_setting(db_key)
                if saved and saved.strip():
                    initial = saved
            except Exception:
                pass

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        self._path_edit = QLineEdit(initial)
        self._path_edit.setReadOnly(True)
        lay.addWidget(self._path_edit, 1)

        btn = QPushButton("📁  Seç")
        btn.setObjectName("secondaryBtn")
        btn.setFixedWidth(90)
        btn.clicked.connect(self._pick)
        lay.addWidget(btn)

    def _pick(self):
        d = QFileDialog.getExistingDirectory(self, "Klasör Seç", self._path_edit.text())
        if d:
            self._path_edit.setText(d)
            # DB'ye kaydet
            if self._db_key:
                try:
                    from app import database
                    database.set_setting(self._db_key, d)
                except Exception:
                    pass
            self.changed.emit(d)

    def path(self) -> str:
        return self._path_edit.text()

    def set_path(self, p: str):
        self._path_edit.setText(p)
