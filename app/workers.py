"""
QThread işçileri: DownloadWorker, CleanWorker.
Ağır işler worker_utils.py ve worker_mdx.py'de.
"""
import os, re, subprocess, shutil, tempfile
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal

from app.worker_utils import (
    ORT_AVAILABLE, ORT_VERSION, ORT_PROVIDERS,
    LIBROSA_OK, SF_OK,
    find_ffmpeg, ensure_ffmpeg, get_providers,
)
from app.worker_mdx import (
    MODEL_CATALOG, DEFAULT_MODEL,
    ensure_model, mdx_separate, compact_vocals, model_output_type,
)

_VID_RE = re.compile(
    r'(?:youtube\.com/(?:watch\?(?:.*?&)?v=|shorts/|embed/)|youtu\.be/)'
    r'([A-Za-z0-9_-]{11})'
)


def extract_video_id(text: str) -> str | None:
    m = _VID_RE.search(text)
    return m.group(1) if m else None


# ── yt-dlp logger ─────────────────────────────────────────────────────────────

class _YTLogger:
    _SKIP = (
        "No supported JavaScript runtime", "deno",
        "ffmpeg not found", "Installing ffmpeg is strongly recommended",
        "writing DASH",
    )
    def __init__(self, w): self._w = w
    def debug(self, msg):
        if not msg.startswith("[debug]") and msg.strip():
            self._w.log.emit(msg.strip(), "")
    def info(self, msg):
        if msg.strip(): self._w.log.emit(msg.strip(), "info")
    def warning(self, msg):
        if any(s in msg for s in self._SKIP): return
        if msg.strip(): self._w.log.emit(f"⚠ {msg.strip()}", "warn")
    def error(self, msg):
        if msg.strip(): self._w.log.emit(f"✗ {msg.strip()}", "err")


# ── İndirme ───────────────────────────────────────────────────────────────────

