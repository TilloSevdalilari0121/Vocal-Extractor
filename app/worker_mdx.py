"""
MDX-Net ONNX inference ve sessizlik kaldırma (VAD).

Model Kataloğu — output_type açıklaması
────────────────────────────────────────
"vocals"       → model vokal stem'ini tahmin eder, direkt kaydet
"instrumental" → model enstrüman stem'ini tahmin eder,
                 vokal = orijinal - enstrüman şeklinde elde edilir

Neden Inst modeller "müzik kaldı" sonucu verdi?
  UVR-MDX-NET-Inst_* modelleri enstrüman çıktısını üretir.
  Önceki kodda bu çıktı direkt "vokal" olarak kaydediliyordu → hata.
  Düzeltme: output_type="instrumental" ise audio - pred = vokal.

Türk halk müziği notu:
  Tüm bu modeller Batı pop/rock veri setiyle eğitildi.
  Zurna, ney, def, erbane gibi enstrümanları "enstrüman" veya "gürültü"
  olarak sınıflandırır. Şu an mevcut ONNX formatında Türk halk müziğine
  özel model bulunmamaktadır.
  BS-Roformer / MelBand-Roformer (2024 SOTA) daha iyi sonuç verir
  ancak PyTorch (.ckpt) gerektirir — ONNX dönüşümü yapılmadıkça eklenemez.
"""
import os, urllib.request
from pathlib import Path

from app.worker_utils import MODEL_DIR

# ── Model kataloğu ────────────────────────────────────────────────────────────
# output_type : "vocals"       → çıktı direkt vokal
#               "instrumental" → çıktı enstrüman; vokal = audio - pred
# use_case    : UI'da gösterilecek kısa kullanım amacı
MODEL_CATALOG: dict[str, dict] = {

    # ── Vokal ayırma (ses koru, müziği sil) ───────────────────────────────────
    "Kim Vocal 2 — Vokal Ayırma (varsayılan)": {
        "file":        "Kim_Vocal_2.onnx",
        "url":         ("https://github.com/TRvlvr/model_repo/releases/download/"
                        "all_public_uvr_models/Kim_Vocal_2.onnx"),
        "output_type": "vocals",
        "use_case":    "🎤 Vokal Ayırma",
        "desc": (
            "Ses korunur, müzik silinir.\n"
            "Batı pop/rock için optimize; zurna/ney gibi enstrümanlar "
            "kısmen müzik olarak sınıflandırılabilir."
        ),
    },
    "Voc FT — Vokal Ayırma (gelişmiş)": {
        "file":        "UVR-MDX-NET-Voc_FT.onnx",
        "url":         ("https://github.com/TRvlvr/model_repo/releases/download/"
                        "all_public_uvr_models/UVR-MDX-NET-Voc_FT.onnx"),
        "output_type": "vocals",
        "use_case":    "🎤 Vokal Ayırma",
        "desc": (
            "Ses korunur, müzik silinir.\n"
            "Kim Vocal 2'ye göre daha ince ayarlı fine-tuned model. "
            "Vokal kalitesi genellikle daha yüksek."
        ),
    },

    # ── Müzik/Enstrüman temizleme (müziği koru, sesi sil) ────────────────────
    "Inst HQ 3 — Müzik Temizleme": {
        "file":        "UVR-MDX-NET-Inst_HQ_3.onnx",
        "url":         ("https://github.com/TRvlvr/model_repo/releases/download/"
                        "all_public_uvr_models/UVR-MDX-NET-Inst_HQ_3.onnx"),
        "output_type": "instrumental",
        "use_case":    "🎸 Müzik Temizleme",
        "desc": (
            "Müzik/enstrüman korunur, insan sesi silinir.\n"
            "Arka plan müziğini temizlemek veya saf enstrüman elde etmek için."
        ),
    },
    "Inst HQ 4 — Müzik Temizleme (gelişmiş)": {
        "file":        "UVR-MDX-NET-Inst_HQ_4.onnx",
        "url":         ("https://github.com/TRvlvr/model_repo/releases/download/"
                        "all_public_uvr_models/UVR-MDX-NET-Inst_HQ_4.onnx"),
        "output_type": "instrumental",
        "use_case":    "🎸 Müzik Temizleme",
        "desc": (
            "Müzik/enstrüman korunur, insan sesi silinir.\n"
            "Inst serisinin en yeni ve en kaliteli versiyonu."
        ),
    },
    "Inst HQ 1 — Müzik Temizleme (alternatif)": {
        "file":        "UVR-MDX-NET-Inst_HQ_1.onnx",
        "url":         ("https://github.com/TRvlvr/model_repo/releases/download/"
                        "all_public_uvr_models/UVR-MDX-NET-Inst_HQ_1.onnx"),
        "output_type": "instrumental",
        "use_case":    "🎸 Müzik Temizleme",
        "desc": (
            "Müzik/enstrüman korunur, insan sesi silinir.\n"
            "HQ 3 ile benzer; bazı parçalarda daha iyi sonuç verebilir."
        ),
    },

    # ── Özel amaçlar ──────────────────────────────────────────────────────────
    "Karaoke — Arka Vokal Koruma": {
        "file":        "UVR_MDXNET_KARA_2.onnx",
        "url":         ("https://github.com/TRvlvr/model_repo/releases/download/"
                        "all_public_uvr_models/UVR_MDXNET_KARA_2.onnx"),
        "output_type": "vocals",
        "use_case":    "🎹 Karaoke",
        "desc": (
            "Ön vokal silinir; arka vokal + enstrüman kalır.\n"
            "Karaoke track oluşturmak için — arka koro seslerini korur."
        ),
    },
    "Reverb Temizleme — Yankı Azaltma": {
        "file":        "Reverb_HQ_By_FoxJoy.onnx",
        "url":         ("https://github.com/TRvlvr/model_repo/releases/download/"
                        "all_public_uvr_models/Reverb_HQ_By_FoxJoy.onnx"),
        "output_type": "vocals",
        "use_case":    "🔇 Yankı Azaltma",
        "desc": (
            "Ses öne alınır, yankı/reverb arka plana atılır.\n"
            "Ses temizledikten sonra kalan yankıyı gidermek için ideal. "
            "Önce Kim Vocal ile ayır, sonra bu modeli uygula."
        ),
    },
}

