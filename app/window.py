"""
Ana pencere — tüm sekmeleri bir araya getirir.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QStatusBar,
    QSystemTrayIcon, QMenu,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from app import database
from app.themes       import THEMES, THEME_DOTS, build_qss
from app.widgets      import ColorDot
from app.download_tab import DownloadTab
from app.clean_tab    import CleanTab
from app.history_tab  import HistoryTab
from app.session_tab  import SessionTab
from app.settings_tab import SettingsTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vocal Extractor Pro")
        self.setMinimumSize(1100, 700)
        self.resize(1200, 750)

        self._current_theme = database.get_setting("theme", "Tahoe Dark")
        if self._current_theme not in THEMES:
            self._current_theme = "Tahoe Dark"

        self._dots: dict[str, ColorDot] = {}
        self._build()
        self._apply_theme(self._current_theme)
        self._setup_tray()

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_titlebar())
        root.addWidget(self._make_tabbar())

        self._stack = QStackedWidget()

        self._tab_download = DownloadTab()
        self._tab_clean    = CleanTab()
        self._tab_history  = HistoryTab()
        self._tab_session  = SessionTab()
        self._tab_settings = SettingsTab()

        self._tab_settings.theme_changed.connect(self._apply_theme)

        for t in (self._tab_download, self._tab_clean,
                  self._tab_history, self._tab_session,
                  self._tab_settings):
            self._stack.addWidget(t)

        root.addWidget(self._stack, 1)

        # Log sinyallerini DB'ye bağla
        self._tab_download._log.appended.connect(
            lambda lvl, msg: database.log_entry(lvl, msg))
        self._tab_clean._log.appended.connect(
            lambda lvl, msg: database.log_entry(lvl, msg))

        self._status = QStatusBar()
        self._status.setObjectName("statusBar")
        self._status.showMessage("Hazır  •  Vocal Extractor Pro v2.0")
        self.setStatusBar(self._status)

    def _make_titlebar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("titleBar")
        bar.setFixedHeight(46)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(14)

        logo = QLabel("🎵")
        logo.setObjectName("appLogo")
        lay.addWidget(logo)

        title = QLabel("VOCAL EXTRACTOR PRO  •  v2.0")
        title.setObjectName("appTitle")
        lay.addWidget(title)
        lay.addStretch()

        for name, color in THEME_DOTS.items():
            dot = ColorDot(name, color)
            dot.set_active(name == self._current_theme)
            dot.clicked_sig.connect(self._apply_theme)
            lay.addWidget(dot)
            self._dots[name] = dot

        return bar

    def _make_tabbar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("tabBar")
        bar.setFixedHeight(44)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(0)

        self._tab_btns: list[QPushButton] = []
        tabs = [
            ("⬇  İndir",    0),
            ("🎛  Temizle",  1),
            ("🕒  Geçmiş",  2),
            ("📋  Oturumlar", 3),
            ("⚙  Ayarlar", 4),
        ]
        for label, idx in tabs:
            btn = QPushButton(label)
            btn.setObjectName("tabBtn")
            btn.setProperty("active", idx == 0)
            btn.clicked.connect(lambda _, i=idx: self._switch_tab(i))
            lay.addWidget(btn)
            self._tab_btns.append(btn)

        lay.addStretch()
        return bar

    def _switch_tab(self, idx: int):
        self._stack.setCurrentIndex(idx)
        for i, btn in enumerate(self._tab_btns):
            btn.setProperty("active", i == idx)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        if idx == 2:
            self._tab_history.reload()
        elif idx == 3:
            self._tab_session.reload()

    def _apply_theme(self, name: str):
        if name not in THEMES:
            return
        t = THEMES[name]
        self.setStyleSheet(build_qss(t))
        self._current_theme = name
        for tname, dot in self._dots.items():
            dot.set_active(tname == name)
        if hasattr(self, "_tab_settings"):
            self._tab_settings.set_theme_silent(name)
        # DB'ye kaydet
        database.set_setting("theme", name)

    def _setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        # Önce ikon ayarla, sonra göster ("No Icon set" uyarısını önler)
        from PyQt6.QtGui import QIcon, QPixmap, QColor
        px = QPixmap(16, 16)
        px.fill(QColor("#7c6af7"))
        icon = QIcon(px)

        self._tray = QSystemTrayIcon(icon, self)
        self._tray.setToolTip("Vocal Extractor Pro")

        menu = QMenu()
        act_show = QAction("Göster", self)
        act_quit = QAction("Kapat",  self)
        act_show.triggered.connect(self.showNormal)
        act_quit.triggered.connect(self._quit)
        menu.addAction(act_show)
        menu.addSeparator()
        menu.addAction(act_quit)
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._tray_click)

        tray_on = database.get_setting("tray", "1") == "1"
        if tray_on:
            self._tray.show()

    def _tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()
            self.raise_()

    def closeEvent(self, e):
        tray_on = database.get_setting("tray", "1") == "1"
        if (tray_on and QSystemTrayIcon.isSystemTrayAvailable()
                and hasattr(self, "_tray")):
            e.ignore()
            self.hide()
            self._tray.showMessage(
                "Vocal Extractor Pro",
                "Arka planda çalışıyor. Kapatmak için tepsi ikonuna sağ tıklayın.",
                QSystemTrayIcon.MessageIcon.Information, 2000)
        else:
            self._quit()
            e.accept()

    def _quit(self):
        database.end_session()
        if hasattr(self, "_tray"):
            self._tray.hide()
            self._tray.setVisible(False)
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()   # app.exec() döngüsünü sonlandır
        # main.py'deki os._exit() gerisini halleder
