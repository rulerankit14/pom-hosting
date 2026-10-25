import os, shutil, subprocess, sys, signal, time, secrets, hashlib, sqlite3, requests
from pathlib import Path
from cryptography.fernet import Fernet
import config, database as db

def xxq():
    try: return Fernet(config.MASTER_INSTANCE_KEY.encode())
    except Exception as e: raise RuntimeError("MASTER_INSTANCE_KEY must be a valid Fernet key.") from e

def kzx(token): return xxq().encrypt(token.encode()).decode()
def kff(value): return xxq().decrypt(value.encode()).decode()

def qfx(token):
    if ":" not in token or len(token)<20: return None
    try:
        r=requests.get(f"https://api.telegram.org/bot{token}/getMe",timeout=12)
        if r.ok and r.json().get("ok"): return r.json()["result"]
    except Exception: pass
    return None

def xkv():
    return "PX-CUSTOM-"+secrets.token_urlsafe(20).upper().replace("-","_")

def xfk(instance, raw, user_limit, revenue_limit, days, created_by):
                                                                                  
    env=os.environ.copy()
    env["BOT_TOKEN"]="000000000:PROVISIONING_PLACEHOLDER"
    env["xkq_admin_root"]=str(created_by)
    env["DB_NAME"]="bot_database.db"
    subprocess.run([sys.executable,"-c",(
        "import database,hashlib,sqlite3; database.init_db(); "
        "h=hashlib.sha256(%r.encode()).hexdigest(); c=sqlite3.connect('bot_database.db'); "
        "c.execute('INSERT INTO premium_keys(key_hash,key_hint,plan,created_by,custom_user_limit,custom_revenue_limit,custom_days) VALUES(?,?,?,?,?,?,?)',"
        "(h,%r,'CUSTOM',%d,%d,%d,%d)); c.commit(); c.close()"
    )%(raw,raw[-6:],int(created_by),int(user_limit),int(revenue_limit),int(days))],
      cwd=instance,env=env,check=True)

def qkk(instance_root, bot_token, admin_id):
    root=Path(instance_root)
    log=open(root/"runtime.log","a",encoding="utf-8")
    proc=subprocess.Popen([sys.executable,"main.py"],cwd=root,env={**os.environ,"BOT_TOKEN":bot_token,"xkq_admin_root":str(admin_id),"DB_NAME":"bot_database.db"},stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    return proc

def zzk():
    for row in db.fqx():
        if row["status"]!="RUNNING": continue
        try:
            os.kill(int(row["pid"]),0)
            continue
        except Exception: pass
        try:
            token=kff(row["bot_token_enc"])
            proc=qkk(row["instance_path"],token,row["admin_id"])
            c=db.kkk(); c.execute("UPDATE bots SET pid=? WHERE id=?",(proc.pid,row["id"])); c.commit(); c.close()
        except Exception:
            pass

def fvf():
                                                         
    while True:
        time.sleep(20)
        for row in db.fqx():
            if row["status"]!="RUNNING": continue
            try: os.kill(int(row["pid"]),0)
            except Exception:
                try:
                    token=kff(row["bot_token_enc"])
                    proc=qkk(row["instance_path"],token,row["admin_id"])
                    c=db.kkk(); c.execute("UPDATE bots SET pid=? WHERE id=?",(proc.pid,row["id"])); c.commit(); c.close()
                except Exception: pass

def zkf(owner_id, admin_id, bot_token, key_row):
    me=qfx(bot_token)
    if not me: raise ValueError("Invalid Telegram bot token or Telegram API unavailable.")
    username=me.get("username") or ""
    if not username: raise ValueError("The supplied bot token has no public username.")
    iid=secrets.token_hex(8)
    instance=Path(config.INSTANCE_ROOT)/iid
    instance.mkdir(parents=True,exist_ok=True)
    shutil.copytree(config.TEMPLATE_ROOT,instance/"bot",dirs_exist_ok=True)
    root=instance/"bot"
    env=(root/".env")
    lines=[
      f"BOT_TOKEN={bot_token}", f"xkq_admin_root={int(admin_id)}",
      f"DB_NAME=bot_database.db"
    ]
    env.write_text("\n".join(lines)+"\n",encoding="utf-8")
    premium_raw=None
    if key_row["premium_enabled"]:
        premium_raw=xkv()
        xfk(str(root),premium_raw,key_row["premium_user_limit"],key_row["premium_revenue_limit"],key_row["premium_days"],admin_id)
    proc=qkk(root,bot_token,admin_id)
    time.sleep(3)
    if proc.poll() is not None:
        try:
            proc.kill()
        except Exception:
            pass
        raise RuntimeError("PX9V process exited during startup. Check runtime.log.")
    bid=db.xzx((int(owner_id),int(me["id"]),username,kzx(bot_token),int(key_row["id"]),int(admin_id),premium_raw,
        key_row["premium_user_limit"],key_row["premium_revenue_limit"],key_row["premium_days"],str(root),proc.pid,"RUNNING"))
    return bid,username,premium_raw

def qkf(row):
    pid=row["pid"]
    if pid:
        try: os.killpg(int(pid),signal.SIGTERM)
        except Exception:
            try: os.kill(int(pid),signal.SIGTERM)
            except Exception: pass
    db.zzz(row["id"])
    if config.REVOKE_DELETE_FILES:
        shutil.rmtree(Path(row["instance_path"]).parents[0],ignore_errors=True)