DEFAULT_MODEL = "Kim Vocal 2 — Vokal Ayırma (varsayılan)"


def model_path(label: str) -> str:
    info = MODEL_CATALOG.get(label, MODEL_CATALOG[DEFAULT_MODEL])
    return str(MODEL_DIR / info["file"])


def model_url(label: str) -> str:
    info = MODEL_CATALOG.get(label, MODEL_CATALOG[DEFAULT_MODEL])
    return info["url"]


def model_desc(label: str) -> str:
    info = MODEL_CATALOG.get(label, MODEL_CATALOG[DEFAULT_MODEL])
    use  = info.get("use_case", "")
    desc = info.get("desc", "")
    return f"{use}\n{desc}" if use else desc


def model_output_type(label: str) -> str:
    """'vocals' veya 'instrumental' döndürür."""
    info = MODEL_CATALOG.get(label, MODEL_CATALOG[DEFAULT_MODEL])
    return info.get("output_type", "vocals")


def ensure_model(label: str, progress_cb=None, log_cb=None) -> str:
    """
    Model yoksa indir. Döndürür: disk yolu.
    Hata durumunda RuntimeError fırlatır.
    """
    def _log(m):
        if log_cb: log_cb(m)
    def _prog(p):
        if progress_cb: progress_cb(p)

    path = model_path(label)
    url  = model_url(label)
    name = Path(path).name

    if os.path.isfile(path) and os.path.getsize(path) > 1_000_000:
        _log(f"✓ Model: {name} ({os.path.getsize(path)/1024/1024:.1f} MB)")
        return path

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    _log(f"Model indiriliyor: {name} (~67 MB)...")

    def _hook(block, bs, total):
        if total > 0:
            _prog(min(30, int(block * bs * 30 / total)))

    try:
        urllib.request.urlretrieve(url, path, _hook)
        size_mb = os.path.getsize(path) / 1024 / 1024
        if size_mb < 1.0:
            raise RuntimeError("İndirilen dosya bozuk/eksik.")
        _log(f"✓ Model hazır: {name} ({size_mb:.1f} MB)")
        _prog(0)
        return path
    except Exception as ex:
        try: os.unlink(path)
        except Exception: pass
        raise RuntimeError(f"Model indirilemedi ({name}): {ex}")


