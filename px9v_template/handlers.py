import asyncio
import os
import re
import urllib.parse
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import RetryAfter, Forbidden, BadRequest, TelegramError

try:
    import qrcode
except ImportError:
    qrcode = None

import config
import database as db

users_state = {}
admin_states = {}


def kxf(upi_uri: str, filename: str = "payment_qr.png"):
    """Create a QR image locally when qrcode is installed, otherwise use the
    QR Server HTTP API as a safe fallback. This keeps customer bots usable
    even when an optional QR/Pillow wheel could not be installed.
    """
    if qrcode is not None:
        qr = qrcode.make(upi_uri)
        out = BytesIO()
        qr.save(out, format="PNG")
        out.seek(0)
        out.name = filename
        return out

    import requests
    from urllib.parse import quote
    url = (
        "https://api.qrserver.com/v1/create-qr-code/"
        f"?size=500x500&margin=10&data={quote(upi_uri, safe='')}"
    )
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    out = BytesIO(response.content)
    out.seek(0)
    out.name = filename
    return out

def zkv():
    try:
        ids=[int(config.xkq_admin_root)]
        for uid,_ in db.fxv():
            access=db.kqk(uid)
            limited,_reason=db.xkz(access)
            if not limited and access and access.get("status") == "ACTIVE":
                ids.append(int(uid))
        config.ADMINS=list(dict.fromkeys(ids))
    except Exception:
        config.ADMINS=[config.xkq_admin_root]
    return config.ADMINS

def fzf(user_id: int) -> bool:
    return int(user_id) in zkv()

def fzq(user_id: int) -> bool:
    return int(user_id) == int(config.xkq_admin_root)


async def kzk(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE, action="use this feature"):
    """Permanent Admin is unrestricted. New Admin loses every operational permission immediately after expiry/limit."""
    uid=int(xuf.effective_user.id)
    if fzq(uid): return True
    access=db.kqk(uid)
    if not access: return False
    limited,reason=db.xkz(access)
    if limited:
        await xxz(uid, access, reason, kfx.bot, notify=True)
        await xuf.effective_message.reply_text(
            "⛔ <b>ACCESS DISABLED | LIMIT HIT </b>\n\n"
            f"Your <b>{access.get('plan')}</b> access has ended because the limit/time was reached.\n"
            "💳 Payment approval, admin tools, broadcasts and other operational access are disabled.\n"
            "💎 Use <b>BUY PREMIUM PLAN</b> from /admin to purchase a new plan.", parse_mode="HTML")
        return False
    return True


