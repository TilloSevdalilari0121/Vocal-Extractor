"""
İNDİRME sekmesi — ses (MP3/WAV/FLAC) veya video (MP4) indir.
DB'ye geçmiş kaydeder; son klasörü hatırlar.
"""
import re
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QButtonGroup, QRadioButton,
    QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt

from app import database
from app.widgets import section_label, h_line, FolderRow, JobCard, LogPanel
from app.workers import DownloadWorker, extract_video_id

AUDIO_QUALITIES = ["320 kbps", "192 kbps", "128 kbps", "64 kbps"]
VIDEO_QUALITIES  = ["2160p (4K)", "1080p", "720p", "480p", "360p"]


def _q_val(q_str: str) -> str:
    return q_str.split()[0].replace("p", "")


class DownloadTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._workers: list[DownloadWorker] = []
        self._empty_lbl = None
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sol panel ─────────────────────────────────────────────────────────
        side = QWidget()
        side.setObjectName("sidePanelBg")
        side.setFixedWidth(340)
        lay = QVBoxLayout(side)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(16)

        lay.addWidget(section_label("YouTube Linki"))
        self._url = QLineEdit()
        self._url.setPlaceholderText("https://youtube.com/watch?v=...")
        self._url.textChanged.connect(self._on_url_changed)
        lay.addWidget(self._url)

        self._hint = QLabel("Video linkini buraya yapıştırın")
        self._hint.setObjectName("jobSub")
        self._hint.setWordWrap(True)
        lay.addWidget(self._hint)

        lay.addWidget(h_line())
        lay.addWidget(section_label("Format"))

        fmt_row = QHBoxLayout()
        fmt_row.setSpacing(8)
        self._fmt_grp = QButtonGroup(self)
        self._rb_mp3  = QRadioButton("MP3")
        self._rb_wav  = QRadioButton("WAV")
        self._rb_flac = QRadioButton("FLAC")
        self._rb_mp4  = QRadioButton("MP4 Video")
        self._rb_mp3.setChecked(True)
        for rb in (self._rb_mp3, self._rb_wav, self._rb_flac, self._rb_mp4):
            self._fmt_grp.addButton(rb)
            fmt_row.addWidget(rb)
        fmt_row.addStretch()
        lay.addLayout(fmt_row)
        self._rb_mp4.toggled.connect(self._on_fmt_changed)

        lay.addWidget(h_line())
        lay.addWidget(section_label("Kalite"))
        self._quality = QComboBox()
        self._quality.addItems(AUDIO_QUALITIES)
        lay.addWidget(self._quality)

        lay.addWidget(h_line())
        lay.addWidget(section_label("Kayıt Klasörü"))
        # db_key ile son klasör hatırlanır
        default_dir = str(Path.home() / "Desktop" / "İndirilenler")
        self._folder = FolderRow(default_dir, db_key="download_dir")
        lay.addWidget(self._folder)

        lay.addStretch()

        self._start_btn = QPushButton("▶   İndir")
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

        self._empty_lbl = QLabel("Henüz indirme yok.\nLink gir ve ▶ İndir'e bas.")
        self._empty_lbl.setObjectName("jobSub")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._jobs_lay.addWidget(self._empty_lbl)

        scroll.setWidget(self._jobs_w)
        right_lay.addWidget(scroll, 1)

        self._log = LogPanel()
        right_lay.addWidget(self._log)

        root.addWidget(right, 1)

    def _on_url_changed(self, text: str):
        if text.startswith("https://www.youtube.com/watch?v=") and len(text) < 60:
            vid = extract_video_id(text)
            if vid:
                self._hint.setText(f"✓ Video ID: {vid}")
                self._hint.setStyleSheet("color:#4ADE80;font-size:11px;")
            return

        vid = extract_video_id(text)
        if vid:
            clean = f"https://www.youtube.com/watch?v={vid}"
            self._url.blockSignals(True)
            self._url.setText(clean)
            self._url.blockSignals(False)
            self._hint.setText(f"✓ Video ID: {vid}  (link temizlendi)")
            self._hint.setStyleSheet("color:#4ADE80;font-size:11px;")
        elif text.strip():
            self._hint.setText("⚠ Geçerli YouTube video linki bulunamadı")
            self._hint.setStyleSheet("color:#FBBF24;font-size:11px;")
        else:
            self._hint.setText("Video linkini buraya yapıştırın")
            self._hint.setStyleSheet("")

    def _on_fmt_changed(self):
        self._quality.clear()
        if self._rb_mp4.isChecked():
            self._quality.addItems(VIDEO_QUALITIES)
        else:
            self._quality.addItems(AUDIO_QUALITIES)

    def _current_fmt(self) -> str:
        if self._rb_wav.isChecked():  return "wav"
        if self._rb_flac.isChecked(): return "flac"
        if self._rb_mp4.isChecked():  return "mp4"
        return "mp3"

    def _start(self):
        raw = self._url.text().strip()

        vid = extract_video_id(raw)
        if not vid:
            self._log.append(
                "✗ Geçerli YouTube video ID bulunamadı!\n"
                "  Örnek: https://youtube.com/watch?v=ABC1234WXYZ", "err")
            self._hint.setText("✗ Geçersiz URL")
            self._hint.setStyleSheet("color:#F87171;font-size:11px;")
            return

        clean_url = f"https://www.youtube.com/watch?v={vid}"
        self._url.blockSignals(True)
        self._url.setText(clean_url)
        self._url.blockSignals(False)
        self._hint.setText(f"✓ İndiriliyor: {clean_url}")
        self._hint.setStyleSheet("color:#4ADE80;font-size:11px;")

        fmt     = self._current_fmt()
        quality = _q_val(self._quality.currentText())
        out_dir = self._folder.path()

        if self._empty_lbl is not None:
            self._empty_lbl.setParent(None)
            self._empty_lbl = None

        steps = ["📥 İndir", "⚙ İşle", "✅ Bitti"]
        card  = JobCard(clean_url, f"{fmt.upper()} — {self._quality.currentText()}", steps)
        card.set_running()
        self._jobs_lay.insertWidget(0, card)

        w = DownloadWorker(clean_url, out_dir, fmt, quality)
        self._workers.append(w)
        w.log.connect(self._log.append)
        w.progress.connect(card.update_progress)
        w.step.connect(lambda s, c=card: c.update_step(0, s))
        w.finished.connect(lambda ok, info, c=card, u=clean_url,
                           q=self._quality.currentText(), f=fmt, d=out_dir:
                           self._on_done(ok, info, c, u, q, f, d))
        w.start()

        self._log.append(f"Başlatıldı → {clean_url}", "info")

    def _on_done(self, ok: bool, info: str, card: JobCard,
                 url: str, quality: str, fmt: str, out_dir: str):
        if ok:
            card.set_done()
            card.set_sub(info)
            self._log.append("✓ İndirme tamamlandı", "ok")

            # Geçmişe kaydet
            save_history = database.get_setting("save_history", "1") == "1"
            if save_history:
                database.add_history({
                    "type":    "download",
                    "title":   url,
                    "path":    info,         # dosya yolu
                    "out_dir": out_dir,
                    "fmt":     fmt,
                    "quality": quality,
                    "status":  "done",
                })
        else:
            card.set_error()
            self._log.append(f"✗ {info[:200]}", "err")

            save_history = database.get_setting("save_history", "1") == "1"
            if save_history:
                database.add_history({
                    "type":    "download",
                    "title":   url,
                    "path":    "",
                    "out_dir": out_dir,
                    "fmt":     fmt,
                    "quality": quality,
                    "status":  "error",
                })