# ── MDX-Net inference ─────────────────────────────────────────────────────────

def mdx_separate(model_path_: str, audio_path: str,
                 providers: list[str],
                 output_type: str = "vocals",
                 progress_cb=None, log_cb=None) -> tuple:
    """
    MDX-Net ONNX modeli ile kaynak ayrıştırması.

    output_type="vocals"
        Model vokal stem'ini tahmin eder → direkt döndürülür.
        Örn: Kim_Vocal_2, Voc_FT, KARA_2, Reverb

    output_type="instrumental"
        Model enstrüman stem'ini tahmin eder.
        vocals = audio - instrumental  şeklinde hesaplanır.
        Örn: Inst_HQ_1, Inst_HQ_3, Inst_HQ_4

    Döndürür: (primary_stem, secondary_stem, sample_rate)
        primary_stem   = modelin hedeflediği stem (vokal VEYA enstrüman)
        secondary_stem = diğeri (audio - primary)
    """
    import numpy as np
    import librosa
    import onnxruntime as ort

    def _log(m):
        if log_cb: log_cb(m)
    def _prog(p):
        if progress_cb: progress_cb(p)

    # ── Ses yükle ─────────────────────────────────────────────────────────────
    _log("Ses dosyası yükleniyor...")
    audio, sr = librosa.load(audio_path, sr=44100, mono=False)
    if audio.ndim == 1:
        audio = np.stack([audio, audio])
    _prog(8)

    # ── Model yükle ───────────────────────────────────────────────────────────
    _log("ONNX modeli yükleniyor...")
    opts = ort.SessionOptions()
    opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    if providers and providers[0] == "DmlExecutionProvider":
        opts.execution_mode     = ort.ExecutionMode.ORT_SEQUENTIAL
        opts.enable_mem_pattern = False

    sess        = ort.InferenceSession(model_path_, sess_options=opts,
                                       providers=providers)
    inp         = sess.get_inputs()[0]
    _, _, dim_f, dim_t = inp.shape
    n_out       = sess.get_outputs()[0].shape[1]
    n_fft       = (dim_f - 1) * 2
    hop_len     = 1024

    _log(f"Model: n_fft={n_fft}, dim_f={dim_f}, dim_t={dim_t}, "
         f"out_ch={n_out}, output_type={output_type}, provider={providers[0]}")
    _prog(15)

    # ── STFT / iSTFT ──────────────────────────────────────────────────────────
    def _stft(y):
        return librosa.stft(y, n_fft=n_fft, hop_length=hop_len,
                            window="hann", center=True)

    def _istft(s):
        return librosa.istft(s, hop_length=hop_len, window="hann",
                             n_fft=n_fft, center=True, length=audio.shape[1])

    spec_L       = _stft(audio[0])
    spec_R       = _stft(audio[1])
    total_frames = spec_L.shape[1]
    _prog(25)

    # ── %50 Overlap-Add (Hann pencereli) — chunk sınırlarında artefakt yok ───
    step      = dim_t // 2
    out_L     = np.zeros((dim_f, total_frames), dtype=complex)
    out_R     = np.zeros((dim_f, total_frames), dtype=complex)
    weight    = np.zeros(total_frames, dtype=np.float32)
    hann      = np.hanning(dim_t).astype(np.float32)
    positions = list(range(0, total_frames, step))

    for ci, i in enumerate(positions):
        end  = min(i + dim_t, total_frames)
        alen = end - i

        cL = spec_L[:, i:end]
        cR = spec_R[:, i:end]
        if alen < dim_t:
            cL = np.pad(cL, ((0, 0), (0, dim_t - alen)))
            cR = np.pad(cR, ((0, 0), (0, dim_t - alen)))

        x    = np.stack([cL.real, cL.imag, cR.real, cR.imag],
                        axis=0)[np.newaxis].astype(np.float32)
        pred = sess.run(None, {inp.name: x})[0]   # (1, n_out, dim_f, dim_t)

        n = pred.shape[1]
        if n >= 4:
            vL = (pred[0, 0] + 1j * pred[0, 1]).astype(complex)
            vR = (pred[0, 2] + 1j * pred[0, 3]).astype(complex)
        elif n == 2:
            vL = (pred[0, 0] + 1j * pred[0, 1]).astype(complex)
            vR = vL.copy()
        else:
            mag = pred[0, 0].astype(np.float32)
            vL  = mag * np.exp(1j * np.angle(cL))
            vR  = mag * np.exp(1j * np.angle(cR))

        w = hann[:alen]
        out_L[:, i:end] += vL[:, :alen] * w
        out_R[:, i:end] += vR[:, :alen] * w
        weight[i:end]   += w
        _prog(25 + int(65 * (ci + 1) / len(positions)))

    weight = np.maximum(weight, 1e-8)
    out_L /= weight
    out_R /= weight

    _prog(92)
    _log("iSTFT uygulanıyor...")
    primary = np.stack([_istft(out_L), _istft(out_R)])   # model çıktısı

    # ── output_type'a göre vokal/enstrüman ata ────────────────────────────────
    if output_type == "instrumental":
        # Model enstrümanı tahmin etti → vokal = orijinal - enstrüman
        _log("ℹ️  Inst modeli: vokal = orijinal − enstrüman")
        instrumental = primary
        vocals       = audio - instrumental
    else:
        # Model vokali tahmin etti (varsayılan)
        vocals       = primary
        instrumental = audio - vocals

    _prog(97)
    return vocals, instrumental, 44100


