import sqlite3
from pathlib import Path
from config import DEFAULT_PROFILE_PING_RULES

DB_PATH = Path("data/checkouts.db")

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def initialize_database():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS checkouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT, item TEXT, price TEXT, site TEXT,
            quantity TEXT, profile TEXT, cancel_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS profile_links (
            keyword TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL
        )""")
        for keyword, user_id in DEFAULT_PROFILE_PING_RULES.items():
            c.execute("INSERT OR IGNORE INTO profile_links VALUES (?, ?)",
                      (keyword.lower().strip(), user_id))

def save_checkout(x):
    with connect() as c:
        c.execute("""INSERT INTO checkouts
        (status,item,price,site,quantity,profile,cancel_reason)
        VALUES (?,?,?,?,?,?,?)""",
        (x.status,x.item,x.price,x.site,x.quantity,x.profile,x.cancel_reason))

def set_profile_link(keyword, user_id):
    with connect() as c:
        c.execute("""INSERT INTO profile_links(keyword,user_id) VALUES(?,?)
        ON CONFLICT(keyword) DO UPDATE SET user_id=excluded.user_id""",
        (keyword.lower().strip(), user_id))

def remove_profile_link(keyword):
    with connect() as c:
        cur = c.execute("DELETE FROM profile_links WHERE keyword=?",
                        (keyword.lower().strip(),))
        return cur.rowcount > 0

def get_profile_links():
    with connect() as c:
        return c.execute("SELECT keyword,user_id FROM profile_links ORDER BY keyword").fetchall()

def find_user_for_profile(profile):
    normalized = (profile or "").lower().strip()
    with connect() as c:
        rows = c.execute("SELECT keyword,user_id FROM profile_links ORDER BY LENGTH(keyword) DESC").fetchall()
    for keyword, user_id in rows:
        if keyword in normalized:
            return int(user_id)
    return None
