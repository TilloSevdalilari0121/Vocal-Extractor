"""
Oturum sekmesi — geçmiş oturumları ve loglarını gösterir.
"""
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSplitter, QTextEdit,
)
from PyQt6.QtCore import Qt, pyqtSignal

from app import database
from app.widgets import section_label, h_line


class SessionItem(QWidget):
    clicked_sig = pyqtSignal(int)   # session_id

    def __init__(self, session: dict, is_current: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("sessionCard")
        self._sid = session["id"]
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(4)

        # Başlık
        title = QLabel(
            f"{'▶  AKTIF  —  ' if is_current else ''}"
            f"Oturum #{session['id']}")
        title.setObjectName("jobTitle")
        lay.addWidget(title)

        # Tarih
        try:
            dt = datetime.fromisoformat(session["started_at"])
            date_str = dt.strftime("%d.%m.%Y  %H:%M:%S")
        except Exception:
            date_str = session.get("started_at", "?")

        ended = session.get("ended_at")
        if ended:
            try:
                dt2 = datetime.fromisoformat(ended)
                dur = dt2 - datetime.fromisoformat(session["started_at"])
                dur_str = f"  ·  {int(dur.total_seconds()//60)}d {int(dur.total_seconds()%60)}s"
            except Exception:
                dur_str = ""
        else:
            dur_str = "  ·  devam ediyor"

        sub = QLabel(f"{date_str}{dur_str}  ·  {session.get('log_count', 0)} satır")
        sub.setObjectName("jobSub")
        lay.addWidget(sub)

    def mousePressEvent(self, e):
        self.clicked_sig.emit(self._sid)

    def set_active(self, v: bool):
        self.setProperty("active", v)
        self.style().unpolish(self)
        self.style().polish(self)


class SessionTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_sid: int | None = None
        self._items: dict[int, SessionItem] = {}
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
        lbl = section_label("Oturumlar")
        top_lay.addWidget(lbl)
        top_lay.addStretch()
        btn_ref = QPushButton("↻  Yenile")
        btn_ref.setObjectName("secondaryBtn")
        btn_ref.clicked.connect(self.reload)
        top_lay.addWidget(btn_ref)
        root.addWidget(top)

        # Splitter: sol = oturum listesi, sağ = log görüntüleyici
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # ── Sol: oturum listesi ──────────────────────────────────────────────
        left_w = QWidget()
        left_w.setObjectName("sidePanelBg")
        left_w.setMinimumWidth(220)
        left_w.setMaximumWidth(300)
        left_lay = QVBoxLayout(left_w)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(0)

        scroll_l = QScrollArea()
        scroll_l.setWidgetResizable(True)
        scroll_l.setFrameShape(QFrame.Shape.NoFrame)

        self._list_w = QWidget()
        self._list_w.setObjectName("sidePanelBg")
        self._list_lay = QVBoxLayout(self._list_w)
        self._list_lay.setContentsMargins(10, 10, 10, 10)
        self._list_lay.setSpacing(6)
        self._list_lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_l.setWidget(self._list_w)
        left_lay.addWidget(scroll_l)
        splitter.addWidget(left_w)

        # ── Sağ: log görüntüleyici ───────────────────────────────────────────
        right_w = QWidget()
        right_w.setObjectName("panelBg")
        right_lay = QVBoxLayout(right_w)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(0)

        # Başlık
        hdr = QWidget()
        hdr.setObjectName("logHeader")
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(16, 10, 16, 10)
        self._log_title = QLabel("Bir oturum seçin")
        self._log_title.setObjectName("jobTitle")
        hdr_lay.addWidget(self._log_title)
        hdr_lay.addStretch()
        btn_exp = QPushButton("📋 Kopyala")
        btn_exp.setObjectName("secondaryBtn")
        btn_exp.clicked.connect(self._copy_log)
        hdr_lay.addWidget(btn_exp)
        right_lay.addWidget(hdr)

        # Log metni
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setObjectName("logViewArea")
        right_lay.addWidget(self._log_text, 1)

        splitter.addWidget(right_w)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        root.addWidget(splitter, 1)

        self.reload()

    def reload(self):
        """Oturum listesini yenile."""
        # Mevcut öğeleri temizle
        while self._list_lay.count():
            item = self._list_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._items.clear()

        sessions = database.get_sessions(limit=100)
        current_id = database.CURRENT_SESSION_ID

        if not sessions:
            lbl = QLabel("Oturum bulunamadı.")
            lbl.setObjectName("jobSub")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list_lay.addWidget(lbl)
            return

        for s in sessions:
            is_cur = (s["id"] == current_id)
            item = SessionItem(s, is_cur)
            item.clicked_sig.connect(self._show_session)
            self._list_lay.addWidget(item)
            self._items[s["id"]] = item

        # İlk oturumu otomatik seç
        if sessions:
            self._show_session(sessions[0]["id"])

    def _show_session(self, session_id: int):
        """Oturum loglarını sağ panelde göster."""
        # Öncekini pasifleştir
        if self._current_sid and self._current_sid in self._items:
            self._items[self._current_sid].set_active(False)

        self._current_sid = session_id

        if session_id in self._items:
            self._items[session_id].set_active(True)

        self._log_title.setText(f"Oturum #{session_id} Logları")
        self._log_text.clear()

        logs = database.get_session_logs(session_id)
        if not logs:
            self._log_text.setPlainText("Bu oturumda log kaydı yok.")
            return

        _COLORS = {
            "ok":   "#4ADE80",
            "err":  "#F87171",
            "warn": "#FBBF24",
            "info": "#A67CFF",
            "":     "#808090",
        }

        html_parts = []
        for entry in logs:
            color = _COLORS.get(entry.get("level", ""), "#808090")
            ts = entry.get("timestamp", "")
            msg = entry.get("message", "").replace("<", "&lt;").replace(">", "&gt;")
            html_parts.append(
                f'<span style="color:#606080;font-family:Consolas;font-size:11px;">'
                f'[{ts}]</span> '
                f'<span style="color:{color};font-family:Consolas;font-size:11px;">'
                f'{msg}</span>')

        self._log_text.setHtml("<br>".join(html_parts))
        sb = self._log_text.verticalScrollBar()
        sb.setValue(sb.maximum())

    def refresh_current(self):
        """Aktif oturum görüntüleniyorsa logları yenile."""
        if self._current_sid == database.CURRENT_SESSION_ID:
            self._show_session(self._current_sid)

    def _copy_log(self):
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(self._log_text.toPlainText())
