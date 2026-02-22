"""
SQLite veritabanı katmanı.
~/.vocal_extractor.db dosyasında saklanır.

Tablolar:
  settings  — anahtar/değer ayarlar (son klasörler, tema vb.)
  history   — indirme ve temizleme geçmişi
  sessions  — uygulama oturumları
  logs      — oturum başına log kayıtları
"""
import sqlite3
from pathlib import Path
from datetime import datetime

# Veritabanı proje içindeki database/ klasöründe saklanır
SCRIPT_DIR = Path(__file__).parent.parent   # projenin kök dizini
DB_DIR     = SCRIPT_DIR / "database"
DB_DIR.mkdir(exist_ok=True)                # klasör yoksa oluştur
DB_PATH    = str(DB_DIR / "vocal_extractor.db")

# Aktif oturum ID'si (main.py tarafından başlatılır)
CURRENT_SESSION_ID: int | None = None


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    """Tabloları oluştur (yoksa)."""
    with _conn() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS history (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                type      TEXT NOT NULL,
                title     TEXT NOT NULL DEFAULT '',
                path      TEXT NOT NULL DEFAULT '',
                out_dir   TEXT NOT NULL DEFAULT '',
                fmt       TEXT NOT NULL DEFAULT '',
                quality   TEXT NOT NULL DEFAULT '',
                status    TEXT NOT NULL DEFAULT 'done',
                date      TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT NOT NULL,
                ended_at   TEXT
            );

            CREATE TABLE IF NOT EXISTS logs (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                timestamp  TEXT NOT NULL,
                level      TEXT NOT NULL DEFAULT '',
                message    TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );
        """)


# ── Settings ──────────────────────────────────────────────────────────────────

def get_setting(key: str, default: str = "") -> str:
    with _conn() as c:
        row = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default


def set_setting(key: str, value: str):
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",
                  (key, str(value)))
        c.commit()


# ── History ───────────────────────────────────────────────────────────────────

def add_history(entry: dict):
    """
    entry anahtarları: type, title, path, out_dir, fmt, quality, status
    """
    entry.setdefault("date", datetime.now().strftime("%Y-%m-%d %H:%M"))
    entry.setdefault("status", "done")
    with _conn() as c:
        c.execute(
            "INSERT INTO history(type,title,path,out_dir,fmt,quality,status,date)"
            " VALUES(:type,:title,:path,:out_dir,:fmt,:quality,:status,:date)",
            entry)
        c.commit()


def get_history(limit: int = 300) -> list[dict]:
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]


def clear_history():
    with _conn() as c:
        c.execute("DELETE FROM history")
        c.commit()


# ── Sessions ──────────────────────────────────────────────────────────────────

def start_session() -> int:
    global CURRENT_SESSION_ID
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO sessions(started_at) VALUES(?)",
            (datetime.now().isoformat(),))
        c.commit()
        CURRENT_SESSION_ID = cur.lastrowid
        return CURRENT_SESSION_ID


def end_session():
    global CURRENT_SESSION_ID
    if CURRENT_SESSION_ID is None:
        return
    with _conn() as c:
        c.execute(
            "UPDATE sessions SET ended_at=? WHERE id=?",
            (datetime.now().isoformat(), CURRENT_SESSION_ID))
        c.commit()


def get_sessions(limit: int = 100) -> list[dict]:
    with _conn() as c:
        rows = c.execute(
            "SELECT s.*, COUNT(l.id) AS log_count "
            "FROM sessions s "
            "LEFT JOIN logs l ON l.session_id = s.id "
            "GROUP BY s.id "
            "ORDER BY s.id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]


def get_session_logs(session_id: int) -> list[dict]:
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM logs WHERE session_id=? ORDER BY id",
            (session_id,)).fetchall()
        return [dict(r) for r in rows]


# ── Logs ──────────────────────────────────────────────────────────────────────

def log_entry(level: str, message: str):
    """Mevcut oturuma log ekle."""
    if CURRENT_SESSION_ID is None:
        return
    with _conn() as c:
        c.execute(
            "INSERT INTO logs(session_id,timestamp,level,message) VALUES(?,?,?,?)",
            (CURRENT_SESSION_ID,
             datetime.now().strftime("%H:%M:%S"),
             level, message))
        c.commit()
