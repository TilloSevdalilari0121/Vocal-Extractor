# 🎵 Vocal Extractor Pro v2.0

Türkçe arayüzlü, yapay zeka destekli ses temizleme ve YouTube indirme masaüstü uygulaması.

**Test ortamı:** AMD Radeon 8060S (DirectML, 96 GB GPU belleği), Windows 11, Python 3.13

---

## ✨ Özellikler

| Özellik | Detay |
|---|---|
| 🎤 AI Ses Temizleme | MDX-Net ONNX modelleri — PyTorch gerektirmez |
| ▶️ YouTube İndirme | MP3 / WAV / FLAC / MP4 desteği |
| 🔇 Sessizlik Temizleme | Müzik arası boşlukları siler, segmentler arası 0.5–3 sn ara bırakır |
| 🖥️ AMD GPU Desteği | DirectML (DirectX 12) ile AMD / Intel / NVIDIA GPU hızlandırma |
| 🎨 9 Tema | macOS Tahoe, Dracula, Nord, Sunset, Okyanus ve daha fazlası |
| 🗄️ SQLite Veritabanı | Geçmiş, oturumlar ve ayarlar kalıcı olarak saklanır |
| 📋 Oturum Kaydı | Her işlem canlı loglanır, geçmişten tekrar izlenebilir |

---

## 🖼️ Sekmeler

```
┌─────────────────────────────────────────────────────────────────┐
│  🎵 İndir   🎛 Temizle   📋 Geçmiş   🖥 Oturumlar   ⚙️ Ayarlar  │
└─────────────────────────────────────────────────────────────────┘
```

### 🎵 İndirme Sekmesi
- YouTube URL'si yapıştır → MP3, WAV, FLAC veya MP4 olarak indir
- Kalite seçimi: 128 kbps – 320 kbps / 360p – 1080p
- ffmpeg yoksa otomatik indirilir (~130 MB, tek seferlik)

### 🎛 Temizleme Sekmesi
- Ses dosyası seç (MP3, WAV, FLAC, M4A, OGG, AAC desteklenir)
- AI modeli seç (7 farklı model — aşağıya bakınız)
- Çıktı formatı: MP3 / WAV / FLAC
- **Sessizlik Temizleme:** müzik aralarını silerek yalnızca ses bölümlerini birleştirir

### 📋 Geçmiş Sekmesi
- İndirme ve temizleme işlemleri listelenir
- Dosyayı aç / klasörü aç butonları
- Tüm geçmişi temizle

### 🖥 Oturumlar Sekmesi
- Her çalıştırma ayrı oturum olarak kaydedilir
- Canlı log görüntüleme, oturumlar arası geçiş
- Log'ları panoya kopyala

---

## 🤖 AI Modeller

Modeller ilk kullanımda `models/` klasörüne otomatik indirilir (~67 MB/model).

### 🎤 Vokal Ayırma — Sesi Koru, Müziği Sil

| Model | Açıklama | Performans |
|---|---|---|
| **Kim Vocal 2** | Genel amaçlı vokal modeli | ⭐⭐⭐⭐ |
| **Voc FT** | Kim Vocal 2'nin gelişmiş fine-tuned versiyonu | ⭐⭐⭐⭐+ |

> **Not:** Her iki model de Batı pop/rock veri setiyle eğitilmiştir. Zurna, ney, def, erbane gibi Türk halk enstrümanları kısmen müzik olarak sınıflandırılabilir — bu model mimarisinin bir sınırıdır.

### 🎸 Müzik Temizleme — Müziği Koru, Sesi Sil

| Model | Açıklama | Performans |
|---|---|---|
| **Inst HQ 4** | En yeni ve en kaliteli Inst modeli | ⭐⭐⭐⭐ |
| **Inst HQ 3** | Yoğun müziklerde sınırlı; hafif müziklerde etkili | ⭐⭐⭐ |
| **Inst HQ 1** | HQ 3'e alternatif | ⭐⭐⭐ |

> **Not:** Bu modeller enstrüman stem'ini tahmin eder. Vokal = orijinal − enstrüman formülüyle elde edilir.

### 🎹 Özel Amaçlar

| Model | Açıklama |
|---|---|
| **Karaoke KARA_2** | Ön vokal silinir; arka koro + enstrüman kalır |
| **Reverb FoxJoy** | Yankı/reverb azaltır; sesi öne alır, müziği arka plana atar |

---

## 🔇 Sessizlik Temizleme

Vokal ayrıştırma sonrası müzik araları ve sessiz bölgeler otomatik silinir.

| Ayar | Seçenekler | Varsayılan |
|---|---|---|
| Araya eklenecek sessizlik | 0.5 / 1 / 1.5 / 2 / 3 sn | 1 sn |
| Sessizlik eşiği | −25 / −35 / −45 / −55 dB | −35 dB |

**Nasıl çalışır:**
1. Her 30 ms frame için RMS hesaplanır
2. Eşiğin altındaki bölgeler sessiz sayılır
3. 400 ms'den kısa iç boşluklar kapatılır (nefes / kısa duraklama korunur)
4. 300 ms'den kısa segmentler atılır
5. Her segmentin başına / sonuna 8 ms fade eklenir (patlama önler)
6. Segmentler seçilen boşlukla birleştirilir

---

## 📁 Proje Yapısı

