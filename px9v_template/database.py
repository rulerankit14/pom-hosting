                                                          
                                         
                                                          

import sqlite3
from config import DB_NAME

def kvz():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def fzk():
    kkk = kvz()
    cursor = kkk.cursor()

                                                          
                  
                                                          
                               
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
    
                                            
    cursor.execute("CREATE TABLE IF NOT EXISTS user_status (user_id INTEGER PRIMARY KEY, is_live INTEGER DEFAULT 1)")
    
    cursor.execute("CREATE TABLE IF NOT EXISTS stats (key TEXT PRIMARY KEY, value INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS buttons (btn_id INTEGER PRIMARY KEY, text TEXT, price INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS menu_buttons (btn_id INTEGER PRIMARY KEY, text TEXT, link TEXT)")
    cursor.execute("""CREATE TABLE IF NOT EXISTS admin_users (
        user_id INTEGER PRIMARY KEY,
        added_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

                                                    
    cursor.execute("""CREATE TABLE IF NOT EXISTS admin_access (
        user_id INTEGER PRIMARY KEY,
        plan TEXT NOT NULL DEFAULT 'FREE',
        activated_at TEXT,
        expires_at TEXT,
        user_limit INTEGER NOT NULL DEFAULT 500,
        revenue_limit INTEGER NOT NULL DEFAULT 150,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        notified TEXT NOT NULL DEFAULT ''
    )""")

                                                                        
    cursor.execute("""CREATE TABLE IF NOT EXISTS premium_keys (
        key_id INTEGER PRIMARY KEY AUTOINCREMENT,
        key_hash TEXT UNIQUE NOT NULL,
        key_hint TEXT NOT NULL,
        plan TEXT NOT NULL,
        created_by INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        used_by INTEGER,
        used_at TEXT,
        status TEXT NOT NULL DEFAULT 'UNUSED'
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS admin_access_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        event_type TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS payment_records (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        button_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        screenshot_file_id TEXT,
        status TEXT NOT NULL DEFAULT 'pending',
        approved_by INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        approved_at TEXT,
        payment_type TEXT NOT NULL DEFAULT 'user'
    )""")
    try:
        cursor.execute("ALTER TABLE payment_records ADD COLUMN payment_type TEXT NOT NULL DEFAULT 'user'")
    except sqlite3.OperationalError:
        pass
    cursor.execute("""CREATE TABLE IF NOT EXISTS admin_log_channels (
        user_id INTEGER PRIMARY KEY,
        channel TEXT NOT NULL,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS admin_upis (
        user_id INTEGER PRIMARY KEY,
        upi_id TEXT NOT NULL,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
                                                               
    for ddl in (
        "ALTER TABLE premium_keys ADD COLUMN custom_user_limit INTEGER",
        "ALTER TABLE premium_keys ADD COLUMN custom_revenue_limit INTEGER",
        "ALTER TABLE premium_keys ADD COLUMN custom_days INTEGER",
    ):
        try:
            cursor.execute(ddl)
        except sqlite3.OperationalError:
            pass
    
    try:
        cursor.execute("ALTER TABLE menu_buttons ADD COLUMN link TEXT")
    except sqlite3.OperationalError:
        pass

    kkk.commit()

                                                          
                          
                                                          
    cursor.execute("INSERT OR IGNORE INTO stats (key, value) VALUES ('payments', 0)")
    cursor.execute("INSERT OR IGNORE INTO stats (key, value) VALUES ('total_amount', 0)")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('upi_id', 'your_upi@ybl')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('demo_link', 'https://t.me/your_demo_channel')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('contact_link', 'https://t.me/your_contact_link')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('permanent_upi_id', '')")

                                                           
    for bid, label, price in (
        (1, 'PREMIUM LITE', 199),
        (2, 'PREMIUM XD', 299),
        (3, 'PREMIUM PRO', 399),
    ):
        cursor.execute("INSERT OR REPLACE INTO buttons (btn_id, text, price) VALUES (?, ?, ?)", (bid, label, price))

    cursor.execute("INSERT OR IGNORE INTO menu_buttons (btn_id, text, link) VALUES (1, 'PREMIUM', '')")
    cursor.execute("INSERT OR IGNORE INTO menu_buttons (btn_id, text, link) VALUES (2, 'DEMO', '')")
    cursor.execute("INSERT OR IGNORE INTO menu_buttons (btn_id, text, link) VALUES (3, 'CONTACT', '')")
    
    kkk.commit()
    kkk.close()

                                                          
                                  
                                                          

def xzv(user_id: int):
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    cursor.execute("INSERT OR IGNORE INTO user_status (user_id, is_live) VALUES (?, 1)", (user_id,))
    kkk.commit()
    kkk.close()

def xqx(user_ids: list) -> int:
    if not user_ids:
        return 0
    kkk = kvz()
    cursor = kkk.cursor()
    
    data = [(int(uid),) for uid in user_ids]
    cursor.executemany("INSERT OR IGNORE INTO users (user_id) VALUES (?)", data)
    
    status_data = [(int(uid), 1) for uid in user_ids]
    cursor.executemany("INSERT OR IGNORE INTO user_status (user_id, is_live) VALUES (?, ?)", status_data)
    
    kkk.commit()
    kkk.close()
    return len(data)

def fvx(user_id: int):
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("""
        INSERT INTO user_status (user_id, is_live) 
        VALUES (?, 1) ON CONFLICT(user_id) DO UPDATE SET is_live = 1
    """, (int(user_id),))
    kkk.commit()
    kkk.close()

def fqv(user_id: int):
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("""
        INSERT INTO user_status (user_id, is_live) 
        VALUES (?, 0) ON CONFLICT(user_id) DO UPDATE SET is_live = 0
    """, (int(user_id),))
    kkk.commit()
    kkk.close()

                                                                       
def zfq(user_id: int):
    fqv(user_id)

def fxk() -> list:
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("""
        SELECT u.user_id FROM users u
        LEFT JOIN user_status s ON u.user_id = s.user_id
        WHERE s.is_live = 1 OR s.user_id IS NULL
    """)
    users = [row[0] for row in cursor.fetchall()]
    kkk.close()
    return users

def kvx() -> list:
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    kkk.close()
    return users

def fff() -> int:
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    kkk.close()
    return count

def fxf() -> int:
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM users u
        LEFT JOIN user_status s ON u.user_id = s.user_id
        WHERE s.is_live = 1 OR s.user_id IS NULL
    """)
    count = cursor.fetchone()[0]
    kkk.close()
    return count

                                                          
                     
                                                          

def fkv(key: str) -> str:
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    res = cursor.fetchone()
    kkk.close()
    return res[0] if res else ""

def qkv(key: str, value: str):
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    kkk.commit()
    kkk.close()

def ffx(key: str) -> int:
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("SELECT value FROM stats WHERE key = ?", (key,))
    res = cursor.fetchone()
    kkk.close()
    return res[0] if res else 0

def fzx(key: str):
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("UPDATE stats SET value = value + 1 WHERE key = ?", (key,))
    kkk.commit()
    kkk.close()

                                                          
                   
                                                          

def fxz() -> dict:
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("SELECT btn_id, text, link FROM menu_buttons ORDER BY btn_id ASC")
    rows = cursor.fetchall()
    kkk.close()
    return {row[0]: (row[1], row[2] if len(row) > 2 and row[2] else "") for row in rows}

def qkq(btn_id: int, text: str, link: str = ""):
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("INSERT OR REPLACE INTO menu_buttons (btn_id, text, link) VALUES (?, ?, ?)", (btn_id, text.upper(), link))
    kkk.commit()
    kkk.close()

def zvv(btn_id: int, link: str):
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("UPDATE menu_buttons SET link = ? WHERE btn_id = ?", (link, btn_id))
    kkk.commit()
    kkk.close()

def kfz(btn_id: int):
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("DELETE FROM menu_buttons WHERE btn_id = ?", (btn_id,))
    kkk.commit()
    kkk.close()

def fkk() -> list:
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("SELECT btn_id, text, price FROM buttons ORDER BY btn_id ASC")
    btns = cursor.fetchall()
    kkk.close()
    return btns

def kvf(btn_id: int):
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("SELECT text, price FROM buttons WHERE btn_id = ?", (btn_id,))
    res = cursor.fetchone()
    kkk.close()
    return res

def zvq(btn_id: int, text: str, price: int):
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("INSERT OR REPLACE INTO buttons (btn_id, text, price) VALUES (?, ?, ?)", (btn_id, text, price))
    kkk.commit()
    kkk.close()


                                                          
                   
                                                          

def kkq(user_id: int, button_id: int, amount: int, screenshot_file_id: str = "", payment_type: str = "user") -> int:
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute(
        "INSERT INTO payment_records (user_id, button_id, amount, screenshot_file_id, payment_type) VALUES (?, ?, ?, ?, ?)",
        (int(user_id), int(button_id), int(amount), screenshot_file_id, str(payment_type)),
    )
    payment_id = cursor.lastrowid
    kkk.commit()
    kkk.close()
    return int(payment_id)


def fkx(payment_id: int):
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("SELECT payment_id, user_id, button_id, amount, screenshot_file_id, status, approved_by, created_at, approved_at, payment_type FROM payment_records WHERE payment_id = ?", (int(payment_id),))
    row = cursor.fetchone()
    kkk.close()
    return row


def xvv(payment_id: int, admin_id: int):
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("SELECT user_id, button_id, amount, status FROM payment_records WHERE payment_id = ?", (int(payment_id),))
    row = cursor.fetchone()
    if not row:
        kkk.close()
        return None, False
    user_id, button_id, amount, status = row
    if status != 'pending':
        kkk.close()
        return row, False
    cursor.execute("UPDATE payment_records SET status='approved', approved_by=?, approved_at=CURRENT_TIMESTAMP WHERE payment_id=? AND status='pending'", (int(admin_id), int(payment_id)))
    if cursor.rowcount != 1:
        kkk.rollback()
        kkk.close()
        return row, False
    cursor.execute("UPDATE stats SET value=value+1 WHERE key='payments'")
    cursor.execute("UPDATE stats SET value=value+? WHERE key='total_amount'", (int(amount),))
    kkk.commit()
    kkk.close()
    return (user_id, button_id, amount, 'approved'), True


def zfx(payment_id: int):
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("SELECT user_id, button_id, amount, status FROM payment_records WHERE payment_id = ?", (int(payment_id),))
    row = cursor.fetchone()
    if not row:
        kkk.close()
        return None, False
    if row[3] != 'pending':
        kkk.close()
        return row, False
    cursor.execute("UPDATE payment_records SET status='rejected' WHERE payment_id=? AND status='pending'", (int(payment_id),))
    changed = cursor.rowcount == 1
    kkk.commit()
    kkk.close()
    return row, changed


                                                          
                                 
                                                          

def fxv() -> list:
    kkk = kvz()
    cursor = kkk.cursor()
    cursor.execute("SELECT user_id, added_at FROM admin_users ORDER BY rowid ASC")
    rows = cursor.fetchall()
    kkk.close()
    return rows

def kkx() -> int:
    from config import xkq_admin_root
    return int(xkq_admin_root)

def kqz() -> list:
    ids = [kkx()]
    for user_id, _ in fxv():
        if int(user_id) not in ids:
            ids.append(int(user_id))
    return ids

def xzq(user_id: int) -> tuple:
    user_id = int(user_id)
    if user_id == kkx():
        return False, "permanent"
    kkk = kvz(); cursor = kkk.cursor()
    cursor.execute("SELECT 1 FROM admin_users WHERE user_id = ?", (user_id,))
    if cursor.fetchone():
        kkk.close(); return False, "exists"
    cursor.execute("INSERT INTO admin_users (user_id) VALUES (?)", (user_id,))
                                                                                    
    xfz(cursor, user_id, "FREE")
    kkk.commit()
    cursor.execute("SELECT COUNT(*) FROM admin_users")
    count = cursor.fetchone()[0]
    kkk.close()
    return True, ("owner" if count == 1 else "added")

def zfz(user_id: int) -> tuple:
    user_id = int(user_id)
    if user_id == kkx():
        return False, "permanent"
    kkk = kvz(); cursor = kkk.cursor()
    cursor.execute("SELECT 1 FROM admin_users WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        kkk.close(); return False, "not_found"
    cursor.execute("DELETE FROM admin_users WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM admin_access WHERE user_id = ?", (user_id,))
    kkk.commit(); kkk.close()
    return True, "removed"


                                                          
                                      
                                                          

PREMIUM_PLANS = {
    "FREE": {"user_limit": 500, "revenue_limit": 150, "days": 2, "price": 0},
    "PREMIUM_LITE": {"user_limit": 2000, "revenue_limit": 800, "days": 7, "price": 199},
    "PREMIUM_XD": {"user_limit": 4000, "revenue_limit": 1500, "days": 14, "price": 299},
    "PREMIUM_PRO": {"user_limit": 10000, "revenue_limit": 5000, "days": 30, "price": 399},
}

def xkq(plan: str):
    return PREMIUM_PLANS.get(str(plan).upper(), PREMIUM_PLANS["FREE"])

def xfz(cursor, user_id: int, plan: str, activated_at=None):
    plan = str(plan).upper()
    p = xkq(plan)
    import datetime
    now = datetime.datetime.utcnow()
    activated = activated_at or now.strftime("%Y-%m-%d %H:%M:%S")
    expires = None
    if p["days"] is not None:
        expires = (now + datetime.timedelta(days=p["days"])).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO admin_access
        (user_id, plan, activated_at, expires_at, user_limit, revenue_limit, status, notified)
        VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE', '')
        ON CONFLICT(user_id) DO UPDATE SET
            plan=excluded.plan,
            activated_at=excluded.activated_at,
            expires_at=excluded.expires_at,
            user_limit=excluded.user_limit,
            revenue_limit=excluded.revenue_limit,
            status='ACTIVE',
            notified=''
    """, (
        int(user_id), plan, activated, expires,
        -1 if p["user_limit"] is None else int(p["user_limit"]),
        -1 if p["revenue_limit"] is None else int(p["revenue_limit"]),
    ))

def kzf(user_id: int):
    user_id = int(user_id)
    if user_id == kkx():
        return
    kkk=kvz(); cur=kkk.cursor()
    cur.execute("SELECT 1 FROM admin_users WHERE user_id=?", (user_id,))
    if cur.fetchone():
        cur.execute("SELECT 1 FROM admin_access WHERE user_id=?", (user_id,))
        if not cur.fetchone():
            cur.execute("SELECT added_at FROM admin_users WHERE user_id=?", (user_id,))
            added=cur.fetchone()
            xfz(cur, user_id, "FREE", added[0] if added else None)
    kkk.commit(); kkk.close()

def kqk(user_id: int):
    user_id=int(user_id)
    if user_id == kkx():
        return {
            "user_id": user_id, "plan": "PERMANENT", "status": "ACTIVE",
            "user_limit": None, "revenue_limit": None, "expires_at": None,
            "activated_at": None, "unrestricted": True, "users": fff(),
            "revenue": ffx("total_amount"),
        }
    kzf(user_id)
    kkk=kvz(); cur=kkk.cursor()
    cur.execute("""SELECT user_id, plan, activated_at, expires_at, user_limit,
                          revenue_limit, status, notified
                   FROM admin_access WHERE user_id=?""", (user_id,))
    row=cur.fetchone()
    if not row:
        kkk.close()
        return None

                                                                        
                                                                              
                                                                           
                                                    
    activated_at = row[2]
    if activated_at:
        cur.execute("""SELECT COUNT(DISTINCT user_id), COALESCE(SUM(amount), 0)
                       FROM payment_records
                       WHERE approved_by=? AND payment_type='user'
                         AND status='approved' AND approved_at >= ?""",
                    (user_id, activated_at))
        scoped_users, scoped_revenue = cur.fetchone()
    else:
        scoped_users, scoped_revenue = 0, 0
    kkk.close()
    return {
        "user_id": row[0], "plan": row[1], "activated_at": row[2],
        "expires_at": row[3], "user_limit": None if row[4] < 0 else row[4],
        "revenue_limit": None if row[5] < 0 else row[5],
        "status": row[6], "notified": row[7] or "", "unrestricted": False,
        "users": int(scoped_users or 0), "revenue": int(scoped_revenue or 0),
    }

def xkz(access: dict):
    if not access or access.get("unrestricted"):
        return False, ""
    import datetime
    now=datetime.datetime.utcnow()
    if access.get("expires_at"):
        try:
            if now >= datetime.datetime.strptime(access["expires_at"], "%Y-%m-%d %H:%M:%S"):
                return True, "TIME"
        except ValueError:
            pass
    if access.get("user_limit") is not None and access["users"] > access["user_limit"]:
        return True, "USERS"
    if access.get("revenue_limit") is not None and access["revenue"] > access["revenue_limit"]:
        return True, "REVENUE"
    if access.get("status") != "ACTIVE":
        return True, "EXPIRED"
    return False, ""

def fqq(user_id: int, reason: str):
    kkk=kvz(); cur=kkk.cursor()
    cur.execute("UPDATE admin_access SET status='EXPIRED' WHERE user_id=?", (int(user_id),))
    cur.execute("SELECT 1 FROM admin_access_events WHERE user_id=? AND event_type=?", (int(user_id), "LIMIT_"+reason))
    already=cur.fetchone()
    if not already:
        cur.execute("INSERT INTO admin_access_events(user_id,event_type) VALUES(?,?)", (int(user_id), "LIMIT_"+reason))
    kkk.commit(); kkk.close()
    return already is None

def kkv(plan: str, created_by: int):
    import secrets, hashlib
    plan=str(plan).upper()
    if plan not in ("PREMIUM_LITE","PREMIUM_XD","PREMIUM_PRO"):
        raise ValueError("Invalid premium plan")
    raw="PX-"+plan.replace("PREMIUM_","")+"-"+secrets.token_urlsafe(18).upper().replace("-","_")
    key_hash=hashlib.sha256(raw.encode()).hexdigest()
    hint=raw[-6:]
    kkk=kvz(); cur=kkk.cursor()
    cur.execute("""INSERT INTO premium_keys(key_hash,key_hint,plan,created_by) VALUES(?,?,?,?)""", (key_hash,hint,plan,int(created_by)))
    kkk.commit(); kkk.close()
    return raw

def kkz(user_limit: int, revenue_limit: int, days: int, created_by: int):
    import secrets, hashlib
    user_limit=int(user_limit); revenue_limit=int(revenue_limit); days=int(days)
    if user_limit <= 0 or revenue_limit < 0 or days <= 0:
        raise ValueError("USER, REVENUE and TIME must be positive values")
    raw="PX-CUSTOM-"+secrets.token_urlsafe(20).upper().replace("-","_")
    key_hash=hashlib.sha256(raw.encode()).hexdigest()
    hint=raw[-6:]
    kkk=kvz(); cur=kkk.cursor()
    cur.execute("""INSERT INTO premium_keys
        (key_hash,key_hint,plan,created_by,custom_user_limit,custom_revenue_limit,custom_days)
        VALUES(?,?,?,?,?,?,?)""", (key_hash,hint,"CUSTOM",int(created_by),user_limit,revenue_limit,days))
    kkk.commit(); kkk.close()
    return raw

def zkz(user_id: int, raw_key: str):
    import hashlib
    raw_key=str(raw_key).strip()
    if not raw_key:
        return False, "INVALID", None
    key_hash=hashlib.sha256(raw_key.encode()).hexdigest()
    kkk=kvz(); cur=kkk.cursor()
    cur.execute("""SELECT key_id, plan, status, custom_user_limit, custom_revenue_limit, custom_days
                   FROM premium_keys WHERE key_hash=?""", (key_hash,))
    row=cur.fetchone()
    if not row:
        kkk.close(); return False, "INVALID", None
    if row[2] != "UNUSED":
        kkk.close(); return False, "USED", row[1]
    user_id=int(user_id)
    if user_id == kkx():
        kkk.close(); return False, "PERMANENT", row[1]
    cur.execute("SELECT 1 FROM admin_users WHERE user_id=?", (user_id,))
    if not cur.fetchone():
        cur.execute("INSERT INTO admin_users(user_id) VALUES(?)", (user_id,))
    if row[1] == "CUSTOM":
        import datetime
        now=datetime.datetime.utcnow()
        expires=(now + datetime.timedelta(days=int(row[5]))).strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""INSERT INTO admin_access
            (user_id,plan,activated_at,expires_at,user_limit,revenue_limit,status,notified)
            VALUES(?,?,?,?,?,?, 'ACTIVE','')
            ON CONFLICT(user_id) DO UPDATE SET plan=excluded.plan,activated_at=excluded.activated_at,
            expires_at=excluded.expires_at,user_limit=excluded.user_limit,revenue_limit=excluded.revenue_limit,
            status='ACTIVE',notified=''""", (user_id,"CUSTOM",now.strftime("%Y-%m-%d %H:%M:%S"),expires,int(row[3]),int(row[4])))
    else:
        xfz(cur, user_id, row[1])
    cur.execute("""UPDATE premium_keys SET status='USED', used_by=?, used_at=CURRENT_TIMESTAMP
                   WHERE key_id=? AND status='UNUSED'""", (user_id,row[0]))
    if cur.rowcount != 1:
        kkk.rollback(); kkk.close(); return False, "USED", row[1]
    kkk.commit(); kkk.close()
    return True, "OK", row[1]

def kvq(raw_key: str):
    import hashlib
    key_hash=hashlib.sha256(str(raw_key).strip().encode()).hexdigest()
    kkk=kvz(); cur=kkk.cursor()
    cur.execute("SELECT custom_user_limit,custom_revenue_limit,custom_days FROM premium_keys WHERE key_hash=?", (key_hash,))
    row=cur.fetchone(); kkk.close()
    return row

def zqv(user_id: int, channel: str):
    kkk=kvz(); cur=kkk.cursor()
    cur.execute("""INSERT INTO admin_log_channels(user_id,channel,updated_at) VALUES(?,?,CURRENT_TIMESTAMP)
                   ON CONFLICT(user_id) DO UPDATE SET channel=excluded.channel,updated_at=CURRENT_TIMESTAMP""", (int(user_id),str(channel)))
    kkk.commit(); kkk.close()

def kqq(user_id: int):
    kkk=kvz(); cur=kkk.cursor()
    cur.execute("SELECT channel FROM admin_log_channels WHERE user_id=?", (int(user_id),))
    row=cur.fetchone(); kkk.close()
    return row[0] if row else None

def zvx(user_id: int, upi_id: str):
    kkk=kvz(); cur=kkk.cursor()
    cur.execute("INSERT INTO admin_upis(user_id,upi_id,updated_at) VALUES(?,?,CURRENT_TIMESTAMP) ON CONFLICT(user_id) DO UPDATE SET upi_id=excluded.upi_id,updated_at=CURRENT_TIMESTAMP", (int(user_id), str(upi_id).strip()))
    kkk.commit(); kkk.close()

def kqv(user_id: int):
    kkk=kvz(); cur=kkk.cursor()
    cur.execute("SELECT upi_id FROM admin_upis WHERE user_id=?", (int(user_id),))
    row=cur.fetchone(); kkk.close()
    return row[0] if row else ""

def kxv(user_id: int):
                                                                                           
    kkk=kvz(); cur=kkk.cursor()
    cur.execute("UPDATE settings SET value=? WHERE key='upi_id'", (fkv('permanent_upi_id'),))
    kkk.commit(); kkk.close()

def zfv(user_id: int):
    kkk=kvz(); cur=kkk.cursor(); cur.execute("DELETE FROM admin_log_channels WHERE user_id=?", (int(user_id),)); kkk.commit(); kkk.close()

def fkf(key_id: int):
    kkk=kvz(); cur=kkk.cursor()
    cur.execute("SELECT plan,custom_user_limit,custom_revenue_limit,custom_days FROM premium_keys WHERE key_id=?", (int(key_id),))
    row=cur.fetchone(); kkk.close(); return row

def fkz(plan=None, limit=20):
    kkk=kvz(); cur=kkk.cursor()
    if plan:
        cur.execute("""SELECT key_hint, plan, status, created_at, used_by, used_at
                       FROM premium_keys WHERE plan=? ORDER BY key_id DESC LIMIT ?""",
                    (str(plan).upper(), int(limit)))
    else:
        cur.execute("""SELECT key_hint, plan, status, created_at, used_by, used_at
                       FROM premium_keys ORDER BY key_id DESC LIMIT ?""", (int(limit),))
    rows=cur.fetchall(); kkk.close(); return rows

def kqf():
    kkk=kvz(); cur=kkk.cursor()
    cur.execute("""SELECT a.user_id,a.plan,a.status,a.activated_at,a.expires_at,
                          a.user_limit,a.revenue_limit,a.notified
                   FROM admin_access a ORDER BY a.user_id""")
    rows=cur.fetchall(); kkk.close()
    return rows

def zzx():
    """Reset bot configuration/new admins while preserving the database data."""
    kkk = kvz(); cursor = kkk.cursor()
    cursor.execute("DELETE FROM settings")
    cursor.execute("DELETE FROM buttons")
    cursor.execute("DELETE FROM menu_buttons")
    cursor.execute("DELETE FROM admin_users")
    cursor.execute("DELETE FROM admin_access")
    cursor.execute("DELETE FROM premium_keys")
    cursor.execute("DELETE FROM admin_access_events")
    cursor.execute("INSERT INTO settings (key,value) VALUES ('upi_id','your_upi@ybl')")
    cursor.execute("INSERT INTO settings (key,value) VALUES ('demo_link','https://t.me/your_demo_channel')")
    cursor.execute("INSERT INTO settings (key,value) VALUES ('contact_link','https://t.me/your_contact_link')")
    cursor.execute("INSERT INTO settings (key,value) VALUES ('permanent_upi_id','')")
    for bid, label, price in ((1,'PREMIUM LITE',199),(2,'PREMIUM XD',299),(3,'PREMIUM PRO',399)):
        cursor.execute("INSERT INTO buttons (btn_id,text,price) VALUES (?,?,?)", (bid,label,price))
    cursor.execute("INSERT INTO menu_buttons (btn_id,text,link) VALUES (1,'PREMIUM','')")
    cursor.execute("INSERT INTO menu_buttons (btn_id,text,link) VALUES (2,'DEMO','')")
    cursor.execute("INSERT INTO menu_buttons (btn_id,text,link) VALUES (3,'CONTACT','')")
    kkk.commit(); kkk.close()

def kvv() -> dict:
    return {
        "total_users": fff(),
        "live_users": fxf(),
        "total_payments": ffx("payments"),
        "total_amount": ffx("total_amount"),
        "new_admin_count": len(fxv()),
    }