class DownloadWorker(QThread):
    log      = pyqtSignal(str, str)
    progress = pyqtSignal(int)
    step     = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, url: str, out_dir: str, fmt: str,
                 quality: str, parent=None):
        super().__init__(parent)
        vid = extract_video_id(url)
        self.url     = f"https://www.youtube.com/watch?v={vid}" if vid else url
        self.out_dir = out_dir
        self.fmt     = fmt
        self.quality = quality

    def run(self):
        try:
            import yt_dlp
        except ImportError:
            self.log.emit("✗ yt-dlp kurulu değil: pip install yt-dlp", "err")
            self.finished.emit(False, "yt-dlp eksik")
            return

        tmp_dir = tempfile.mkdtemp(prefix="vocal_dl_")
        try:
            vid = extract_video_id(self.url)
            if not vid:
                raise ValueError(f"Geçersiz YouTube URL: {self.url[:60]!r}")

            url = f"https://www.youtube.com/watch?v={vid}"
            self.log.emit(f"✓ Video ID: {vid}", "ok")

            ffmpeg_exe = ensure_ffmpeg(self)
            self.step.emit("Bağlanıyor...")

            with yt_dlp.YoutubeDL(
                {"quiet": True, "no_warnings": True,
                 "noplaylist": True, "logger": _YTLogger(self)}
            ) as ydl:
                info = ydl.extract_info(url, download=False)

            if not info:
                raise ValueError("Video bilgisi alınamadı.")

            title = info.get("title", "indirilen")
            dur   = info.get("duration", 0) or 0
            self.log.emit(f"✓ {title}", "ok")
            self.log.emit(f"⏱  {dur // 60}:{dur % 60:02d}", "")

            safe = "".join(
                c for c in title if c.isalnum() or c in " _-"
            ).strip()[:80] or "indirilen"

            os.makedirs(self.out_dir, exist_ok=True)
            out_tpl = os.path.join(self.out_dir, f"{safe}.%(ext)s")

            base = {
                "noplaylist": True, "progress_hooks": [self._hook],
                "logger": _YTLogger(self), "outtmpl": out_tpl,
            }
            if ffmpeg_exe:
                base["ffmpeg_location"] = str(Path(ffmpeg_exe).parent)

            if self.fmt == "mp4":
                dl_opts = {
                    **base,
                    "format": (
                        f"bestvideo[height<={self.quality}][ext=mp4]"
                        f"+bestaudio[ext=m4a]/bestvideo[height<={self.quality}]"
                        f"+bestaudio/best[height<={self.quality}]"
                    ),
                    "merge_output_format": "mp4",
                }
            elif ffmpeg_exe:
                dl_opts = {
                    **base,
                    "format": "bestaudio/best",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": self.fmt,
                        "preferredquality": self.quality,
                    }],
                }
            else:
                self.log.emit("⚠ ffmpeg yok → m4a kaydedilecek", "warn")
                dl_opts = {**base, "format": "bestaudio[ext=m4a]/bestaudio/best"}

            self.step.emit("İndiriliyor...")
            self.log.emit("İndirme başladı...", "warn")
            with yt_dlp.YoutubeDL(dl_opts) as ydl:
                ydl.download([url])

            final = self._find_output(self.out_dir, safe)
            if not final:
                raise FileNotFoundError("İndirilen dosya bulunamadı.")

            self.progress.emit(100)
            self.log.emit(f"✓ Kaydedildi: {final}", "ok")
            self.step.emit("✓ Tamamlandı")
            self.finished.emit(True, final)

        except Exception as ex:
            import traceback
            self.log.emit(f"✗ Hata: {ex}", "err")
            self.log.emit(
                "\n".join(traceback.format_exc().strip().splitlines()[-4:]), "err")
            self.step.emit("✗ Hata")
            self.finished.emit(False, str(ex))
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def _hook(self, d: dict):
        st = d.get("status", "")
        if st == "downloading":
            raw = d.get("_percent_str", "0").strip().rstrip("%")
            try:
                pct   = min(95, int(float(raw.replace(",", "."))))
                speed = d.get("_speed_str", "?")
                eta   = d.get("_eta_str", "?")
                self.progress.emit(pct)
                self.step.emit(f"İndiriliyor {raw}%  —  {speed}  —  ETA {eta}")
            except ValueError:
                pass
        elif st == "finished":
            self.progress.emit(97)
            self.step.emit("Dönüştürülüyor...")

    @staticmethod
    def _find_output(folder: str, stem: str) -> str | None:
        try:
            files = os.listdir(folder)
        except FileNotFoundError:
            return None
        for f in files:
            p = Path(f)
            if p.suffix == ".part":
                continue
            if p.stem == stem or p.stem.startswith(stem):
                full = os.path.join(folder, f)
                if os.path.isfile(full) and os.path.getsize(full) > 0:
                    return full
        return None


# ── Ses Temizleme ─────────────────────────────────────────────────────────────

