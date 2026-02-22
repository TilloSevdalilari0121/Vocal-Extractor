"""
SES TEMİZLEME sekmesi — DB entegrasyonlu, son klasörü hatırlar.
"""
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QScrollArea, QFrame, QFileDialog,
    QButtonGroup, QRadioButton, QCheckBox,
)
from PyQt6.QtCore import Qt

from app import database
from app.widgets import section_label, h_line, FolderRow, JobCard, LogPanel
from app.workers import CleanWorker
from app.worker_mdx import MODEL_CATALOG, DEFAULT_MODEL, model_desc, model_output_type


class CleanTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._workers: list[CleanWorker] = []
        self._src_path = ""
        self._empty_lbl = None
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sol panel ─────────────────────────────────────────────────────────
        side = QWidget()
        side.setObjectName("sidePanelBg")
        side.setFixedWidth(360)
        lay = QVBoxLayout(side)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(14)

        # Kaynak dosya
        lay.addWidget(section_label("Kaynak Dosya"))
        self._src_line = QLineEdit()
        self._src_line.setPlaceholderText("Dosya seç veya sürükle...")
        self._src_line.setReadOnly(True)
        lay.addWidget(self._src_line)

        src_btn_row = QHBoxLayout()
        src_btn_row.setSpacing(8)
        btn_file = QPushButton("🎵  Dosya Seç")
        btn_file.setObjectName("secondaryBtn")
        btn_file.clicked.connect(self._pick_file)
        btn_folder = QPushButton("📁  Klasörden")
        btn_folder.setObjectName("secondaryBtn")
        btn_folder.clicked.connect(self._pick_from_folder)
        src_btn_row.addWidget(btn_file)
        src_btn_row.addWidget(btn_folder)
        lay.addLayout(src_btn_row)

        lay.addWidget(h_line())

        # Kayıt klasörü
        lay.addWidget(section_label("Kayıt Klasörü"))
        default_out = str(Path.home() / "Desktop" / "Temizlenen_Sesler")
        self._out_folder = FolderRow(default_out, db_key="clean_dir")
        lay.addWidget(self._out_folder)

        lay.addWidget(h_line())

        # Model seçimi
        lay.addWidget(section_label("Yapay Zeka Modeli"))
        self._model_cb = QComboBox()
        self._model_cb.addItems(list(MODEL_CATALOG.keys()))
        self._model_cb.setCurrentText(DEFAULT_MODEL)
        self._model_cb.currentTextChanged.connect(self._on_model_changed)
        lay.addWidget(self._model_cb)

        self._model_hint = QLabel()
        self._model_hint.setObjectName("jobSub")
        self._model_hint.setWordWrap(True)
        lay.addWidget(self._model_hint)
        self._on_model_changed(DEFAULT_MODEL)   # ilk ipucu

        lay.addWidget(h_line())

        # Çıktı formatı
        lay.addWidget(section_label("Çıktı Formatı"))
        fmt_row = QHBoxLayout()
        fmt_row.setSpacing(8)
        self._fmt_grp = QButtonGroup(self)
        self._rb_mp3  = QRadioButton("MP3")
        self._rb_wav  = QRadioButton("WAV")
        self._rb_flac = QRadioButton("FLAC")
        self._rb_mp3.setChecked(True)
        for rb in (self._rb_mp3, self._rb_wav, self._rb_flac):
            self._fmt_grp.addButton(rb)
            fmt_row.addWidget(rb)
        fmt_row.addStretch()
        lay.addLayout(fmt_row)

        lay.addWidget(h_line())

        # Sessizlik temizleme
        lay.addWidget(section_label("Sessizlik Temizleme"))
        self._trim_chk = QCheckBox("Müzik aralarındaki sessizlikleri kaldır")
        self._trim_chk.setChecked(True)
        self._trim_chk.toggled.connect(self._on_trim_toggled)
        lay.addWidget(self._trim_chk)

        pause_row = QHBoxLayout()
        pause_row.setSpacing(8)
        lbl_p = QLabel("Araya eklenecek sessizlik:")
        lbl_p.setObjectName("jobSub")
        pause_row.addWidget(lbl_p)
        self._pause_cb = QComboBox()
        self._pause_cb.addItems(["0.5 sn", "1 sn", "1.5 sn", "2 sn", "3 sn"])
        self._pause_cb.setCurrentIndex(1)
        self._pause_cb.setFixedWidth(90)
        pause_row.addWidget(self._pause_cb)
        pause_row.addStretch()
        lay.addLayout(pause_row)

        db_row = QHBoxLayout()
        db_row.setSpacing(8)
        lbl_db = QLabel("Sessizlik eşiği:")
        lbl_db.setObjectName("jobSub")
        db_row.addWidget(lbl_db)
        self._thresh_cb = QComboBox()
        self._thresh_cb.addItems(["-25 dB", "-35 dB", "-45 dB", "-55 dB"])
        self._thresh_cb.setCurrentIndex(1)
        self._thresh_cb.setFixedWidth(90)
        db_row.addWidget(self._thresh_cb)
        db_row.addStretch()
        lay.addLayout(db_row)

        lay.addStretch()

        self._start_btn = QPushButton("🎛   Temizlemeyi Başlat")
        self._start_btn.setObjectName("primaryBtn")
        self._start_btn.setFixedHeight(48)
        self._start_btn.clicked.connect(self._start)
        lay.addWidget(self._start_btn)

        root.addWidget(side)

        # ── Sağ panel ─────────────────────────────────────────────────────────
        right = QWidget()
        right.setObjectName("panelBg")
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._jobs_w = QWidget()
        self._jobs_w.setObjectName("panelBg")
        self._jobs_lay = QVBoxLayout(self._jobs_w)
        self._jobs_lay.setContentsMargins(20, 20, 20, 20)
        self._jobs_lay.setSpacing(12)
        self._jobs_lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._empty_lbl = QLabel("Dosya seç ve temizlemeyi başlat.")
        self._empty_lbl.setObjectName("jobSub")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._jobs_lay.addWidget(self._empty_lbl)

        scroll.setWidget(self._jobs_w)
        right_lay.addWidget(scroll, 1)

        self._log = LogPanel()
        right_lay.addWidget(self._log)

        root.addWidget(right, 1)

    # ── Yardımcı slotlar ──────────────────────────────────────────────────────

    def _on_model_changed(self, label: str):
        out = model_output_type(label)
        prefix = "🎤 Çıktı: ses (vokal)" if out == "vocals" else "🎸 Çıktı: enstrüman → vokal tersçevrilir"
        self._model_hint.setText(f"{prefix}\n{model_desc(label)}")

    def _on_trim_toggled(self, checked: bool):
        self._pause_cb.setEnabled(checked)
        self._thresh_cb.setEnabled(checked)

    def _current_fmt(self) -> str:
        if self._rb_wav.isChecked():  return "wav"
        if self._rb_flac.isChecked(): return "flac"
        return "mp3"

    # ── Dosya seçimi ──────────────────────────────────────────────────────────

    def _pick_file(self):
        start_dir = database.get_setting("last_browse_dir", str(Path.home()))
        path, _ = QFileDialog.getOpenFileName(
            self, "Ses Dosyası Seç", start_dir,
            "Ses Dosyaları (*.mp3 *.wav *.flac *.m4a *.ogg *.aac *.mp4 *.webm)")
        if path:
            database.set_setting("last_browse_dir", str(Path(path).parent))
            self._set_src(path)

    def _pick_from_folder(self):
        start_dir = database.get_setting("last_browse_dir", str(Path.home()))
        folder = QFileDialog.getExistingDirectory(self, "Klasör Seç", start_dir)
        if not folder:
            return
        database.set_setting("last_browse_dir", folder)
        exts  = {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".aac"}
        found = [str(f) for f in Path(folder).iterdir()
                 if f.suffix.lower() in exts]
        if not found:
            self._log.append("Klasörde ses dosyası bulunamadı!", "err")
            return
        if len(found) == 1:
            self._set_src(found[0])
        else:
            path, _ = QFileDialog.getOpenFileName(
                self, "Dosya Seç", folder,
                "Ses Dosyaları (*.mp3 *.wav *.flac *.m4a *.ogg)")
            if path:
                self._set_src(path)

    def _set_src(self, path: str):
        self._src_path = path
        self._src_line.setText(path)
        self._log.append(f"Seçildi: {Path(path).name}", "info")

    # ── İşlem başlatma ────────────────────────────────────────────────────────

    def _start(self):
        if not self._src_path or not os.path.exists(self._src_path):
            self._log.append("Lütfen geçerli bir kaynak dosya seçin!", "err")
            return

        model_label = self._model_cb.currentText()
        out_dir     = self._out_folder.path()
        out_fmt     = self._current_fmt()
        fname       = Path(self._src_path).name
        trim        = self._trim_chk.isChecked()
        pause_sn    = float(self._pause_cb.currentText().replace(" sn", ""))
        thresh_db   = int(self._thresh_cb.currentText().replace(" dB", ""))

        if self._empty_lbl is not None:
            self._empty_lbl.setParent(None)
            self._empty_lbl = None

        steps = ["🧠 Model", "🎛 Ayır", "🎵 Kaydet", "✅ Bitti"]
        card  = JobCard(fname, model_label, steps)
        card.set_running()
        self._jobs_lay.insertWidget(0, card)

        w = CleanWorker(
            self._src_path, out_dir, model_label, out_fmt,
            trim=trim, pause_sec=pause_sn, thresh_db=thresh_db)
        self._workers.append(w)
        w.log.connect(self._log.append)
        w.progress.connect(card.update_progress)
        w.step.connect(lambda s, c=card: c.update_step(0, s))
        w.finished.connect(
            lambda ok, info, c=card, f=fname, d=out_dir,
                   fmt=out_fmt, ml=model_label:
            self._on_done(ok, info, c, f, d, fmt, ml))
        w.start()
        self._log.append(f"Başlatıldı → {fname}", "info")

    def _on_done(self, ok: bool, info: str, card: JobCard,
                 fname: str, out_dir: str, fmt: str, model_label: str):
        if ok:
            card.set_done()
            card.set_sub(info)
            self._log.append("✓ Temizleme tamamlandı", "ok")
        else:
            card.set_error()
            self._log.append(f"✗ {info}", "err")

        if database.get_setting("save_history", "1") == "1":
            database.add_history({
                "type":    "clean",
                "title":   fname,
                "path":    info if ok else "",
                "out_dir": out_dir,
                "fmt":     fmt,
                "quality": model_label,
                "status":  "done" if ok else "error",
            })
