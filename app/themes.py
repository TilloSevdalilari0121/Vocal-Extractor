"""
Tema paleti ve QSS üretici.

Temalar:
  Tahoe Light  — macOS 26 Tahoe açık mod (Apple HIG renkleri)
  Tahoe Dark   — macOS 26 Tahoe koyu mod
  Sunset       — Gün batımı turuncu/amber
  Blue         — Gece mavisi
  Forest       — Orman yeşili
  Dracula      — Dracula resmi paleti
  Nord         — Nord Arctic paleti
  Siber        — Siber/Matrix neon
  Okyanus      — Derin okyanus
"""

THEMES: dict[str, dict] = {

    # ── macOS 26 Tahoe Light ─────────────────────────────────────────────────
    "Tahoe Light": {
        "bg":      "#F2F2F7",   # systemBackground
        "surface": "#FFFFFF",   # secondarySystemBackground
        "panel":   "#E5E5EA",   # tertiarySystemBackground
        "border":  "#C6C6C8",   # separator
        "accent":  "#007AFF",   # systemBlue
        "accent2": "#5856D6",   # systemIndigo
        "text":    "#000000",   # label
        "muted":   "#6C6C70",   # secondaryLabel
        "success": "#34C759",   # systemGreen
        "error":   "#FF3B30",   # systemRed
        "warning": "#FF9500",   # systemOrange
        "inputbg": "#FFFFFF",
        "icon_bg": "#E5E5EA",
    },

    # ── macOS 26 Tahoe Dark ──────────────────────────────────────────────────
    "Tahoe Dark": {
        "bg":      "#1C1C1E",   # systemBackground dark
        "surface": "#2C2C2E",   # secondarySystemBackground dark
        "panel":   "#3A3A3C",   # tertiarySystemBackground dark
        "border":  "#48484A",   # separator dark
        "accent":  "#0A84FF",   # systemBlue dark
        "accent2": "#5E5CE6",   # systemIndigo dark
        "text":    "#FFFFFF",
        "muted":   "#8E8E93",   # secondaryLabel dark
        "success": "#32D74B",   # systemGreen dark
        "error":   "#FF453A",   # systemRed dark
        "warning": "#FF9F0A",   # systemOrange dark
        "inputbg": "#1C1C1E",
        "icon_bg": "#3A3A3C",
    },

    # ── Sunset ───────────────────────────────────────────────────────────────
    "Sunset": {
        "bg":      "#1A0800",
        "surface": "#2D1200",
        "panel":   "#3D1800",
        "border":  "#5C2800",
        "accent":  "#FF6B35",
        "accent2": "#FFB347",
        "text":    "#FFE8D6",
        "muted":   "#A06040",
        "success": "#4ADE80",
        "error":   "#FF5555",
        "warning": "#FFB86C",
        "inputbg": "#150600",
        "icon_bg": "#3D1800",
    },

    # ── Blue ─────────────────────────────────────────────────────────────────
    "Blue": {
        "bg":      "#020B18",
        "surface": "#071526",
        "panel":   "#0B1F38",
        "border":  "#1A3A5C",
        "accent":  "#38BDF8",
        "accent2": "#818CF8",
        "text":    "#E0F2FE",
        "muted":   "#4A7090",
        "success": "#4ADE80",
        "error":   "#F87171",
        "warning": "#FBBF24",
        "inputbg": "#030D1F",
        "icon_bg": "#0B1F38",
    },

    # ── Forest ───────────────────────────────────────────────────────────────
    "Forest": {
        "bg":      "#021005",
        "surface": "#071A09",
        "panel":   "#0D250F",
        "border":  "#1A4020",
        "accent":  "#4ADE80",
        "accent2": "#86EFAC",
        "text":    "#DCFCE7",
        "muted":   "#3D7050",
        "success": "#4ADE80",
        "error":   "#F87171",
        "warning": "#FBBF24",
        "inputbg": "#020C04",
        "icon_bg": "#0D250F",
    },

    # ── Dracula (resmi palet) ─────────────────────────────────────────────────
    # https://draculatheme.com/contribute
    "Dracula": {
        "bg":      "#282A36",   # Background
        "surface": "#1E1F29",   # daha koyu yüzey
        "panel":   "#343746",   # Current Line
        "border":  "#44475A",   # Comment
        "accent":  "#BD93F9",   # Purple
        "accent2": "#FF79C6",   # Pink
        "text":    "#F8F8F2",   # Foreground
        "muted":   "#6272A4",   # Comment blue
        "success": "#50FA7B",   # Green
        "error":   "#FF5555",   # Red
        "warning": "#FFB86C",   # Orange
        "inputbg": "#21222C",
        "icon_bg": "#343746",
    },

    # ── Nord (resmi palet) ────────────────────────────────────────────────────
    # https://www.nordtheme.com
    "Nord": {
        "bg":      "#2E3440",   # nord0
        "surface": "#3B4252",   # nord1
        "panel":   "#434C5E",   # nord2
        "border":  "#4C566A",   # nord3
        "accent":  "#88C0D0",   # nord8  (frost)
        "accent2": "#81A1C1",   # nord9
        "text":    "#ECEFF4",   # nord6
        "muted":   "#7A8899",
        "success": "#A3BE8C",   # nord14 (green)
        "error":   "#BF616A",   # nord11 (red)
        "warning": "#EBCB8B",   # nord13 (yellow)
        "inputbg": "#2B3040",
        "icon_bg": "#434C5E",
    },

    # ── Siber ─────────────────────────────────────────────────────────────────
    "Siber": {
        "bg":      "#020308",
        "surface": "#060612",
        "panel":   "#0A0A1E",
        "border":  "#151530",
        "accent":  "#00FF94",   # neon yeşil
        "accent2": "#00E5FF",   # neon cyan
        "text":    "#C8FFE8",
        "muted":   "#1E604A",
        "success": "#00FF94",
        "error":   "#FF004F",
        "warning": "#FFD600",
        "inputbg": "#040408",
        "icon_bg": "#0A0A1E",
    },

    # ── Okyanus ───────────────────────────────────────────────────────────────
    "Okyanus": {
        "bg":      "#020D15",
        "surface": "#051A2A",
        "panel":   "#082438",
        "border":  "#0F3550",
        "accent":  "#06B6D4",
        "accent2": "#22D3EE",
        "text":    "#CFFAFE",
        "muted":   "#1E6080",
        "success": "#4ADE80",
        "error":   "#F87171",
        "warning": "#FBBF24",
        "inputbg": "#010A10",
        "icon_bg": "#082438",
    },
}

