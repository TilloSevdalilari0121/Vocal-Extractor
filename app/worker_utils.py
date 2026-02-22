"""
Paylaşılan sabitler, ffmpeg yönetimi, ONNX provider tespiti.
workers.py ve worker_mdx.py tarafından import edilir.
"""
import os, subprocess, shutil, zipfile, urllib.request
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal

# ── Kütüphane kontrolleri (import sırası önemli: onnxruntime önce) ────────────
try:
    import onnxruntime as _ort
    ORT_AVAILABLE = True
    ORT_VERSION   = _ort.__version__
    ORT_PROVIDERS = _ort.get_available_providers()
except Exception as _e:
    ORT_AVAILABLE = False
    ORT_VERSION   = ""
    ORT_PROVIDERS = ["CPUExecutionProvider"]
    print(f"[worker_utils] onnxruntime yüklenemedi: {_e}")

try:
    import librosa as _lib
    LIBROSA_OK = True
except Exception:
    LIBROSA_OK = False

try:
    import soundfile as _sf
    SF_OK = True
except Exception:
    SF_OK = False

# ── Yollar ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.parent
FFMPEG_DIR = SCRIPT_DIR / "ffmpeg_bin"
FFMPEG_EXE = FFMPEG_DIR / "ffmpeg.exe"
MODEL_DIR  = SCRIPT_DIR / "models"

FFMPEG_URL = (
    "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/"
    "ffmpeg-master-latest-win64-gpl.zip"
)

# ── ffmpeg ────────────────────────────────────────────────────────────────────

def find_ffmpeg() -> str | None:
    if FFMPEG_EXE.exists():
        return str(FFMPEG_EXE)
    return shutil.which("ffmpeg")


def add_to_path(folder: str):
    os.environ["PATH"] = folder + os.pathsep + os.environ.get("PATH", "")


def test_ffmpeg(exe: str) -> bool:
    try:
        r = subprocess.run([exe, "-version"], capture_output=True, timeout=10)
        return r.returncode == 0
    except Exception:
        return False


class FFmpegInstaller(QThread):
    log      = pyqtSignal(str, str)
    progress = pyqtSignal(int)
    done     = pyqtSignal(bool)

    def run(self):
        try:
            FFMPEG_DIR.mkdir(parents=True, exist_ok=True)
            zip_path = FFMPEG_DIR / "ffmpeg.zip"
            self.log.emit("ffmpeg indiriliyor (~130 MB)...", "warn")

            def _hook(block, bs, total):
                if total > 0:
                    self.progress.emit(min(90, int(block * bs * 90 / total)))

            urllib.request.urlretrieve(FFMPEG_URL, zip_path, _hook)
            self.progress.emit(92)
            self.log.emit("✓ İndirildi, çıkarılıyor...", "ok")

            with zipfile.ZipFile(zip_path, "r") as zf:
                for m in zf.namelist():
                    if Path(m).name in ("ffmpeg.exe", "ffprobe.exe") and "/bin/" in m:
                        (FFMPEG_DIR / Path(m).name).write_bytes(zf.read(m))
                        self.log.emit(f"✓ {Path(m).name} kuruldu", "ok")

            zip_path.unlink(missing_ok=True)
            if not FFMPEG_EXE.exists():
                raise FileNotFoundError("ffmpeg.exe çıkarılamadı!")
            add_to_path(str(FFMPEG_DIR))
            self.progress.emit(100)
            self.log.emit("✓ ffmpeg hazır!", "ok")
            self.done.emit(True)
        except Exception as ex:
            self.log.emit(f"✗ ffmpeg indirilemedi: {ex}", "err")
            self.done.emit(False)


def ensure_ffmpeg(worker) -> str | None:
    """ffmpeg yoksa indir, yolunu döndür. Worker log/progress sinyallerine yazar."""
    exe = find_ffmpeg()
    if exe and test_ffmpeg(exe):
        add_to_path(str(Path(exe).parent))
        worker.log.emit(f"✓ ffmpeg: {exe}", "info")
        return exe
    worker.log.emit("ffmpeg kuruluyor...", "warn")
    worker.step.emit("ffmpeg kuruluyor...")
    ok_box = [False]
    inst = FFmpegInstaller()
    inst.log.connect(worker.log)
    inst.progress.connect(worker.progress)
    inst.done.connect(lambda s: ok_box.__setitem__(0, s))
    inst.start()
    inst.wait()
    return str(FFMPEG_EXE) if ok_box[0] else None


# ── ONNX provider ─────────────────────────────────────────────────────────────

def get_providers() -> list[str]:
    """DirectML → CUDA → CPU öncelik sırasıyla kullanılabilir provider'ları döndür."""
    try:
        import onnxruntime as ort
        avail = ort.get_available_providers()
        result = []
        if "DmlExecutionProvider"  in avail: result.append("DmlExecutionProvider")
        if "CUDAExecutionProvider" in avail: result.append("CUDAExecutionProvider")
        result.append("CPUExecutionProvider")
        return result
    except Exception:
        return ["CPUExecutionProvider"]