async def fvk(bot):
    """Background monitor: notify Permanent Admin when a New Admin expires or crosses a limit."""
    while True:
        try:
            for row in db.fxv():
                uid = int(row[0])
                access = db.kqk(uid)
                limited, reason = db.xkz(access)
                if not limited:
                    continue
                first = db.fqq(uid, reason)
                xfx()
                zkv()
                if not first:
                    continue
                reason_text = {
                    "USERS": "User limit reached",
                    "REVENUE": "Revenue limit reached",
                    "TIME": "Premium/Free time period ended",
                    "EXPIRED": "Premium access ended",
                }.get(reason, "Premium access ended")
                try:
                    await bot.send_message(
                        chat_id=config.xkq_admin_root,
                        text=(
                            "🚨 <b>NEW ADMIN LIMIT NOTIFICATION</b>\n\n"
                            f"👤 Admin ID: <code>{uid}</code>\n"
                            f"📦 Plan: <b>{access.get('plan')}</b>\n"
                            f"⚠️ Reason: <b>{reason_text}</b>\n"
                            f"👥 Users: <b>{access.get('users')}</b> / {xkx(access.get('user_limit'))}\n"
                            f"💰 Revenue: <b>₹{access.get('revenue')}</b> / {xkx(access.get('revenue_limit'))}\n\n"
                            "🇮🇳 Hinglish: New Admin ki Free/Premium limit ya time khatam ho gaya hai. "
                            "Uska admin access ab block hai."
                        ),
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
                permanent_upi = db.fkv("permanent_upi_id")
                if permanent_upi:
                    db.qkv("upi_id", permanent_upi)
        except Exception:
            pass
        await asyncio.sleep(60)

def xfx():
    permanent_upi=db.fkv("permanent_upi_id")
    if permanent_upi:
        db.qkv("upi_id", permanent_upi)
    return permanent_upi

async def xxz(uid:int, access:dict, reason:str, bot=None, notify=True):
    first=db.fqq(uid, reason)
    xfx()
    zkv()
    if notify and first and bot:
        reason_text={"USERS":"User limit reached","REVENUE":"Revenue limit reached","TIME":"Premium/Free time period ended","EXPIRED":"Premium access ended"}.get(reason,"Premium access ended")
        try:
            await bot.send_message(chat_id=config.xkq_admin_root, text=(
                "🚨 <b>NEW ADMIN ACCESS ALERT</b>\n\n"
                f"👤 Admin ID: <code>{uid}</code>\n"
                f"📌 Plan: <b>{access.get('plan')}</b>\n"
                f"⚠️ Reason: <b>{reason_text}</b>\n"
                f"👥 Users: <b>{access.get('users')}</b> / {xkx(access.get('user_limit'))}\n"
                f"💰 Revenue: <b>₹{access.get('revenue')}</b> / {xkx(access.get('revenue_limit'))}\n\n"
                "🔒 All New Admin access disabled. Permanent Admin UPI restored."), parse_mode="HTML")
        except Exception: pass
    return first

def xkx(value):
    return "Unlimited" if value is None else str(value)

def xxv(access):
    if not access:
        return "No access record"
    return (
        f"📦 <b>Plan:</b> {access['plan']}\n"
        f"📊 <b>Users:</b> {access['users']} / {xkx(access['user_limit'])}\n"
        f"💰 <b>Revenue:</b> ₹{access['revenue']} / {xkx(access['revenue_limit'])}\n"
        f"⏳ <b>Expires:</b> {access['expires_at'] or 'Lifetime'}\n"
        f"🟢 <b>Status:</b> {access['status']}"
    )

                                                          
                                      
                                                          

BROADCAST_CONCURRENCY = 15
BROADCAST_RETRY_LIMIT = 5

broadcast_running = False

async def zqq(kfx, uid: int, source_chat_id: int, message_id: int, delay: int):
    retries = 0
    while retries < BROADCAST_RETRY_LIMIT:
        try:
            sent = await kfx.bot.copy_message(
                chat_id=uid,
                from_chat_id=source_chat_id,
                message_id=message_id
            )
                         
            kfx.application.create_task(
                kfq(kfx, uid, sent.message_id, delay)
            )
            return "success", uid

                                
        except RetryAfter as e:
            retries += 1
            wait_time = int(e.retry_after) + 1
            await asyncio.sleep(wait_time)

                                              
        except Forbidden:
            return "dead", uid

                                   
        except BadRequest as e:
            error_text = str(e).lower()
            permanent_errors = (
                "chat not found",
                "user not found",
                "bot was blocked",
                "user is deactivated",
                "forbidden"
            )
            if any(error in error_text for error in permanent_errors):
                return "dead", uid
            return "failed", uid

                               
        except TelegramError:
            retries += 1
            if retries >= BROADCAST_RETRY_LIMIT:
                return "failed", uid
            await asyncio.sleep(min(2 ** retries, 10))

                        
        except Exception:
            retries += 1
            if retries >= BROADCAST_RETRY_LIMIT:
                return "failed", uid
            await asyncio.sleep(min(2 ** retries, 10))

    return "failed", uid


async def zqx(kfx, admin_chat_id: int, users: list, source_chat_id: int, message_id: int, delay: int):
    semaphore = asyncio.Semaphore(BROADCAST_CONCURRENCY)
    sent_count = 0
    dead_count = 0
    failed_count = 0
    dead_users = []

    async def qff(uid):
        nonlocal sent_count, dead_count, failed_count
        async with semaphore:
            status, user_id = await zqq(
                kfx=kfx, uid=uid, source_chat_id=source_chat_id,
                message_id=message_id, delay=delay
            )
            if status == "success":
                sent_count += 1
            elif status == "dead":
                dead_count += 1
                dead_users.append(user_id)
            else:
                failed_count += 1

    tasks = [asyncio.create_task(qff(uid)) for uid in users]
    await asyncio.gather(*tasks)

    for uid in dead_users:
        try: db.zfq(uid)
        except Exception: pass

    try:
        await kfx.bot.send_message(
            chat_id=admin_chat_id,
            text=(
                "✅ <b>Broadcast Finished</b>\n\n"
                f"📨 Sent: <b>{sent_count}</b>\n"
                f"💀 Dead/Blocked Removed: <b>{dead_count}</b>\n"
                f"⚠️ Failed: <b>{failed_count}</b>\n"
                f"👥 Total Processed: <b>{len(users)}</b>"
            ),
            parse_mode="HTML"
        )
    except Exception:
        pass


async def qkx(kfx, admin_chat_id: int, users: list, source_chat_id: int, message_id: int, delay: int):
    global broadcast_running

    if broadcast_running:
        await kfx.bot.send_message(
            chat_id=admin_chat_id,
            text="⚠️ A broadcast is already running."
        )
        return

    broadcast_running = True
    try:
        await kfx.bot.send_message(
            chat_id=admin_chat_id,
            text=(
                "🚀 <b>Broadcast Started</b>\n\n"
                f"👥 Live Users: <b>{len(users)}</b>\n"
                "⚡ Running in background..."
            ),
            parse_mode="HTML"
        )
        await zqx(
            kfx=kfx, admin_chat_id=admin_chat_id, users=users,
            source_chat_id=source_chat_id, message_id=message_id, delay=delay
        )
    finally:
        broadcast_running = False


async def zqz(kfx, uid, file_bytes, file_path, delay):
    retries = 0
    while retries < BROADCAST_RETRY_LIMIT:
        try:
            if file_path.lower().endswith(".mp4"):
                sent = await kfx.bot.send_video(chat_id=uid, video=BytesIO(file_bytes))
            else:
                sent = await kfx.bot.send_document(chat_id=uid, document=BytesIO(file_bytes))
            
            kfx.application.create_task(kfq(kfx, uid, sent.message_id, delay))
            return "success", uid

        except RetryAfter as e:
            retries += 1
            await asyncio.sleep(int(e.retry_after) + 1)
        except Forbidden:
            return "dead", uid
        except BadRequest as e:
            error_text = str(e).lower()
            permanent_errors = ("chat not found", "user not found", "bot was blocked", "user is deactivated", "forbidden")
            if any(error in error_text for error in permanent_errors):
                return "dead", uid
            return "failed", uid
        except Exception:
            retries += 1
            if retries >= BROADCAST_RETRY_LIMIT:
                return "failed", uid
            await asyncio.sleep(min(2 ** retries, 10))
    return "failed", uid


async def zqk(kfx, admin_chat_id, users, file_path, file_bytes, delay):
    semaphore = asyncio.Semaphore(BROADCAST_CONCURRENCY)
    sent_count = 0
    dead_count = 0
    failed_count = 0
    dead_users = []

    async def qff(uid):
        nonlocal sent_count, dead_count, failed_count
        async with semaphore:
            status, user_id = await zqz(kfx=kfx, uid=uid, file_bytes=file_bytes, file_path=file_path, delay=delay)
            if status == "success":
                sent_count += 1
            elif status == "dead":
                dead_count += 1
                dead_users.append(user_id)
            else:
                failed_count += 1

    tasks = [asyncio.create_task(qff(uid)) for uid in users]
    await asyncio.gather(*tasks)

    for uid in dead_users:
        try: db.zfq(uid)
        except Exception: pass

    try:
        await kfx.bot.send_message(
            chat_id=admin_chat_id,
            text=(
                "✅ <b>File Broadcast Finished</b>\n\n"
                f"📨 Sent: <b>{sent_count}</b>\n"
                f"💀 Dead/Blocked Removed: <b>{dead_count}</b>\n"
                f"⚠️ Failed: <b>{failed_count}</b>\n"
                f"👥 Total Processed: <b>{len(users)}</b>"
            ),
            parse_mode="HTML"
        )
    except Exception:
        pass


                                                          
                       
                                                          

def fxq(btn_id: int) -> str:
    """Return Telegram's native button style. Custom admin color always wins.
    Default menu: Blue, Green, Blue, Green, ... with the final button Red.
    """
    color = (db.fkv(f"menu_color_{btn_id}") or "").upper()
    if color == "R":
        return "danger"
    if color == "G":
        return "success"
    if color == "B":
        return "primary"

    buttons = db.fxz()
    last_id = max(buttons.keys(), default=btn_id)
    if btn_id == last_id:
        return "danger"
    return "primary" if btn_id % 2 == 1 else "success"


def fkq(btn_id: int) -> str:
    color = db.fkv(f"btn_color_{btn_id}")
    if color:
        color = color.upper()
        if color == "R": return "danger"    
        if color == "G": return "success"   
        if color == "B": return "primary"   

    if btn_id % 2 != 0:
        return "success" 
    else:
        return "primary" 


                                                          
                       
                                                          

def fqf():
    demo_link = db.fkv("demo_link")
    contact_link = db.fkv("contact_link")
    m_btns = db.fxz()

    kbx = []
    for btn_id, (text, link) in m_btns.items():
        btn_style = fxq(btn_id)

        if btn_id == 1:
            kbx.append([InlineKeyboardButton(text, callback_data="premium", style=btn_style)])
        elif btn_id == 2:
            url = link if link else demo_link
            kbx.append([InlineKeyboardButton(text, url=url, style=btn_style)])
        elif btn_id == 3:
            url = link if link else contact_link
            kbx.append([InlineKeyboardButton(text, url=url, style=btn_style)])
        else:
            if link:
                kbx.append([InlineKeyboardButton(text, url=link, style=btn_style)])
            else:
                kbx.append([InlineKeyboardButton(text, callback_data=f"custom_btn_{btn_id}", style=btn_style)])

    return InlineKeyboardMarkup(kbx)

def zkx():
    btns = db.fkk()
    kbx = []
    for btn in btns:
        btn_id = btn[0]
        btn_style = fkq(btn_id)
        kbx.append([InlineKeyboardButton(f"{btn[1]} - ₹{btn[2]}", callback_data=f"plan_{btn_id}", style=btn_style)])
    kbx.append([InlineKeyboardButton("⬅️ BACK", callback_data="back_main", style="danger")])
    return InlineKeyboardMarkup(kbx)

def zxq(btn_id):
    kbx = [
        [InlineKeyboardButton("✅ VERIFY PAYMENT", callback_data=f"verify_{btn_id}", style="success")],
        [InlineKeyboardButton("⬅️ BACK", callback_data="premium", style="danger")]
    ]
    return InlineKeyboardMarkup(kbx)

def xvf():
    labels = [("📊 Dashboard","admin_dashboard"),("ℹ️ INFO","xxf_info"),("💎 BUY PREMIUM PLAN","admin_buy_premium"),("📢 Broadcast","admin_broadcast"),("📦 Manage Plans","admin_manage_button"),("💳 Edit UPI","admin_edit_upi"),("📝 Edit Welcome","admin_edit_welcome"),("💎 Edit Premium","admin_edit_premium"),("🔗 Manage Demo","admin_manage_demo"),("⚙️ Edit Menu","admin_edit_menu"),("✅ Set Approved","admin_set_approved"),("📞 Contact Link","admin_contact_link"),("📝 Log Channel","admin_log_channel")]
    kbx=[]
    for i in range(0,len(labels),2):
        row=[]
        for j in range(i,min(i+2,len(labels))):
            text,cb=labels[j]; style="primary" if j%2==0 else "success"
            if j==len(labels)-1: style="danger"
            row.append(InlineKeyboardButton(text,callback_data=cb,style=style))
        kbx.append(row)
    return InlineKeyboardMarkup(kbx)

def zxf():
    labels=[("🗄️ DATABASE","padmin_database"),("➕ ADDDATA","padmin_adddata"),("👑 NEW ADMIN","padmin_new_admin"),("🗑️ REMOVE ADMIN","padmin_remove_admin"),("🔎 CHECK ADMIN","padmin_check_admin"),("🏦 DEFAULT UPI","padmin_default_upi"),("💎 PREMIUM","pkkfs_premium"),("📢 PERMANENT LOG CHANNEL","padmin_permanent_log"),("♻️ RESET","padmin_reset"),("💾 SAVE LOGS","padmin_save_logs")]
    kbx=[]
    for i in range(0,len(labels),2):
        row=[]
        for j in range(i,min(i+2,len(labels))):
            text,cb=labels[j]; style="danger" if cb=="padmin_reset" else ("primary" if j%2==0 else "success")
            row.append(InlineKeyboardButton(text,callback_data=cb,style=style))
        kbx.append(row)
    return InlineKeyboardMarkup(kbx)


async def kfq(kfx: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: int = 30):
    await asyncio.sleep(delay)
    try:
        await kfx.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass


                                                          
                              
                                                          

async def qxv(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    user_id = xuf.effective_user.id
    db.xzv(user_id)
    users_state[user_id] = {"status": "idle", "rejects": 0}

    w_msg_id = db.fkv("welcome_msg_id")
    w_chat_id = db.fkv("welcome_chat_id")

    if xuf.message:
        if w_msg_id and w_chat_id:
            try:
                await kfx.bot.copy_message(
                    chat_id=user_id,
                    from_chat_id=int(w_chat_id),
                    message_id=int(w_msg_id),
                    reply_markup=fqf()
                )
                return
            except Exception:
                pass
        
        await xuf.message.reply_text("Welcome to the Bot!", reply_markup=fqf())


                                                          
                              
                                                          

async def fzv(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if not fzf(xuf.effective_user.id):
        return
    if not await kzk(xuf, kfx):
        return

    cmds_guide = """
🛠 <b>COMPLETE ADMIN COMMANDS GUIDE (A-Z)</b>

🔹 <b>/admin</b>
👉  Admin Panel

🔹 <b>/premiumkey</b>
👉 New Admin Premium Activation: <code>/premiumkey YOUR-KEY</code>

🔹 <b>/addlink</b>
👉 <code>/addlink [LINK] [BUTTON_ID]</code>

🔹 <b>/admin</b> or <b>/dashboard</b>
👉 Open Admin Panel

🔹 <b>/broadcast</b> or <b>/sendall</b>
👉 Reply to msg: <code>/broadcast [60]</code> (60s auto-delete)
👉 Local file: <code>/broadcast video.mp4 [120]</code>
<i>*Without time brackets, defaults to 6 hours.</i>

🔹 <b>/button</b>
👉 <code>/button VIP PLAN [99] [1]</code>

🔹 <b>/buttoncolor</b> (🌟 NEW)
👉 Change Premium Button Color: <code>/buttoncolor [BUTTON_ID] [R/G/B]</code>
👉 Example: <code>/buttoncolor [2] [G]</code>

🔹 <b>/cmds</b>
👉 Show this guide

🔹 <b>/demo</b> & <b>/link</b>
👉 <code>/demo [your link] </code>
👉 <code>/link [your link ] </code>

🔹 <b>/menu</b>
👉 With Link: <code>/menu [MY CHANNEL][4][https:]</code>
👉 Without Link: <code>/menu [MY CHANNEL][4]</code>

🔹 <b>/addlogchnl</b>
👉 <code>/addlogchnl https.....</code>
👉 Bot must be admin on the channel.

🔹 <b>/menucolor</b> (🌟 NEW)
👉 Change Main Menu Color: <code>/menucolor [BUTTON_ID] [R/G/B]</code>
👉 Example: <code>/menucolor [5] [R]</code>

🔹 <b>/remove</b>
👉 Remove menu button: <code>/remove 4</code>

🔹 <b>/save</b> & <b>/fset</b>
👉 Backup Bot Settings: <code>/save</code>
👉 Restore Settings: Reply to the backup file with <code>/fset</code>

🔹 <b>/setapprove</b>
👉 Reply to approval message/video: <code>/setapprove</code>

🔹 <b>/setupi</b>
👉 <code>/setupi your_upi@ybl</code>

🔹 <b>/setwelcome</b> & <b>/setpremium</b>
👉 Reply to message/photo: <code>/setwelcome</code>
👉 Reply to message/photo: <code>/setpremium</code>

🔹 <b>/sms</b>
👉 Reply to msg: <code>/sms 123456789 [60]</code> (60s auto-delete)
    """
    await xuf.message.reply_text(cmds_guide, parse_mode='HTML')


                                                          
                                      
                                                          

async def xvz(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    user_id = xuf.effective_user.id
    if fzq(user_id):
        await xuf.message.reply_text("🛠 **Admin Control Panel**", reply_markup=xvf(), parse_mode='Markdown')
        return

    access = db.kqk(user_id)
    if not access:
        return

    limited, reason = db.xkz(access)
    if limited:
        await xxz(user_id, access, reason, kfx.bot, notify=True)
                                                                              
                                                                          
                                                        
        await xuf.message.reply_text(
            "⛔ <b>ACCESS DISABLED | BUY PREMIUM </b>\n\n"
            "Your previous access has ended because the limit/time was reached.\n"
            "💳 Payment approval, admin tools, broadcasts and other operational access are disabled.\n\n"
            "💎 <b>BUY PREMIUM PLAN</b> remains available so you can purchase a new plan.",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('💎 BUY PREMIUM PLAN', callback_data='admin_buy_premium', style='success')]
            ])
        )
        return

    if not await kzk(xuf, kfx, "open the Admin Panel"):
        return
    await xuf.message.reply_text("🛠 **Admin Control Panel**", reply_markup=xvf(), parse_mode='Markdown')

async def zxx(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if not fzq(xuf.effective_user.id): return
    zkv()
    await xuf.message.reply_text("⚡️ <b>PERMANENT ADMIN PANEL</b> ⚡️",parse_mode="HTML",reply_markup=zxf())

async def xff(chat_id, kfx):
    snap=db.kvv(); admins=db.fxv()
    logs=(f"BOT LOG SNAPSHOT\n================\nTotal Users: {snap['total_users']}\nLive Users: {snap['live_users']}\nTotal Payments: {snap['total_payments']}\nTotal Revenue: INR {snap['total_amount']}\nNew Admin Count: {snap['new_admin_count']}\n\nNo UPI, usernames, user IDs, screenshots or personal payment details are stored in this log file.\n")
    lf=BytesIO(logs.encode()); lf.name="bot_logs.txt"
    cfg=[]
    for key,cmd in (("upi_id","/setupi"),("demo_link","/demo"),("contact_link","/link")):
        val=db.fkv(key)
        if val: cfg.append(f"{cmd} {val}")
    for bid,(text,link) in db.fxz().items(): cfg.append(f"/menu [{text}][{bid}]"+(f"[{link}]" if link else ""))
    for bid,text,price in db.fkk(): cfg.append(f"/button {text} [{price}] [{bid}]")
    for aid,_ in admins: cfg.append(f"/newadmin {aid}")
    cf=BytesIO(("\n".join(cfg)+"\n").encode()); cf.name="bot_config_backup.txt"
    await kfx.bot.send_document(chat_id=chat_id,document=lf,caption="📊 <b>BOT LOGS BACKUP</b>",parse_mode="HTML")
    await kfx.bot.send_document(chat_id=chat_id,document=cf,caption="⚙️ <b>BOT CONFIG BACKUP</b> — reply with /fset to restore",parse_mode="HTML")


def fvq():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 BUY PREMIUM LITE • ₹199", callback_data="admin_buy_PREMIUM_LITE", style="primary")],
        [InlineKeyboardButton("🚀 BUY PREMIUM XD • ₹299", callback_data="admin_buy_PREMIUM_XD", style="success")],
        [InlineKeyboardButton("👑 BUY PREMIUM PRO • ₹399", callback_data="admin_buy_PREMIUM_PRO", style="primary")],
        [InlineKeyboardButton("🛠️ BUY CUSTOM PLAN", callback_data="admin_buy_CUSTOM", style="primary")],
        [InlineKeyboardButton("⬅️ BACK", callback_data="admin_back", style="danger")],
    ])