# Tema dot renkleri (title bar'daki küçük daireler için)
THEME_DOTS = {
    "Tahoe Light": "#007AFF",
    "Tahoe Dark":  "#0A84FF",
    "Sunset":      "#FF6B35",
    "Blue":        "#38BDF8",
    "Forest":      "#4ADE80",
    "Dracula":     "#BD93F9",
    "Nord":        "#88C0D0",
    "Siber":       "#00FF94",
    "Okyanus":     "#06B6D4",
}


def _luminance(hex_color: str) -> float:
    """0–255 arası ağırlıklı parlaklık."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return 0.299 * r + 0.587 * g + 0.114 * b


def _btn_text(accent: str) -> str:
    """Accent renginin üzerinde okunabilir buton metin rengi."""
    return "#000000" if _luminance(accent) > 145 else "#FFFFFF"


def build_qss(t: dict) -> str:
    bt = _btn_text(t["accent"])
    bt2 = _btn_text(t["accent2"])
    icon_bg = t.get("icon_bg", t["panel"])

    # Tahoe Light için özel gölge / radius artırımı
    is_light = _luminance(t["bg"]) > 200

    return f"""
/* ═══════════════════════════════════════════════════════
   VOCAL EXTRACTOR PRO  –  Tema QSS
════════════════════════════════════════════════════════ */