```
📦 vocal-extractor-pro/
├── main.py                  ← Giriş noktası
├── requirements.txt         ← Python bağımlılıkları
│
├── app/
│   ├── window.py            ← Ana pencere, sekme yöneticisi
│   ├── download_tab.py      ← YouTube indirme sekmesi
│   ├── clean_tab.py         ← Ses temizleme sekmesi
│   ├── history_tab.py       ← Geçmiş sekmesi
│   ├── session_tab.py       ← Oturum / log görüntüleyici
│   ├── settings_tab.py      ← Ayarlar sekmesi
│   │
│   ├── workers.py           ← QThread: DownloadWorker, CleanWorker
│   ├── worker_mdx.py        ← MDX-Net inference, VAD, model kataloğu
│   ├── worker_utils.py      ← ffmpeg, ONNX provider, sabitler
│   │
│   ├── database.py          ← SQLite: ayarlar, geçmiş, oturumlar, log
│   ├── themes.py            ← 9 tema (QSS tabanlı)
│   └── widgets.py           ← Paylaşılan widget'lar
│
├── database/
│   └── vocal_extractor.db   ← SQLite veritabanı (otomatik oluşturulur)
│
├── models/                  ← ONNX modelleri (otomatik indirilir)
│   ├── Kim_Vocal_2.onnx
│   ├── UVR-MDX-NET-Voc_FT.onnx
│   ├── UVR-MDX-NET-Inst_HQ_4.onnx
│   ├── UVR-MDX-NET-Inst_HQ_3.onnx
│   ├── UVR-MDX-NET-Inst_HQ_1.onnx
│   ├── UVR_MDXNET_KARA_2.onnx
│   └── Reverb_HQ_By_FoxJoy.onnx
│
└── ffmpeg_bin/              ← ffmpeg (otomatik indirilir)
    ├── ffmpeg.exe
    └── ffprobe.exe
```

---

## ⚙️ Kurulum

### 1. Python 3.11 – 3.13

```bash
python --version   # 3.11+ olduğundan emin ol
```

### 2. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

`requirements.txt` içeriği:

```
PyQt6>=6.8.0
yt-dlp>=2025.1.1
onnxruntime-directml>=1.20.0
librosa>=0.10.0
soundfile>=0.12.0
numpy>=1.26.0
scipy>=1.12.0
```

> **AMD / Intel GPU:** `onnxruntime-directml` DirectX 12 üzerinden GPU hızlandırması sağlar.
> GPU yoksa veya sorun çıkarsa:
> ```bash
> pip uninstall onnxruntime-directml -y
> pip install onnxruntime
> ```

### 3. Çalıştır

```bash
python main.py
```

ffmpeg ve AI modelleri ilk çalıştırmada otomatik indirilir.

---

## 🖥️ Sistem Gereksinimleri

| Bileşen | Minimum | Test Edilen |
|---|---|---|
| İşletim Sistemi | Windows 10 64-bit | Windows 11 |
| Python | 3.11 | 3.13 |
| RAM | 8 GB | 16 GB |
| GPU | DirectX 12 uyumlu (opsiyonel) | AMD Radeon 8060S |
| Disk | 2 GB (modeller için) | — |

### Test Ortamı

```
GPU:      AMD Radeon 8060S Graphics
Sürücü:   32.0.22021.1009  (13.10.2025)
DirectX:  12 (Feature Level 12.2)
GPU RAM:  96 GB adanmış + 15.8 GB paylaşılan
API:      DirectML (DmlExecutionProvider)
```

---

## 🗄️ Veritabanı

Tüm veriler proje içindeki `database/vocal_extractor.db` SQLite dosyasında saklanır.

| Tablo | İçerik |
|---|---|
| `settings` | Tema, GPU, bildirim, geçmiş ayarları |
| `history` | İndirme ve temizleme kayıtları |
| `sessions` | Uygulama oturumları (başlangıç/bitiş zamanı) |
| `logs` | Her oturuma ait detaylı işlem logları |

---

## 🎨 Temalar

9 yerleşik tema:

| Tema | Tür |
|---|---|
| macOS Tahoe Light | Açık |
| macOS Tahoe Dark | Koyu |
| Dracula | Koyu |
| Nord | Koyu |
| Sunset | Koyu |
| Blue Ocean | Koyu |
| Forest | Koyu |
| Siber | Koyu |
| Okyanus | Koyu |

---

## 🔧 Teknik Detaylar

### MDX-Net Inference

- **STFT parametreleri:** `n_fft = (dim_f - 1) × 2`, `hop_length = 1024`
- **Overlap-Add:** %50 overlap, Hann penceresi — chunk sınırlarında artefakt yok
- **output_type:**
  - `vocals` → model çıktısı direkt vokal
  - `instrumental` → vokal = orijinal − model çıktısı
- **Stereo:** Sol/Sağ kanal bağımsız işlenir, complex spektrogram

### GPU Öncelik Sırası

```
DmlExecutionProvider (AMD/Intel/NVIDIA DirectML)
  → CUDAExecutionProvider (NVIDIA CUDA)
    → CPUExecutionProvider (fallback)
```

---

## 📝 Sürüm Geçmişi

### v2.0
- SQLite veritabanı katmanı eklendi (JSON'dan geçiş)
- 9 tema sistemi yeniden yazıldı
- Oturum takibi ve canlı log görüntüleyici
- 7 MDX-Net modeli desteği
- Sessizlik temizleme (VAD) özelliği
- `output_type` düzeltmesi — Inst modelleri artık doğru çalışıyor
- `workers.py` 3 modüle bölündü: `worker_utils`, `worker_mdx`, `workers`
- Overlap-Add inference — chunk artefaktı giderildi
- STFT shape mismatch düzeltmesi (3072 vs 3073 bin)

### v1.0
- Temel YouTube indirme
- Kim Vocal 2 ile tek model desteği
- JSON tabanlı ayarlar ve geçmiş

---

## 📄 Lisans

Kişisel kullanım amaçlı geliştirilmiştir.

AI modelleri [Ultimate Vocal Remover](https://github.com/Anjok07/ultimatevocalremovergui) projesi tarafından eğitilmiştir.