def zxz():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 PREMIUM LITE • ₹199", callback_data="padmin_key_PREMIUM_LITE", style="primary")],
        [InlineKeyboardButton("🚀 PREMIUM XD • ₹299", callback_data="padmin_key_PREMIUM_XD", style="success")],
        [InlineKeyboardButton("👑 PREMIUM PRO • ₹399", callback_data="padmin_key_PREMIUM_PRO", style="primary")],
        [InlineKeyboardButton("🛠️ CUSTOM PREMIUM", callback_data="padmin_custom_premium", style="primary")],
        [InlineKeyboardButton("📋 KEY STATUS", callback_data="padmin_key_status", style="success")],
    ])

def zkk():
    return (
        "╭━━━━━━━━━━━━━━━━━━━━━━╮\n│ 💎 <b>PREMIUM PLANS</b>\n╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        "🆓 <b>FREE</b>\n├ 👥 Users: 500\n├ 💰 Payment Limit: ₹150\n├ ⏳ Duration: 2 Days\n└ 💵 Price: FREE\n\n"
        "💎 <b>PREMIUM LITE</b>\n├ 👥 Users: 2,000\n├ 💰 Payment Limit: ₹800\n├ ⏳ Duration: 7 Days\n└ 💵 Price: ₹199\n\n"
        "🚀 <b>PREMIUM XD</b>\n├ 👥 Users: 4,000\n├ 💰 Payment Limit: ₹1,500\n├ ⏳ Duration: 14 Days\n└ 💵 Price: ₹299\n\n"
        "👑 <b>PREMIUM PRO</b>\n├ 👥 Users: 10,000\n├ 💰 Payment Limit: ₹5,000\n├ ⏳ Duration: 30 Days\n└ 💵 Price: ₹399\n\n"
        "🛠️ <b>CUSTOM PLAN</b>\n├ ✨ Custom limits available\n└ 📩 Contact: @HEXAZONxHERE\n\n"
        "╭━━━━━━━━━━━━━━━━━━━━━━╮\n│ 📌 <b>QUICK SUMMARY</b>\n╰━━━━━━━━━━━━━━━━━━━━━━╯\n"
        "🆓 Free → 500 Users • ₹150 • 2 Days\n💎 Lite → 2,000 Users • ₹800 • 7 Days\n🚀 XD → 4,000 Users • ₹1,500 • 14 Days\n👑 Pro → 10,000 Users • ₹5,000 • 30 Days\n\n💡 Select the plan according to your requirements."
    )