/* ── Temel ──────────────────────────────────────────── */
QMainWindow, QDialog {{
    background: {t['bg']};
}}
QWidget {{
    background: transparent;
    color: {t['text']};
    font-family: {'SF Pro Display' if is_light else 'Segoe UI'}, 'Segoe UI', sans-serif;
    font-size: 13px;
}}
QScrollArea, QStackedWidget {{
    background: transparent;
    border: none;
}}

/* ── Kaydırma çubuğu ────────────────────────────────── */
QScrollBar:vertical {{
    background: {t['panel']};
    width: 6px;
    border-radius: 3px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {t['border']};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {t['muted']};
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ height: 0; }}

/* ── Başlık çubuğu ──────────────────────────────────── */
#titleBar {{
    background: {t['surface']};
    border-bottom: 1px solid {t['border']};
}}
#appTitle {{
    color: {t['muted']};
    font-size: 11px;
    font-family: 'Consolas', monospace;
    letter-spacing: 2px;
}}
#appLogo {{
    color: {t['accent']};
    font-size: 15px;
    font-weight: bold;
}}

/* ── Tab bar ────────────────────────────────────────── */
#tabBar {{
    background: {t['surface']};
    border-bottom: 1px solid {t['border']};
}}
#tabBtn {{
    background: transparent;
    color: {t['muted']};
    border: none;
    border-bottom: 2px solid transparent;
    padding: 11px 22px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
}}
#tabBtn:hover {{
    color: {t['text']};
    background: transparent;
}}
#tabBtn[active="true"] {{
    color: {t['accent']};
    border-bottom: 2px solid {t['accent']};
    background: transparent;
}}

/* ── Kart / panel ───────────────────────────────────── */
#card {{
    background: {t['surface']};
    border: 1px solid {t['border']};
    border-radius: {'14px' if is_light else '12px'};
}}
#sectionLabel {{
    color: {t['muted']};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    font-family: 'Consolas', monospace;
}}
#panelBg {{
    background: {t['bg']};
}}
#sidePanelBg {{
    background: {t['surface']};
    border-right: 1px solid {t['border']};
}}

/* ── Input ──────────────────────────────────────────── */
QLineEdit {{
    background: {t['inputbg']};
    border: {'1.5' if is_light else '1.5'}px solid {t['border']};
    border-radius: {'10px' if is_light else '8px'};
    padding: 10px 14px;
    color: {t['text']};
    font-size: 13px;
    selection-background-color: {t['accent']};
}}
QLineEdit:focus {{
    border: 1.5px solid {t['accent']};
    {'background: #FFFFFF;' if is_light else ''}
}}
QLineEdit:read-only {{
    color: {t['muted']};
}}

/* ── ComboBox ───────────────────────────────────────── */
QComboBox {{
    background: {t['inputbg']};
    border: 1.5px solid {t['border']};
    border-radius: {'10px' if is_light else '8px'};
    padding: 8px 14px;
    color: {t['text']};
    font-size: 12px;
    min-width: 120px;
}}
QComboBox:focus, QComboBox:hover {{
    border-color: {t['accent']};
}}
QComboBox::drop-down {{
    border: none;
    width: 30px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {t['muted']};
    margin-right: 10px;
}}
QComboBox QAbstractItemView {{
    background: {t['panel']};
    border: 1px solid {t['border']};
    border-radius: {'10px' if is_light else '8px'};
    color: {t['text']};
    selection-background-color: {t['accent']};
    selection-color: {bt};
    outline: none;
    padding: 4px;
}}