# ── VAD — Sessizlik kaldırma ──────────────────────────────────────────────────

def compact_vocals(vocals: "np.ndarray", sr: int,
                   pause_sec: float = 1.0,
                   thresh_db: int   = -35,
                   min_seg_sec: float = 0.3,
                   log_cb=None) -> "np.ndarray":
    """
    Vokal dizisindeki sessiz bölgeleri çıkarır,
    ses segmentleri arasına `pause_sec` sn boşluk ekler.
    """
    import numpy as np

    def _log(m):
        if log_cb: log_cb(m)

    n_samples  = vocals.shape[1]
    frame_len  = int(sr * 0.030)            # 30 ms
    n_frames   = n_samples // frame_len
    min_smp    = int(min_seg_sec * sr)
    threshold  = 10 ** (thresh_db / 20.0)

    mono = (vocals[0] + vocals[1]) / 2.0
    rms  = np.array([
        np.sqrt(np.mean(mono[f * frame_len:(f + 1) * frame_len] ** 2 + 1e-12))
        for f in range(n_frames)
    ], dtype=np.float32)

    active = rms > threshold

    # 400 ms'den kısa iç sessizlikleri kapat
    fill = max(1, int(400 / 30))
    for i in range(len(active) - fill):
        if active[i] and active[i + fill]:
            active[i:i + fill] = True

    segments = []
    in_seg, s_start = False, 0
    for fi, act in enumerate(active):
        if act and not in_seg:
            in_seg, s_start = True, fi * frame_len
        elif not act and in_seg:
            in_seg = False
            end = fi * frame_len
            if end - s_start >= min_smp:
                segments.append((s_start, end))
    if in_seg:
        end = n_frames * frame_len
        if end - s_start >= min_smp:
            segments.append((s_start, end))

    if not segments:
        _log("⚠ Ses segmenti bulunamadı — orijinal korunuyor")
        return vocals

    orig_sec  = n_samples / sr
    kept_sec  = sum(e - s for s, e in segments) / sr
    _log(f"✓ {len(segments)} segment  |  korunan: {kept_sec:.1f}s  |  "
         f"çıkarılan: {orig_sec - kept_sec:.1f}s")

    gap  = np.zeros((2, int(pause_sec * sr)), dtype=np.float32)
    fade = min(int(0.008 * sr), 256)
    parts = []
    for idx, (s, e) in enumerate(segments):
        seg = vocals[:, s:e].copy().astype(np.float32)
        if fade > 0 and seg.shape[1] > fade * 2:
            ramp = np.linspace(0.0, 1.0, fade, dtype=np.float32)
            seg[:, :fade]  *= ramp
            seg[:, -fade:] *= ramp[::-1]
        parts.append(seg)
        if idx < len(segments) - 1:
            parts.append(gap)

    return np.concatenate(parts, axis=1)