async def xvx(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    uid=int(xuf.effective_user.id)
    if not db.kqk(uid): return
    access=db.kqk(uid)
    try:
        chat=await kfx.bot.get_chat(uid)
        name=f"@{chat.username}" if chat.username else (chat.first_name or "Unknown")
    except Exception: name="Unknown"
    if access.get("unrestricted"):
        plan="PERMANENT ADMIN"; status="ACTIVE"; expires="Lifetime"
        plan_rev="Unlimited"; plan_users="Unlimited"
    else:
        plan=access.get("plan","FREE"); status=access.get("status","UNKNOWN"); expires=access.get("expires_at") or "Lifetime"
        plan_rev=xkx(access.get("revenue_limit")); plan_users=xkx(access.get("user_limit"))
    text=(
        "╭━━━━━━━━━━━━━━━━━━━━━━╮\n│ ℹ️ <b>ADMIN INFO</b>\n╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        f"👤 <b>Admin:</b> {name}\n"
        f"🆔 <b>ID:</b> <code>{uid}</code>\n"
        f"📦 <b>Plan:</b> {plan}\n"
        f"📊 <b>Users:</b> {access.get('users',0)}\n"
        f"💰 <b>Revenue:</b> ₹{access.get('revenue',0)}\n\n"
        "╭─ <b>PLAN STATUS</b> ─╮\n"
        f"Revenue: ₹{access.get('revenue',0)} / {('₹'+plan_rev) if plan_rev != 'Unlimited' else 'Unlimited'}\n"
        f"User: {access.get('users',0)} / {plan_users}\n"
        f"⏳ Expires: {expires}\n"
        f"🟢 Status: {status}\n"
        "╰────────────────────╯"
    )
    await xuf.effective_message.reply_text(text,parse_mode="HTML")

async def xqz(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    await xuf.effective_message.reply_text(zkk(), parse_mode="HTML", reply_markup=fvq())


async def zxk(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    qxx=xuf.callback_query; await qxx.answer(); uid=qxx.from_user.id
    if not fzq(uid): return
    data=qxx.data
    if data=="padmin_database": return await qfk(xuf,kfx)
    if data=="padmin_adddata":
        await qxx.message.reply_text("Use /adddata 123456 789012 or reply to a .txt file with /adddata"); return
    if data=="padmin_new_admin":
        admin_states[uid]="WAITING_FOR_NEW_ADMIN"; await qxx.message.reply_text("👑 Send new Admin ID (numeric).",parse_mode="HTML"); return
    if data=="padmin_remove_admin":
        admin_states[uid]="WAITING_FOR_REMOVE_ADMIN"; await qxx.message.reply_text("🗑️ Send Admin ID to remove. Permanent Admin cannot be removed."); return
    if data=="padmin_default_upi":
        admin_states[uid]="WAITING_FOR_PERMANENT_UPI"
        current=db.fkv("permanent_upi_id")
        await qxx.message.reply_text(
            "🏦 <b>PERMANENT DEFAULT UPI</b>\n\n"
            f"Current: <code>{current or 'NOT SET'}</code>\n\n"
            "Send the Permanent Admin UPI ID. This UPI will be restored automatically whenever a New Admin access expires or hits a limit.", parse_mode="HTML")
        return
    if data=="pkkfs_premium":
        await qxx.message.reply_text(
            "💎 <b>PREMIUM KEY GENERATOR</b>\n\n"
            "Select the plan. A one-time key will be generated for the New Admin.",
            parse_mode="HTML", reply_markup=zxz()
        ); return
    if data=="padmin_custom_premium":
        admin_states[uid]="WAITING_FOR_CUSTOM_PREMIUM"
        await qxx.message.reply_text(
            "🛠️ <b>CUSTOM PREMIUM GENERATOR</b>\n\n"
            "Send details exactly like this:\n<code>[USER][REVENUE][TIME]</code>\n\n"
            "Example: <code>[500][200][7]</code> = 500 users, ₹200 revenue, 7 days.",
            parse_mode="HTML"
        ); return
    if data=="padmin_permanent_log":
        admin_states[uid]="WAITING_FOR_PERMANENT_LOG_CHANNEL"
        current=db.kqq(config.xkq_admin_root)
        await qxx.message.reply_text(
            "📢 <b>PERMANENT LOG CHANNEL</b>\n\n"
            f"Current: <code>{current or 'NOT SET'}</code>\n\n"
            "Send channel as <code>@channel</code>, <code>https://t.me/channel</code> or numeric <code>-100...</code>.\n"
            "Send <code>RESET</code> to remove it.", parse_mode="HTML"
        ); return
    if data=="padmin_key_status":
        rows=db.fkz()
        if not rows:
            await qxx.message.reply_text("📭 No premium keys generated yet."); return
        text=["🔑 <b>RECENT PREMIUM KEYS</b>",""]
        for hint,plan,status,created,used_by,used_at in rows:
            text.append(f"• <b>{plan.replace('PREMIUM_','')}</b> | ...{hint} | {status} | Used: {used_by or '-'}")
        await qxx.message.reply_text("\n".join(text), parse_mode="HTML"); return
    if data.startswith("padmin_key_"):
        plan=data.replace("padmin_key_","",1)
        if plan not in ("PREMIUM_LITE","PREMIUM_XD","PREMIUM_PRO"):
            return
        try:
            key=db.kkv(plan, uid)
            p=db.PREMIUM_PLANS[plan]
            await qxx.message.reply_text(
                "🔐 <b>PREMIUM KEY CREATED</b>\n\n"
                f"📦 Plan: <b>{plan.replace('PREMIUM_','')}</b>\n"
                f"💰 Price reference: <b>₹{p['price']}</b>\n"
                f"🔑 Key:\n<code>{key}</code>\n\n"
                "⚠️ One-time key. Send this key to the New Admin.\n"
                "FOR REDEEM USE  /premiumkey [KEY ].",
                parse_mode="HTML"
            )
        except Exception as e:
            await qxx.message.reply_text(f"❌ Key generation failed: {e}")
        return
    if data=="padmin_check_admin":
        lines=["<b>👑 CURRENT ADMINS</b>","",f"<b>PERMANENT ADMIN</b>\nADMIN ID: <code>{config.xkq_admin_root}</code>"]
        try:
            c=await kfx.bot.get_chat(config.xkq_admin_root); lines[2]=f"<b>PERMANENT ADMIN</b>\nADMIN USERNAME: {('@'+c.username) if c.username else (c.first_name or 'Unknown')}\nADMIN ID: <code>{config.xkq_admin_root}</code>"
        except Exception: pass
        rows=db.fxv()
        for i,(aid,added) in enumerate(rows,1):
            name="Unknown / inaccessible"
            try:
                c=await kfx.bot.get_chat(aid); name='@'+c.username if c.username else (c.first_name or name)
            except Exception: pass
            access = db.kqk(aid)
            plan = access['plan'] if access else 'FREE'
            status = access['status'] if access else 'UNKNOWN'
            lines.append(f"\n<b>{'OWNER' if i==1 else 'ADMIN #'+str(i)}</b>\nADMIN USERNAME: {name}\nADMIN ID: <code>{aid}</code>\nADDED: {added}\nPLAN: <b>{plan}</b> | STATUS: <b>{status}</b>")
        await qxx.message.reply_text("\n".join(lines),parse_mode="HTML"); return
    if data=="padmin_save_logs":
        await xff(uid,kfx); return
    if data=="padmin_reset":
        await xff(uid,kfx)
        db.zzx(); zkv(); users_state.clear(); admin_states.clear()
        await qxx.message.reply_text("♻️ <b>BOT RESET COMPLETE</b>\nDatabase preserved. New admins and configurable bot settings were reset.",parse_mode="HTML",reply_markup=zxf()); return

async def xqq(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    qxx = xuf.callback_query
    await qxx.answer()
    user_id = qxx.from_user.id
    data = qxx.data

    if not (fzf(user_id) or db.kqk(user_id)):
        return

    if data == 'xxf_info':
        await xvx(xuf, kfx)
        return

    if data == 'admin_buy_premium':
        await xqz(xuf, kfx)
        return

    if data.startswith('admin_buy_'):
        if not await kzk(xuf, kfx, 'buy a premium plan'):
            return
        plan=data.replace('admin_buy_','',1)
        if plan == 'CUSTOM':
            await qxx.message.reply_text('🛠️ <b>FOR CUSTOM PREMIUM CONTACT: @HEXAZONxHERE</b>', parse_mode='HTML')
            return
        if plan not in db.PREMIUM_PLANS or plan == 'FREE': return
        amount=int(db.PREMIUM_PLANS[plan]['price'])
        permanent_upi=db.fkv('permanent_upi_id')
        if not permanent_upi:
            await qxx.message.reply_text('❌ Permanent Admin default UPI is not configured yet.')
            return
        upi_uri='upi://pay?'+urllib.parse.urlencode({'pa':permanent_upi,'pn':'Permanent Admin','am':f'{amount:.2f}','cu':'INR'})
        try:
            qr_bytes = kxf(upi_uri, f'kkfs_premium_{plan.lower()}.png')
        except Exception as e:
            await qxx.message.reply_text(f'❌ Could not generate the payment QR right now: {e}')
            return
        plan_label=plan.replace('PREMIUM_','')
        users_state[user_id]={'status':'kkfs_premium_pending','plan':plan,'price':amount}
        await qxx.message.delete()
        await kfx.bot.send_photo(chat_id=user_id, photo=qr_bytes, caption=(
            f'💎 <b>BUY PREMIUM {plan_label}</b>\n\n💰 Amount: <b>₹{amount}</b>\n🏦 UPI: <code>{permanent_upi}</code>\n\n'
            'Scan the QR and then send your payment screenshot here.\nThe payment proof will go directly to the Permanent Admin.'), parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('⬅️ BACK',callback_data='admin_back',style='danger')]]))
        return

    if data == 'admin_back':
        await qxx.message.delete()
        await kfx.bot.send_message(user_id,'🛠️ <b>Admin Control Panel</b>',parse_mode='HTML',reply_markup=xvf())
        return

    if not await kzk(xuf, kfx, "use the Admin Panel"):
        return

    if data == 'admin_edit_upi':
        admins=db.fxv()
        if not admins or int(admins[0][0]) != user_id:
            await qxx.message.reply_text('⛔ UPI function disabled .')
            return
        admin_states[user_id] = 'WAITING_FOR_UPI'
        await qxx.message.reply_text('WRITE DOWN 👇 YOUR UPI\nexample: yourupi@fam\n\nThis UPI stays active only while your access is active.')
        
    elif data == 'admin_broadcast':
        admin_states[user_id] = 'WAITING_FOR_BROADCAST'
        await qxx.message.reply_text("SEND BROADCAST MASSAGE (TEXT , VIDEO, IMAGES) 👇")
        
    elif data == 'admin_edit_welcome':
        admin_states[user_id] = 'WAITING_FOR_WELCOME'
        await qxx.message.reply_text("SEND WELCOME MASSAGE 👇\n(You can send text, or a photo with caption. It will be saved exactly as you send it!)")

    elif data == 'admin_edit_premium':
        admin_states[user_id] = 'WAITING_FOR_PREMIUM'
        await qxx.message.reply_text("SEND PREMIUM MASSAGE 👇\n(You can send text, or a photo like 1000275769.jpg with a caption!)")
        
    elif data == 'admin_manage_button':
        admin_states[user_id] = 'WAITING_FOR_MANAGE_BUTTON'
        await qxx.message.reply_text("CUSTOMIZE YOUR BOT BUTTON\n\nSEND WHICH BUTTON YOU WANT TO SAVE\nExample: VIP VIP Plan 1 [99] [1]")
        
    elif data == 'admin_edit_menu':
        admin_states[user_id] = 'WAITING_FOR_EDIT_MENU'
        await qxx.message.reply_text("CUSTOMIZE YOUR BOT BUTTON\n\nSEND WHICH BUTTON YOU WANT TO SAVE\nWith Link Example: `[MY CHANNEL][4][https://t.me/example]`\nWithout Link Example: `[MY CHANNEL][4]`", parse_mode="Markdown")
        
    elif data == 'admin_manage_demo':
        admin_states[user_id] = 'WAITING_FOR_DEMO'
        await qxx.message.reply_text("WRITE DOWN 👇 LINK\nexample: https.........")
        
    elif data == 'admin_contact_link':
        admin_states[user_id] = 'WAITING_FOR_CONTACT'
        await qxx.message.reply_text("WRITE DOWN 👇 LINK\nexample: https://t.me/yourusername")
        
    elif data == 'admin_set_approved':
        admin_states[user_id] = 'WAITING_FOR_SET_APPROVED'
        await qxx.message.reply_text("Send the file/video to set for approved users.")
        
    elif data == 'admin_log_channel':
        admin_states[user_id] = 'WAITING_FOR_LOG_CHANNEL'
        await qxx.message.reply_text(
            "Send log channel now.\n"
            "Example: https://t.me/mychannel or @mychannel or -1001234567890\n"
            "Private invite links (+...) are not valid send targets."
        )
        
    elif data == 'admin_dashboard':
        total_users = db.fff()
        total_payments = db.ffx("payments")
        total_amount = db.ffx("total_amount")
        upi = db.fkv("upi_id")
        
        new_admins = db.fxv()
        owner_id = new_admins[0][0] if new_admins else None
        try:
            owner_chat = await kfx.bot.get_chat(owner_id) if owner_id else None
            new_admin_name = f"@{owner_chat.username}" if owner_chat and owner_chat.username else (owner_chat.first_name if owner_chat else "Not Set")
        except Exception:
            new_admin_name = "Not Set"
        dash_text = f"""╭━━━━━━━━━━━━━━━━━━━━━━╮

⚡️ <b>𝗔𝗗𝗠𝗜𝗡 𝗖𝗘𝗡𝗧𝗘𝗥</b> ⚡️

╰━━━━━━━━━━━━━━━━━━━━━━╯

🤖 <b>BOT INFORMATION</b>

│ 🟢 Status     : <b>ONLINE</b>

│ 🆔 Bot        : <code>@{kfx.bot.username}</code>

│ 👑 Owner      : <b>{new_admin_name}</b>

╭─ 📊 <b>STATISTICS</b>

│ 👥 Users      : <b>{total_users}</b>

│ 💳 Payments   : <b>{total_payments}</b>

│ 💰 Revenue    : <b>₹{total_amount}</b>

╰──────────────────────

🏦 <b>PAYMENT GATEWAY</b>

│ 🔗 UPI        : <code>{upi}</code>

│ 🟢 System     : <b>ACTIVE</b>

━━━━━━━━━━━━━━━━━━━━━━

🛡️ <b>SECURE ADMIN PANEL</b>

⚙️ Full System Management

━━━━━━━━━━━━━━━━━━━━━━

⚡ <i>Powered &amp; Developed by @HEXAZONxHERE </i>"""
        await qxx.message.reply_text(dash_text, parse_mode='HTML')

async def xvk(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    user_id = xuf.effective_user.id
    if not fzf(user_id) or user_id not in admin_states:
        return
    if not await kzk(xuf, kfx):
        return

    state = admin_states[user_id]
    msg_text = xuf.message.text or xuf.message.caption or ""

    if state == 'WAITING_FOR_PERMANENT_UPI':
        if not fzq(user_id): return
        upi=msg_text.strip()
        if not upi or ' ' in upi or '@' not in upi:
            await xuf.message.reply_text('❌ Invalid UPI. Example: <code>name@upi</code>',parse_mode='HTML'); return
        db.qkv('permanent_upi_id',upi)
        db.qkv('upi_id',upi)
        admin_states.pop(user_id,None)
        zkv()
        await xuf.message.reply_text(f'✅ Permanent Default UPI saved: <code>{upi}</code>\n\nThis UPI will automatically be restored after any New Admin limit/expiry.',parse_mode='HTML')
        return

    if state == 'WAITING_FOR_NEW_ADMIN':
        raw=msg_text.strip()
        if not raw.isdigit():
            await xuf.message.reply_text("❌ Invalid Admin ID. Send numeric Telegram user ID only."); return
        ok,reason=db.xzq(int(raw)); zkv(); admin_states.pop(user_id,None)
        if ok: await xuf.message.reply_text(f"✅ {'OWNER' if reason=='owner' else 'NEW ADMIN'} added: <code>{raw}</code>",parse_mode='HTML')
        elif reason=='permanent': await xuf.message.reply_text("❌ Permanent Admin cannot be added as a new admin.")
        else: await xuf.message.reply_text("⚠️ This Admin ID is already added.")

    elif state == 'WAITING_FOR_REMOVE_ADMIN':
        raw=msg_text.strip()
        if not raw.isdigit():
            await xuf.message.reply_text("❌ Invalid Admin ID. Send numeric Telegram user ID only."); return
        ok,reason=db.zfz(int(raw)); zkv(); admin_states.pop(user_id,None)
        if ok: await xuf.message.reply_text(f"✅ Admin <code>{raw}</code> removed. The next oldest new admin is now owner.",parse_mode='HTML')
        elif reason=='permanent': await xuf.message.reply_text("❌ Permanent Admin cannot be removed.")
        else: await xuf.message.reply_text("❌ That Admin is not set.")

    elif state == 'WAITING_FOR_CUSTOM_PREMIUM':
        match = re.fullmatch(r'\s*\[\s*(\d+)\s*\]\s*\[\s*(\d+)\s*\]\s*\[\s*(\d+)\s*\]\s*', msg_text)
        if not match:
            await xuf.message.reply_text("❌ Format Error. Use: [USER][REVENUE][TIME]\nExample: [500][200][7]")
            return
        user_limit, revenue_limit, days = map(int, match.groups())
        if user_limit <= 0 or revenue_limit < 0 or days <= 0:
            await xuf.message.reply_text("❌ USER and TIME must be greater than 0; REVENUE cannot be negative.")
            return
        try:
            key=db.kkz(user_limit, revenue_limit, days, user_id)
            await xuf.message.reply_text(
                "🛠️ <b>CUSTOM PREMIUM KEY CREATED</b>\n\n"
                f"👥 User Limit: <b>{user_limit}</b>\n"
                f"💰 Revenue Limit: <b>₹{revenue_limit}</b>\n"
                f"⏳ Duration: <b>{days} days</b>\n\n"
                f"🔑 Key:\n<code>{key}</code>\n\n"
                "⚠️ One-time key. Send this key to the New Admin.\n"
                "FOR REDEEM USE > /premiumkey [KEY] .", parse_mode="HTML"
            )
        except Exception as e:
            await xuf.message.reply_text(f"❌ Custom key generation failed: {e}")
        admin_states.pop(user_id, None)

    elif state == 'WAITING_FOR_PERMANENT_LOG_CHANNEL':
        if msg_text.strip().upper() == 'RESET':
            db.zfv(config.xkq_admin_root)
            await xuf.message.reply_text("♻️ Permanent log channel reset ho gaya.")
            admin_states.pop(user_id, None)
            return
        normalized = fvv(msg_text.strip())
        if not normalized:
            await xuf.message.reply_text("❌ Invalid channel. Use @channel, https://t.me/channel, or -100... chat ID.")
            return
        db.zqv(config.xkq_admin_root, normalized)
        await xuf.message.reply_text(f"✅ Permanent log channel saved: <code>{normalized}</code>", parse_mode="HTML")
        admin_states.pop(user_id, None)

    elif state == 'WAITING_FOR_UPI':
        db.qkv("upi_id", msg_text.strip())
        await xuf.message.reply_text(f"✅ UPI ID successfully updated to: `{msg_text}`", parse_mode="Markdown")
        del admin_states[user_id]

    elif state == 'WAITING_FOR_BROADCAST':
                                                                    
        users = db.fxk() if hasattr(db, "get_live_users") else db.kvx()
        delay = 21600                  
        
        kfx.application.create_task(
            qkx(
                kfx=kfx,
                admin_chat_id=user_id,
                users=users,
                source_chat_id=xuf.message.chat_id,
                message_id=xuf.message.message_id,
                delay=delay
            )
        )
        del admin_states[user_id]

    elif state == 'WAITING_FOR_WELCOME':
        db.qkv("welcome_msg_id", xuf.message.message_id)
        db.qkv("welcome_chat_id", xuf.message.chat_id)
        await xuf.message.reply_text("✅ Welcome Message Set Successfully!")
        del admin_states[user_id]

    elif state == 'WAITING_FOR_PREMIUM':
        db.qkv("premium_msg_id", xuf.message.message_id)
        db.qkv("premium_chat_id", xuf.message.chat_id)
        await xuf.message.reply_text("✅ Premium Message Set Successfully!")
        del admin_states[user_id]

    elif state == 'WAITING_FOR_MANAGE_BUTTON':
        match = re.search(r"(.*)\[(\d+)\]\s*\[(\d+)\]", msg_text)
        if match:
            text = match.group(1).strip()
            price = int(match.group(2))
            btn_id = int(match.group(3))
            db.zvq(btn_id, text, price)
            await xuf.message.reply_text(f"✅ Button {btn_id} updated: {text} | ₹{price}")
            del admin_states[user_id]
        else:
            await xuf.message.reply_text("❌ Format Error. Ex: VIP VIP Plan 1 [99] [1]")

    elif state == 'WAITING_FOR_EDIT_MENU':
        match = re.search(r"\[(.*?)\]\s*\[(\d+)\](?:\s*\[(.*?)\])?", msg_text)
        if match:
            text = match.group(1).strip()
            btn_id = int(match.group(2))
            link = match.group(3).strip() if match.group(3) else ""
            db.qkq(btn_id, text, link)
            await xuf.message.reply_text(f"✅ Menu Button {btn_id} added successfully!")
            del admin_states[user_id]
        else:
            await xuf.message.reply_text("❌ Format Error. Ex:\n`[NAME][NUMBER][LINK]`", parse_mode="Markdown")

    elif state == 'WAITING_FOR_DEMO':
        db.qkv("demo_link", msg_text.strip())
        await xuf.message.reply_text(f"✅ Demo link updated!")
        del admin_states[user_id]

    elif state == 'WAITING_FOR_CONTACT':
        db.qkv("contact_link", msg_text.strip())
        await xuf.message.reply_text(f"✅ Contact link updated!")
        del admin_states[user_id]
        
    elif state == 'WAITING_FOR_LOG_CHANNEL':
        if msg_text.strip().upper() == 'RESET':
            db.zfv(user_id)
            await xuf.message.reply_text("♻️ Your New Admin log channel has been reset.")
            admin_states.pop(user_id, None)
            return
        normalized = fvv(msg_text.strip())
        if not normalized:
            await xuf.message.reply_text("❌ Invalid channel. Use https://t.me/channel, @channelusername, or numeric -100... chat ID.")
            return
        db.zqv(user_id, normalized)
        await xuf.message.reply_text(f"✅ Your log channel saved: {normalized}")
        admin_states.pop(user_id, None)

    elif state == 'WAITING_FOR_SET_APPROVED':
        db.qkv("approve_msg_id", xuf.message.message_id)
        db.qkv("approve_chat_id", xuf.message.chat_id)
        await xuf.message.reply_text("✅ Approval Media/Message Set! (Auto-deletes in 30s)")
        del admin_states[user_id]


                                                          
                                                  
                                                          

async def zqf(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if not fzf(xuf.effective_user.id): return
    if not await kzk(xuf, kfx): return
        
    config_lines = []
    upi = db.fkv("upi_id")
    if upi: config_lines.append(f"/setupi {upi}")
    
    demo = db.fkv("demo_link")
    if demo: config_lines.append(f"/demo {demo}")
    
    contact = db.fkv("contact_link")
    if contact: config_lines.append(f"/link {contact}")
    
    for btn_id, (text, link) in db.fxz().items():
        if link: config_lines.append(f"/menu [{text}][{btn_id}][{link}]")
        else: config_lines.append(f"/menu [{text}][{btn_id}]")
            
    for btn in db.fkk():
        config_lines.append(f"/button {btn[1]} [{btn[2]}] [{btn[0]}]")
        
    file_content = "\n".join(config_lines)
    file = BytesIO(file_content.encode('utf-8'))
    file.name = "bot_settings_backup.txt"
    
    await kfx.bot.send_document(
        chat_id=xuf.effective_chat.id,
        document=file,
        caption="✅ **BOT CONFIGURATION BACKUP**\n\nRestart k baad settings restore karne ke liye is file ko reply me tag karke `/fset` use karein.",
        parse_mode="Markdown"
    )

async def kzv(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if not fzf(xuf.effective_user.id): return
    if not await kzk(xuf, kfx): return
        
    if not xuf.message.reply_to_message or not xuf.message.reply_to_message.document:
        await xuf.message.reply_text("❌ Kripya backup `.txt` file ko reply karke `/fset` use karein.")
        return
        
    doc = xuf.message.reply_to_message.document
    if doc.mime_type == 'text/plain' or doc.file_name.endswith('.txt'):
        processing_msg = await xuf.message.reply_text("⏳ Restoring settings from file...")
        try:
            file = await kfx.bot.get_file(doc.file_id)
            file_bytes = await file.download_as_bytearray()
            content = file_bytes.decode('utf-8')
            
            for line in content.splitlines():
                line = line.strip()
                if not line: continue
                
                if line.startswith("/setupi"):
                    db.qkv("upi_id", line.replace("/setupi", "").strip())
                elif line.startswith("/demo"):
                    db.qkv("demo_link", line.replace("/demo", "").strip())
                elif line.startswith("/link"):
                    db.qkv("contact_link", line.replace("/link", "").strip())
                elif line.startswith("/menu"):
                    match = re.search(r"\[(.*?)\]\s*\[(\d+)\](?:\s*\[(.*?)\])?", line)
                    if match:
                        text = match.group(1).strip()
                        btn_id = int(match.group(2))
                        link = match.group(3).strip() if match.group(3) else ""
                        db.qkq(btn_id, text, link)
                elif line.startswith("/newadmin"):
                    raw_admin = line.replace("/newadmin", "", 1).strip()
                    if raw_admin.isdigit(): db.xzq(int(raw_admin))
                elif line.startswith("/button"):
                    match = re.search(r"/button\s+(.*?)\[(\d+)\]\s*\[(\d+)\]", line)
                    if match:
                        text = match.group(1).strip()
                        price = int(match.group(2))
                        btn_id = int(match.group(3))
                        db.zvq(btn_id, text, price)
                        
            await processing_msg.edit_text("✅ All settings have been successfully restored!")
        except Exception as e:
            await processing_msg.edit_text(f"❌ Error restoring settings: {e}")


                                                          
                                                 
                                                          

def fvv(value: str):
    value = value.strip()
    if re.fullmatch(r"-100\d+", value):
        return value
    if value.startswith("@"): 
        return value
    m = re.fullmatch(r"https?://t\.me/([A-Za-z0-9_]{4,})/?", value)
    if m:
        return "@" + m.group(1)
    return None


async def qxx(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if not fzf(xuf.effective_user.id):
        return
    if not await kzk(xuf, kfx):
        return
    raw = xuf.message.text.replace("/menucolor", "", 1).strip()
    match = re.fullmatch(r"\s*\[?\s*(\d+)\s*\]?\s*\[?\s*([RGBrgb])\s*\]?\s*", raw)
    if not match:
        await xuf.message.reply_text("❌ Format Error!\nUse: /menucolor [button number] [R/G/B]\nExample: /menucolor [5] [R]")
        return
    btn_id, color = int(match.group(1)), match.group(2).upper()
    if btn_id not in db.fxz():
        await xuf.message.reply_text(f"❌ Menu button {btn_id} does not exist. Add it first with /menu [NAME][{btn_id}]")
        return
    db.qkv(f"menu_color_{btn_id}", color)
    names = {"R": "🔴 RED", "G": "🟢 GREEN", "B": "🔵 BLUE"}
    await xuf.message.reply_text(f"✅ Main Menu Button {btn_id} color updated to {names[color]}.")


async def zvz(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if not fzf(xuf.effective_user.id):
        return
    if not await kzk(xuf, kfx):
        return
    raw = xuf.message.text.replace("/buttoncolor", "", 1).strip()
    match = re.fullmatch(r"\s*\[?\s*(\d+)\s*\]?\s*\[?\s*([RGBrgb])\s*\]?\s*", raw)
    if not match:
        await xuf.message.reply_text("❌ Format Error!\nUse: /buttoncolor [button number] [R/G/B]")
        return
    btn_id, color = int(match.group(1)), match.group(2).upper()
    if not db.kvf(btn_id):
        await xuf.message.reply_text(f"❌ Premium button {btn_id} does not exist. Create it first with /button NAME [PRICE] [{btn_id}]")
        return
    db.qkv(f"btn_color_{btn_id}", color)
    names = {"R": "🔴 RED", "G": "🟢 GREEN", "B": "🔵 BLUE"}
    await xuf.message.reply_text(f"✅ Premium Button {btn_id} color updated to {names[color]}.")


async def xzz(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if not fzf(xuf.effective_user.id):
        return
    if not await kzk(xuf, kfx):
        return
    raw = " ".join(kfx.args).strip()
    if not raw:
        await xuf.message.reply_text("Use: /addlogchnl https://t.me/yourchannel")
        return
    normalized = fvv(raw)
    if not normalized:
        await xuf.message.reply_text(
            "❌ Invalid channel. Use a public channel link like https://t.me/mychannel, @mychannel, or numeric -100... chat ID.\n"
            "Private invite links such as https://t.me/+... cannot be used as a send target."
        )
        return
    try:
        chat = await kfx.bot.get_chat(normalized)
        if chat.type != "channel":
            await xuf.message.reply_text("❌ The target must be a Telegram channel.")
            return
        db.zqv(xuf.effective_user.id, normalized)
        await xuf.message.reply_text(f"✅ Your log channel connected: {chat.title} ({normalized})")
    except Exception as e:
        await xuf.message.reply_text(
            "❌ I could not access that channel. Add the bot to the channel (preferably as admin) and try again.\n"
            f"Details: {e}"
        )


async def qxf(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if not fzf(xuf.effective_user.id): return
    if not await kzk(xuf, kfx): return
    if not xuf.message.reply_to_message: return
    db.qkv("welcome_msg_id", xuf.message.reply_to_message.message_id)
    db.qkv("welcome_chat_id", xuf.message.chat_id)
    await xuf.message.reply_text("✅ Live Welcome message set successfully with exact formatting!")

async def qxk(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if not fzf(xuf.effective_user.id): return
    if not await kzk(xuf, kfx): return
    if not xuf.message.reply_to_message: return
    db.qkv("premium_msg_id", xuf.message.reply_to_message.message_id)
    db.qkv("premium_chat_id", xuf.message.chat_id)
    await xuf.message.reply_text("✅ Live Premium menu message set successfully!")

async def xzk(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if xuf.effective_user.id != config.xkq_admin_root: return
    if xuf.message.reply_to_message and xuf.message.reply_to_message.document:
        doc = xuf.message.reply_to_message.document
        if doc.mime_type == 'text/plain' or doc.file_name.endswith('.txt'):
            try:
                file = await kfx.bot.get_file(doc.file_id)
                content = (await file.download_as_bytearray()).decode('utf-8')
                added = db.xqx(re.findall(r'\b\d+\b', content))
                await xuf.message.reply_text(f"✅ Added {added} users!")
            except: pass
            return
    if not kfx.args: return
    added = db.xqx(kfx.args)
    await xuf.message.reply_text(f"✅ Successfully added {added} users!")

async def kfk(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    uid=int(xuf.effective_user.id)
    if fzq(uid):
        await xvz(xuf,kfx); return
    access=db.kqk(uid)
    if not access: return
    limited,reason=db.xkz(access)
    if limited:
        await xxz(uid,access,reason,kfx.bot,notify=True)
        await xuf.message.reply_text(
            '⛔ <b>ADMIN ACCESS DISABLED</b>\n\nYour previous plan is no longer active.\n\n💎 Tap <b>BUY PREMIUM PLAN</b> below to purchase a new plan.',
            parse_mode='HTML',reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('💎 BUY PREMIUM PLAN',callback_data='admin_buy_premium',style='success')],[InlineKeyboardButton('ℹ️ INFO',callback_data='xxf_info',style='primary')]]))
        return
    await xvz(xuf,kfx)

async def zvk(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if not fzf(xuf.effective_user.id): return
    if not await kzk(xuf, kfx): return
    if not xuf.message.reply_to_message: return
    db.qkv("approve_msg_id", xuf.message.reply_to_message.message_id)
    db.qkv("approve_chat_id", xuf.message.chat_id)
    await xuf.message.reply_text("✅ Approval content updated!")

async def zvf(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if not fzf(xuf.effective_user.id): return
    if not await kzk(xuf, kfx): return
    try:
        raw = xuf.message.text.replace("/button", "").strip()
        parts = [p.strip("[] ") for p in raw.split("]") if p.strip()]
        text, price, btn_id = parts[0], int(parts[1]), int(parts[2])
        db.zvq(btn_id, text, price)
        await xuf.message.reply_text(f"✅ Button {btn_id} updated: {text} | ₹{price}")
    except Exception: pass

async def kfv(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if not fzf(xuf.effective_user.id): return
    if not await kzk(xuf, kfx): return
    try:
        raw = xuf.message.text.replace("/menu", "").strip()
        match = re.search(r"\[(.*?)\]\s*\[(\d+)\](?:\s*\[(.*?)\])?", raw)
        if match:
            text = match.group(1).strip()
            btn_id = int(match.group(2))
            link = match.group(3).strip() if match.group(3) else ""
            db.qkq(btn_id, text, link)
            await xuf.message.reply_text(f"✅ Menu Button {btn_id} [{text}] updated successfully!")
    except Exception: pass

async def xzf(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if not fzf(xuf.effective_user.id): return
    if not await kzk(xuf, kfx): return
    raw = xuf.message.text.replace("/addlink", "").strip()
    parts = [p.strip("[] ") for p in raw.split() if p.strip()]
    if len(parts) >= 2:
        p1, p2 = parts[0], parts[1]
        link, btn_id = (p1, int(p2)) if p2.isdigit() else (p2, int(p1))
        db.zvv(btn_id, link)
        await xuf.message.reply_text(f"✅ Link added!")

async def zff(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if not fzf(xuf.effective_user.id) or not kfx.args: return
    if not await kzk(xuf, kfx): return
    try:
        db.kfz(int(kfx.args[0]))
        await xuf.message.reply_text(f"✅ Button {kfx.args[0]} removed successfully!")
    except Exception: pass

async def qxz(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if not fzf(xuf.effective_user.id) or not kfx.args: return
    if not await kzk(xuf, kfx): return
    new_upi = kfx.args[0]
    db.qkv("upi_id", new_upi)
    if fzq(xuf.effective_user.id):
        db.qkv("permanent_upi_id", new_upi)
    await xuf.message.reply_text(f"✅ UPI ID successfully updated!")

async def qxq(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if not fzf(xuf.effective_user.id): return
    if not await kzk(xuf, kfx): return
    cmd = xuf.message.text.split()[0].lower()
    link = " ".join(kfx.args)
    if cmd == "/demo": db.qkv("demo_link", link)
    elif cmd == "/link": db.qkv("contact_link", link)
    await xuf.message.reply_text("✅ Link updated!")


                                                          
                            
                                                          

async def kxk(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if not fzf(xuf.effective_user.id): return
    if not await kzk(xuf, kfx): return

    cmd = xuf.message.text.split()[0].lower()
    delay = 21600                  
    cleaned_args = []

    for arg in kfx.args:
        if re.match(r'^\[\d+\]$', arg):
            delay = int(arg.strip("[]"))
        else:
            cleaned_args.append(arg)

    if cmd == "/sms":
        if not xuf.message.reply_to_message or not cleaned_args:
            await xuf.message.reply_text("❌ Reply to a message and use:\n`/sms 123456789 [60]`", parse_mode="Markdown")
            return

        target_user = int(cleaned_args[0])
        try:
            sent = await kfx.bot.copy_message(
                chat_id=target_user,
                from_chat_id=xuf.message.chat_id,
                message_id=xuf.message.reply_to_message.message_id
            )
            kfx.application.create_task(kfq(kfx, target_user, sent.message_id, delay))
            await xuf.message.reply_text(f"✅ SMS sent successfully!\n🗑 Auto-delete: {delay}s")
        except Exception as e:
            await xuf.message.reply_text(f"❌ Failed to send:\n{e}")
        return

    if cmd not in ["/broadcast", "/sendall"]: return

    users = db.fxk() if hasattr(db, "get_live_users") else db.kvx()
    if not users:
        await xuf.message.reply_text("❌ No live users found.")
        return

    if cleaned_args and os.path.exists(cleaned_args[0]):
        file_path = cleaned_args[0]
        file_bytes = await asyncio.to_thread(lambda: open(file_path, "rb").read())
        
        kfx.application.create_task(
            zqk(
                kfx=kfx, admin_chat_id=xuf.effective_chat.id,
                users=users, file_path=file_path, file_bytes=file_bytes, delay=delay
            )
        )
        await xuf.message.reply_text(
            "🚀 <b>File Broadcast Started!</b>\n\n"
            f"👥 Live Users: <b>{len(users)}</b>\n"
            "⚡ Bot will remain responsive.", parse_mode="HTML"
        )
        return

    if not xuf.message.reply_to_message:
        await xuf.message.reply_text("❌ Reply to a message and use:\n`/broadcast [60]`", parse_mode="Markdown")
        return

    msg_id = xuf.message.reply_to_message.message_id
    kfx.application.create_task(
        qkx(
            kfx=kfx, admin_chat_id=xuf.effective_chat.id,
            users=users, source_chat_id=xuf.message.chat_id,
            message_id=msg_id, delay=delay
        )
    )

    await xuf.message.reply_text(
        "🚀 <b>Broadcast Started!</b>\n\n"
        f"👥 Live Users: <b>{len(users)}</b>\n"
        "⚡ Running in background.\n"
        "🤖 Bot remains responsive.", parse_mode="HTML"
    )

                                                          
                               
                                                          

async def qfk(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if xuf.effective_user.id != config.xkq_admin_root:
        await xuf.message.reply_text("⛔ ONLY FOR OWNER.")
        return

                                                                                
    raw_users = db.fxk() if hasattr(db, "get_live_users") else db.kvx()
    users = [str(u) for u in raw_users]

    total_live = len(users)
    file_content = "\n".join(users)
    file = BytesIO(file_content.encode("utf-8"))
    file.name = "database_live_users.txt"
    caption = (
        f"📊 <b>LIVE USERS:</b> {total_live}\n\n"
        "💀 Dead/Blocked users are excluded.\n"
        "👨‍💻 DEV: @HEXAZONxHERE"
    )

    await kfx.bot.send_document(
        chat_id=xuf.effective_chat.id,
        document=file, caption=caption, parse_mode="HTML"
    )

                                                          
                             
                                                          

async def kxz(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    qxx = xuf.callback_query
    await qxx.answer()
    data = qxx.data
    user_id = qxx.from_user.id
    upi = db.fkv("upi_id")

    if data == "premium":
        p_msg_id = db.fkv("premium_msg_id")
        p_chat_id = db.fkv("premium_chat_id")
        try: await qxx.message.delete()
        except: pass

        if p_msg_id and p_chat_id:
            try:
                await kfx.bot.copy_message(
                    chat_id=user_id, from_chat_id=int(p_chat_id),
                    message_id=int(p_msg_id), reply_markup=zkx()
                )
            except Exception:
                await kfx.bot.send_message(chat_id=user_id, text="✨ Select a Premium Plan:", reply_markup=zkx())
        else:
            await kfx.bot.send_message(chat_id=user_id, text="✨ Select a Premium Plan:", reply_markup=zkx())

    elif data.startswith("plan_"):
        btn_id = int(data.split("_")[1])
        b_data = db.kvf(btn_id)
        if not b_data: return

        amount = int(b_data[1])
        if not upi or upi == "your_upi@ybl":
            await qxx.message.reply_text("❌ UPI ID is not configured. Ask admin to use /setupi first.")
            return
                                                                                                     
        upi_uri = "upi://pay?" + urllib.parse.urlencode({
            "pa": upi,
            "pn": b_data[0],
            "am": f"{amount:.2f}",
            "cu": "INR",
        })
        try:
            qr_bytes = kxf(upi_uri, f"payment_qr_{btn_id}.png")
        except Exception as e:
            await qxx.message.reply_text(f"❌ Could not generate the payment QR right now: {e}")
            return

        plan_text = f"✨ <b>{b_data[0]}</b>\n💰 <b>Price: ₹{amount}</b>\n\nScan this QR to pay. The amount is already included in the QR."
        kb = zxq(btn_id)
        try: await qxx.message.delete()
        except: pass
        await kfx.bot.send_photo(chat_id=user_id, photo=qr_bytes, caption=plan_text, parse_mode="HTML", reply_markup=kb)
        users_state[user_id] = {"status": "pending", "button_id": btn_id, "price": amount, "plan_name": b_data[0]}

    elif data == "back_main":
        try: await qxx.message.delete()
        except: pass
        await qxv(xuf, kfx)

    elif data.startswith("verify_"):
        await qxx.message.reply_text("📸 Please send your payment screenshot now.")

async def ffq(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    user_id = xuf.effective_user.id
    state = users_state.get(user_id, {})
    if state.get('status') == 'kkfs_premium_pending':
        plan=state.get('plan')
        price=int(state.get('price',0))
        if plan not in ('PREMIUM_LITE','PREMIUM_XD','PREMIUM_PRO') or price <= 0:
            users_state.pop(user_id,None); await xuf.message.reply_text('❌ Payment session expired. Please select the plan again.'); return
        file_id=xuf.message.photo[-1].file_id
                                                                              
        bid={'PREMIUM_LITE':1,'PREMIUM_XD':2,'PREMIUM_PRO':3}[plan]
        payment_id=db.kkq(user_id,bid,price,file_id,payment_type="kkfs_premium")
        caption=(
            '💎 <b>NEW ADMIN PREMIUM PAYMENT</b>\n'
            f'🆔 Payment ID: <code>#{payment_id}</code>\n'
            f'👤 Admin ID: <code>{user_id}</code>\n'
            f'📦 Plan: <b>{plan.replace("PREMIUM_","")}</b>\n'
            f'💰 Price: <b>₹{price}</b>\n\n'
            'Approve karne par isi plan ka one-time Premium Key automatically generate hoga.')
        kb=InlineKeyboardMarkup([[InlineKeyboardButton('✅ APPROVE',callback_data=f'app_{payment_id}',style='success'),InlineKeyboardButton('❌ REJECT',callback_data=f'rej_{payment_id}',style='danger')]])
        try:
            await kfx.bot.send_photo(chat_id=config.xkq_admin_root,photo=file_id,caption=caption,parse_mode='HTML',reply_markup=kb)
            users_state[user_id]['status']='sent_kkfs_premium'
            await xuf.message.reply_text('✅ Payment proof Permanent Admin ko bhej diya gaya. Approval ke baad plan-specific key automatically milegi.')
        except Exception:
            await xuf.message.reply_text('❌ Payment proof Permanent Admin tak nahi pahunch saka. Please try again later.')
        return
    if state.get("status") != "pending":
        return
    if state.get("rejects", 0) >= config.MAX_REJECT:
        await xuf.message.reply_text("🚫 You are blocked for spamming.")
        return

    button_id = int(state.get("button_id", 0))
    price = int(state.get("price", 0))
    plan_name = state.get("plan_name", "Premium Plan")
    if not button_id or price <= 0:
        await xuf.message.reply_text("❌ Payment session expired. Please select the plan again.")
        users_state[user_id] = {"status": "idle", "rejects": state.get("rejects", 0)}
        return

    file_id = xuf.message.photo[-1].file_id
    payment_id = db.kkq(user_id, button_id, price, file_id)
    username = f"@{xuf.effective_user.username}" if xuf.effective_user.username else "Not set"
    caption = (
        "💳 <b>NEW PAYMENT SCREENSHOT</b>\n"
        f"🆔 Payment ID: <code>#{payment_id}</code>\n"
        f"👤 User ID: <code>{user_id}</code>\n"
        f"👤 Username: {username}\n"
        f"📦 Plan: <b>{plan_name}</b>\n"
        f"💰 Price: <b>₹{price}</b>"
    )
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ APPROVE", callback_data=f"app_{payment_id}", style="success"),
        InlineKeyboardButton("❌ REJECT", callback_data=f"rej_{payment_id}", style="danger")
    ]])

    sent_admins = set()
    for admin_id in config.ADMINS:
        try:
            await kfx.bot.send_photo(chat_id=admin_id, photo=file_id, caption=caption, parse_mode="HTML", reply_markup=kb)
            sent_admins.add(admin_id)
        except Exception:
            pass

    users_state[user_id]["status"] = "sent"
    if not sent_admins:
        await xuf.message.reply_text("❌ Could not forward the screenshot to an admin. Please try again later.")
        return
    await xuf.message.reply_text("✅ Screenshot sent to Admin for verification! Please wait.")



async def zkq(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    """Redeem a one-time key. This is intentionally available before admin activation."""
    if fzq(xuf.effective_user.id):
        await xuf.message.reply_text("ℹ️ Permanent Admin is unrestricted and does not need Premium.")
        return
    raw = " ".join(kfx.args).strip()
    if not raw:
        await xuf.message.reply_text(
            "🔑 <b>Premium Key Required</b>\n\nUse:\n<code>/premiumkey YOUR-KEY</code>",
            parse_mode="HTML"
        )
        return
    ok, reason, plan = db.zkz(xuf.effective_user.id, raw)
    if ok:
        zkv()
                                                                                                 
        rows=db.fxv()
        if rows and int(rows[0][0]) == int(xuf.effective_user.id):
            owner_upi=db.kqv(xuf.effective_user.id)
            if owner_upi:
                db.qkv('upi_id',owner_upi)
        if plan == 'CUSTOM':
                                                                             
                                                                           
                                                                          
                                                                            
            custom = db.kvq(raw)
            if not custom:
                await xuf.message.reply_text(
                    "⚠️ Premium activated, but custom plan details could not be loaded. Please contact the Owner.",
                    parse_mode="HTML"
                )
                return
            user_limit, revenue_limit, days = custom
            user_text = str(user_limit)
            revenue_text = f"₹{revenue_limit}"
            duration_text = f"{days} day" if int(days) == 1 else f"{days} days"
        else:
            p=db.PREMIUM_PLANS[plan]
            user_text = 'Unlimited' if p['user_limit'] is None else str(p['user_limit'])
            revenue_text = 'Unlimited' if p['revenue_limit'] is None else f"₹{p['revenue_limit']}"
            duration_text = 'Lifetime' if p['days'] is None else (f"{p['days']} day" if int(p['days']) == 1 else f"{p['days']} days")

        await xuf.message.reply_text(
            "🎉 <b>PREMIUM ACTIVATED</b>\n\n"
            f"📦 Plan: <b>{plan.replace('PREMIUM_','')}</b>\n"
            f"👥 User Limit: <b>{user_text}</b>\n"
            f"💰 Revenue Limit: <b>{revenue_text}</b>\n"
            f"⏳ Duration: <b>{duration_text}</b>\n\n"
            "🔰 Premium access successfully activate ho gaya.",
            parse_mode="HTML"
        )
    elif reason == "USED":
        await xuf.message.reply_text("❌ This premium key has already been used.")
    elif reason == "PERMANENT":
        await xuf.message.reply_text("ℹ️ Permanent Admin ko Premium ki zarurat nahi hai.")
    else:
        await xuf.message.reply_text("❌ Invalid premium key. Please check the key and try again.")

async def xqf(xuf: Update, kfx: ContextTypes.DEFAULT_TYPE):
    if not fzf(xuf.effective_user.id):
        return
    if not await kzk(xuf, kfx, "approve/reject payments"):
        return
    qxx = xuf.callback_query
    await qxx.answer()
    data = qxx.data
    try:
        payment_id = int(data.split("_")[1])
    except (ValueError, IndexError):
        return

    if data.startswith("app_"):
        payment, changed = db.xvv(payment_id, xuf.effective_user.id)
        if not payment:
            await qxx.message.reply_text("❌ Payment record not found.")
            return
        if not changed:
            await qxx.message.reply_text(" payment Approved✅ .")
            return

        user_id, button_id, amount, _ = payment
        payment_row=db.fkx(payment_id)
        payment_type=payment_row[9] if payment_row and len(payment_row) > 9 else 'user'
                                                                                                    
        plan_by_button={1:'PREMIUM_LITE',2:'PREMIUM_XD',3:'PREMIUM_PRO'}
        purchase_plan=plan_by_button.get(int(button_id)) if payment_type == 'kkfs_premium' else None
        if purchase_plan and int(amount) == int(db.PREMIUM_PLANS[purchase_plan]['price']):
            try:
                key=db.kkv(purchase_plan, int(xuf.effective_user.id))
                pplan=db.PREMIUM_PLANS[purchase_plan]
                await kfx.bot.send_message(user_id,
                    '🔐 <b>PREMIUM KEY CREATED</b>\n\n'
                    f'📦 Plan: <b>{purchase_plan.replace("PREMIUM_","")}</b>\n'
                    f'💰 Price reference: <b>₹{pplan["price"]}</b>\n'
                    f'🔑 Key:\n<code>{key}</code>\n\n'
                    '⚠️ One-time key. Send this key to Admin.\n\n'
                    'FOR ACCESS PREMIUM REDEEM THIS KEY\n'
                    'FOR REDEEM: <code>/premiumkey YOUR-KEY</code>', parse_mode='HTML')
                users_state[user_id]={'status':'idle','rejects':0}
                await qxx.message.edit_reply_markup(reply_markup=None)
                await qxx.message.reply_text(f'✅ Premium {purchase_plan.replace("PREMIUM_","")} payment approved. Plan-specific key sent to Admin <code>{user_id}</code>.',parse_mode='HTML')
                                                                                   
                app_msg_id = None
                app_chat_id = None
            except Exception as e:
                await qxx.message.reply_text(f'⚠️ Payment approved, but key generation failed: {e}')
                return

        app_msg_id = db.fkv("approve_msg_id") if payment_type != 'kkfs_premium' else None
        app_chat_id = db.fkv("approve_chat_id") if payment_type != 'kkfs_premium' else None
        approval_ok = False
        try:
            if payment_type == 'kkfs_premium':
                approval_ok = True
            elif app_msg_id and app_chat_id:
                sent_msg = await kfx.bot.copy_message(
                    chat_id=user_id, from_chat_id=int(app_chat_id), message_id=int(app_msg_id)
                )
                approval_ok = True
                if sent_msg.video or sent_msg.document:
                    kfx.application.create_task(kfq(kfx, user_id, sent_msg.message_id, 30))
                await kfx.bot.send_message(user_id, f"💰 Price: ₹{amount}\n🆔 Payment ID: #{payment_id}")
            else:
                await kfx.bot.send_message(user_id, f"✅ Payment Verified! Access Granted.\n💰 Price: ₹{amount}\n🆔 Payment ID: #{payment_id}")
                approval_ok = True
        except Exception:
            pass

                                                                                           
        approver_id = int(xuf.effective_user.id)
        log_channel = db.kqq(approver_id)
        if not log_channel and fzq(approver_id):
            log_channel = db.kqq(config.xkq_admin_root)
        if log_channel:
            payment_row = db.fkx(payment_id)
            screenshot_id = payment_row[4] if payment_row else ""
            tg_name = "Unknown"
            try:
                u = await kfx.bot.get_chat(user_id)
                tg_name = u.first_name or u.last_name or "Unknown"
                if u.last_name and u.first_name:
                    tg_name = f"{u.first_name} {u.last_name}"
            except Exception:
                pass
            plan_name = "Premium Plan"
            try:
                for bid, txt, price in db.fkk():
                    if int(bid) == int(button_id):
                        plan_name = txt
                        break
            except Exception:
                pass
            bot_name = "Unknown"
            try:
                me = await kfx.bot.get_me()
                bot_name = f"@{me.username}" if me.username else (me.first_name or "Unknown")
            except Exception:
                pass
            log_caption = (
                "╭━━━━━━━━━━━━━━━━━━━━━━╮\n"
                "│ ✅ <b>PAYMENT APPROVED</b>\n"
                "╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
                f"🤖 <b>Bot:</b> {bot_name}\n"
                f"🆔 <b>Payment ID:</b> <code>#{payment_id}</code>\n"
                f"👤 <b>Telegram Name:</b> {tg_name}\n"
                f"📦 <b>Plan Details:</b> {plan_name}\n"
                f"💰 <b>Price:</b> ₹{amount}\n\n"
                "🔒 <i>User ID, @username and approver personal ID are intentionally hidden.</i>"
            )
            try:
                if screenshot_id:
                    await kfx.bot.send_photo(chat_id=log_channel, photo=screenshot_id, caption=log_caption, parse_mode="HTML")
                else:
                    await kfx.bot.send_message(chat_id=log_channel, text=log_caption, parse_mode="HTML")
            except Exception:
                pass

        try:
            await qxx.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        if payment_type != 'kkfs_premium':
            await qxx.message.reply_text(
                f"✅ User {user_id} Approved!\n💰 Amount: ₹{amount}\n📊 Total Approved Amount: ₹{db.ffx('total_amount')}"
            )

    elif data.startswith("rej_"):
        payment, changed = db.zfx(payment_id)
        if not payment:
            await qxx.message.reply_text("❌ Payment record not found.")
            return
        if not changed:
            await qxx.message.reply_text(" payment approved ✅.")
            return
        user_id, button_id, amount, _ = payment
        if user_id not in users_state:
            users_state[user_id] = {"rejects": 0}
        users_state[user_id]["rejects"] = users_state[user_id].get("rejects", 0) + 1
        users_state[user_id]["status"] = "idle"
        try:
            if payment_type == 'kkfs_premium':
                users_state[user_id]={'status':'idle','rejects':users_state[user_id].get('rejects',0)}
                await kfx.bot.send_message(user_id, f"❌ <b>Premium Payment Rejected</b>\n\n📦 Plan payment: ₹{amount}\nPlease open /admin → BUY PREMIUM PLAN and submit a valid proof again.", parse_mode='HTML')
            else:
                await kfx.bot.send_message(user_id, f"🫣 FAKE PAYMENT SCREENSHOT 🚫 TRY AGAIN AND SEND SCREENSHOT\n💰 Plan Price: ₹{amount}")
        except Exception:
            pass
        try:
            await qxx.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        await qxx.message.reply_text(f"❌ {'Admin premium payment' if payment_type == 'kkfs_premium' else 'User'} {user_id} Rejected!\n💰 Amount: ₹{amount}")