/* ── Radio / Check ──────────────────────────────────── */
QRadioButton, QCheckBox {{
    color: {t['text']};
    spacing: 8px;
    font-size: 12px;
}}
QRadioButton::indicator {{
    width: 16px; height: 16px;
    border-radius: 8px;
    border: 2px solid {t['border']};
    background: {t['inputbg']};
}}
QRadioButton::indicator:checked {{
    background: {t['accent']};
    border-color: {t['accent']};
}}
QCheckBox::indicator {{
    width: 16px; height: 16px;
    border-radius: 4px;
    border: 2px solid {t['border']};
    background: {t['inputbg']};
}}
QCheckBox::indicator:checked {{
    background: {t['accent']};
    border-color: {t['accent']};
}}

/* ── Progress bar ───────────────────────────────────── */
QProgressBar {{
    background: {t['border']};
    border-radius: 3px;
    text-align: center;
    font-size: 10px;
    color: transparent;
    max-height: 5px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {t['accent']}, stop:1 {t['accent2']});
    border-radius: 3px;
}}

/* ── Liste ──────────────────────────────────────────── */
QListWidget {{
    background: {t['inputbg']};
    border: 1px solid {t['border']};
    border-radius: {'10px' if is_light else '8px'};
    outline: none;
    padding: 4px;
}}
QListWidget::item {{
    color: {t['text']};
    padding: 8px 10px;
    border-radius: 6px;
    font-size: 12px;
}}
QListWidget::item:selected {{
    background: {t['accent']};
    color: {bt};
}}
QListWidget::item:hover:!selected {{
    background: {t['panel']};
}}

/* ── TableWidget ────────────────────────────────────── */
QTableWidget {{
    background: {t['inputbg']};
    border: 1px solid {t['border']};
    border-radius: {'10px' if is_light else '8px'};
    gridline-color: {t['border']};
    color: {t['text']};
    outline: none;
}}
QTableWidget::item:selected {{
    background: {t['accent']};
    color: {bt};
}}
QHeaderView::section {{
    background: {t['panel']};
    color: {t['muted']};
    border: none;
    border-bottom: 1px solid {t['border']};
    padding: 6px 10px;
    font-size: 11px;
    font-weight: 700;
    font-family: 'Consolas', monospace;
    letter-spacing: 1px;
}}

/* ── TextEdit / log ─────────────────────────────────── */
QTextEdit {{
    background: {t['inputbg']};
    border: 1px solid {t['border']};
    border-radius: {'10px' if is_light else '8px'};
    color: {t['text']};
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px;
    padding: 6px;
    selection-background-color: {t['accent']};
}}

/* ── Butonlar ───────────────────────────────────────── */
#primaryBtn {{
    background: {t['accent']};
    color: {bt};
    border: none;
    border-radius: {'12px' if is_light else '10px'};
    padding: 13px 28px;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 1px;
}}
#primaryBtn:hover {{
    background: {t['accent2']};
    color: {bt2};
}}
#primaryBtn:disabled {{
    background: {t['border']};
    color: {t['muted']};
}}
#secondaryBtn {{
    background: {t['panel']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: {'10px' if is_light else '8px'};
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 600;
}}
#secondaryBtn:hover {{
    border-color: {t['accent']};
    color: {t['accent']};
    background: {t['panel']};
}}
#dangerBtn {{
    background: transparent;
    color: {t['error']};
    border: 1px solid {t['error']};
    border-radius: {'10px' if is_light else '8px'};
    padding: 6px 14px;
    font-size: 11px;
    font-weight: 600;
}}
#dangerBtn:hover {{
    background: {t['error']};
    color: white;
}}
#iconBtn {{
    background: transparent;
    border: none;
    color: {t['muted']};
    font-size: 16px;
    padding: 4px 8px;
    border-radius: 6px;
}}
#iconBtn:hover {{
    color: {t['text']};
    background: {t['panel']};
}}