class CleanWorker(QThread):
    log      = pyqtSignal(str, str)
    progress = pyqtSignal(int)
    step     = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, src: str, out_dir: str, model_label: str, out_fmt: str,
                 trim: bool = False, pause_sec: float = 1.0,
                 thresh_db: int = -35, parent=None):
        super().__init__(parent)
        self.src         = src
        self.out_dir     = out_dir
        self.model_label = model_label or DEFAULT_MODEL
        self.out_fmt     = out_fmt
        self.trim        = trim
        self.pause_sec   = pause_sec
        self.thresh_db   = thresh_db

    def run(self):
        problems = []
        if not ORT_AVAILABLE: problems.append("onnxruntime-directml")
        if not LIBROSA_OK:    problems.append("librosa")
        if not SF_OK:         problems.append("soundfile")
        if problems:
            self.log.emit(f"✗ Eksik kütüphane: {', '.join(problems)}", "err")
            self.finished.emit(False, "Eksik bağımlılıklar")
            return

        self.log.emit(f"✓ onnxruntime {ORT_VERSION}", "info")
        self.log.emit(f"✓ Providers: {ORT_PROVIDERS}", "info")

        try:
            import soundfile as sf
            import numpy as np

            os.makedirs(self.out_dir, exist_ok=True)

            # ── Model indir / kontrol et ───────────────────────────────────────
            self.step.emit("Model kontrol ediliyor...")
            mdl_path = ensure_model(
                self.model_label,
                progress_cb = self.progress.emit,
                log_cb      = lambda m: self.log.emit(m, "info"),
            )

            # ── Provider ──────────────────────────────────────────────────────
            providers = get_providers()
            pn = providers[0]
            if pn == "DmlExecutionProvider":
                self.log.emit("✓ AMD/Intel/NVIDIA GPU (DirectML) aktif!", "ok")
            elif pn == "CUDAExecutionProvider":
                self.log.emit("✓ NVIDIA GPU (CUDA) aktif!", "ok")
            else:
                self.log.emit("⚠ GPU yok — CPU kullanılıyor", "warn")

            # ── Ayrıştır ──────────────────────────────────────────────────────
            self.step.emit("Vokal ayrıştırılıyor...")
            self.log.emit(f"Kaynak: {Path(self.src).name}", "info")
            self.log.emit(f"Model: {self.model_label}", "info")

            out_type = model_output_type(self.model_label)
            self.log.emit(
                f"Çıktı tipi: {'Vokal' if out_type == 'vocals' else 'Enstrüman (vokal=ters)'}",
                "info")

            vocals, _, sr = mdx_separate(
                model_path_  = mdl_path,
                audio_path   = self.src,
                providers    = providers,
                output_type  = out_type,
                progress_cb  = self.progress.emit,
                log_cb       = lambda m: self.log.emit(m, "info"),
            )

            # ── Sessizlik temizleme ────────────────────────────────────────────
            if self.trim:
                self.step.emit("Sessizlikler temizleniyor...")
                self.log.emit(
                    f"Sessizlik temizleme: eşik={self.thresh_db} dB, "
                    f"ara={self.pause_sec} sn", "info")
                vocals = compact_vocals(
                    vocals,
                    sr        = sr,
                    pause_sec = self.pause_sec,
                    thresh_db = self.thresh_db,
                    log_cb    = lambda m: self.log.emit(m, "ok"),
                )
                self.progress.emit(98)

            # ── Kaydet ────────────────────────────────────────────────────────
            self.step.emit("Kaydediliyor...")
            suffix = " – Temiz Ses"
            if self.trim:
                suffix += " (sessizlik giderildi)"
            base     = Path(self.src).stem
            final    = os.path.join(
                self.out_dir, f"{base}{suffix}.{self.out_fmt.lower()}")
            vocals_T = np.clip(vocals.T, -1.0, 1.0).astype(np.float32)

            if self.out_fmt.lower() == "wav":
                sf.write(final, vocals_T, sr, subtype="PCM_16")
            elif self.out_fmt.lower() in ("mp3", "flac"):
                ffmpeg_exe = find_ffmpeg()
                if not ffmpeg_exe:
                    self.log.emit("ffmpeg yok → WAV kaydediliyor", "warn")
                    final = final.replace(f".{self.out_fmt.lower()}", ".wav")
                    sf.write(final, vocals_T, sr, subtype="PCM_16")
                else:
                    tmp_wav = final + "_tmp.wav"
                    sf.write(tmp_wav, vocals_T, sr, subtype="PCM_16")
                    codec = "libmp3lame" if self.out_fmt.lower() == "mp3" else "flac"
                    ret = subprocess.run(
                        [ffmpeg_exe, "-y", "-i", tmp_wav,
                         "-codec:a", codec, "-qscale:a", "2", final],
                        capture_output=True, text=True, timeout=300)
                    try: os.unlink(tmp_wav)
                    except Exception: pass
                    if ret.returncode != 0:
                        raise RuntimeError(
                            f"ffmpeg hatası: {ret.stderr[-200:]}")
            else:
                sf.write(final, vocals_T, sr)

            self.progress.emit(100)
            self.log.emit(f"✓ Kaydedildi: {final}", "ok")
            self.step.emit("✓ Tamamlandı")
            self.finished.emit(True, final)

        except Exception as ex:
            import traceback
            self.log.emit(f"✗ Hata: {ex}", "err")
            self.log.emit(
                "\n".join(traceback.format_exc().strip().splitlines()[-5:]), "err")
            self.step.emit("✗ Hata")
            self.finished.emit(False, str(ex))