/* ── Durum rozetleri ────────────────────────────────── */
#badgeRunning {{
    background: rgba(251,191,36,0.15);
    color: {t['warning']};
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 10px;
    font-weight: 700;
    font-family: 'Consolas', monospace;
}}
#badgeDone {{
    background: rgba(74,222,128,0.15);
    color: {t['success']};
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 10px;
    font-weight: 700;
    font-family: 'Consolas', monospace;
}}
#badgeError {{
    background: rgba(248,113,113,0.15);
    color: {t['error']};
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 10px;
    font-weight: 700;
    font-family: 'Consolas', monospace;
}}
#badgeWaiting {{
    background: rgba(96,96,128,0.20);
    color: {t['muted']};
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 10px;
    font-weight: 700;
    font-family: 'Consolas', monospace;
}}

/* ── İş kartı ───────────────────────────────────────── */
#jobCard {{
    background: {t['surface']};
    border: 1px solid {t['border']};
    border-radius: {'14px' if is_light else '12px'};
}}
#jobIconBg {{
    background: {icon_bg};
    border-radius: 10px;
    font-size: 20px;
}}
#jobTitle {{
    font-size: 13px;
    font-weight: 700;
    color: {t['text']};
}}
#jobSub {{
    font-size: 11px;
    color: {t['muted']};
    font-family: 'Consolas', monospace;
}}

/* ── Adım etiketleri ────────────────────────────────── */
#stepDone {{
    background: rgba(74,222,128,0.12);
    color: {t['success']};
    border: 1px solid {t['success']};
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    font-family: 'Consolas', monospace;
}}
#stepActive {{
    background: rgba(251,191,36,0.12);
    color: {t['warning']};
    border: 1px solid {t['warning']};
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    font-family: 'Consolas', monospace;
}}
#stepWait {{
    background: transparent;
    color: {t['muted']};
    border: 1px solid {t['border']};
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    font-family: 'Consolas', monospace;
}}

/* ── Log paneli ─────────────────────────────────────── */
#logPanel {{
    background: {t['surface']};
    border-top: 1px solid {t['border']};
}}
#logHeader {{
    background: transparent;
    border-bottom: 1px solid {t['border']};
}}
#logTitle {{
    color: {t['muted']};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    font-family: 'Consolas', monospace;
}}

/* ── Geçmiş kartı ───────────────────────────────────── */
#histCard {{
    background: {t['surface']};
    border: 1px solid {t['border']};
    border-radius: {'14px' if is_light else '10px'};
}}
#histCard:hover {{
    border-color: {t['accent']};
}}

/* ── Ayarlar ────────────────────────────────────────── */
#settingsGroup {{
    background: {t['surface']};
    border: 1px solid {t['border']};
    border-radius: {'14px' if is_light else '12px'};
}}
#settingsGroupTitle {{
    color: {t['muted']};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    font-family: 'Consolas', monospace;
    background: {t['panel']};
    border-radius: {'14px' if is_light else '12px'} {'14px' if is_light else '12px'} 0 0;
    padding: 10px 16px;
    border-bottom: 1px solid {t['border']};
}}

/* ── Oturum kartı ───────────────────────────────────── */
#sessionCard {{
    background: {t['surface']};
    border: 1px solid {t['border']};
    border-radius: {'10px' if is_light else '8px'};
}}
#sessionCard:hover {{
    border-color: {t['accent']};
}}
#sessionCard[active="true"] {{
    border-color: {t['accent']};
    background: {t['panel']};
}}

/* ── Status bar ─────────────────────────────────────── */
#statusBar {{
    background: {t['surface']};
    border-top: 1px solid {t['border']};
    color: {t['muted']};
    font-size: 11px;
    font-family: 'Consolas', monospace;
}}

/* ── Separator ──────────────────────────────────────── */
#separator {{
    background: {t['border']};
    max-height: 1px;
    min-height: 1px;
}}
QSplitter::handle {{
    background: {t['border']};
    width: 1px;
}}

/* ── Splitter handle hover ──────────────────────────── */
QSplitter::handle:hover {{
    background: {t['accent']};
}}
"""
