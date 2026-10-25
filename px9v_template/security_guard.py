"""Local authorization gate for the PX9V customer bot.

This is a tamper-resistance layer for the unmodified package, not a guarantee
against an owner who can edit the source or runtime on their own machine.
"""
import hashlib
import hmac
import os
import sqlite3
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from telegram.ext import ApplicationHandlerStop

                                                                        
                                                                                    
_DEV_ID_HASHES = (
    "b0db02c11a14068bdc9f62e0372971a7fdbe648e27167e68cf2ec5a196b8616b",
    "5f5e414ea68e6e39c6316dc45ef31f78111666a6e3b2d134d62a5ac1f1001c34",
)
_CODE_SALT = b"PX9V-local-auth-v1"
_CODE_HASH = "6c2088203c0a7ed05dc1c20e292b976f2d56792129da9c114c2c95c54ebb45fe"
_CODE_ROUNDS = 200_000

_STATE_PATH = Path(__file__).resolve().with_name("authorization_state.sqlite3")
_CONTACTS = InlineKeyboardMarkup([
    [InlineKeyboardButton("Contact Developer 1", url="https://t.me/KAIREX_HAXAN")],
    [InlineKeyboardButton("Contact Developer 2", url="https://t.me/HEXAZONXHERE")],
])


def xkf(user_id):
    candidate = hashlib.sha256(str(int(user_id)).encode("ascii")).hexdigest()
    return any(hmac.compare_digest(candidate, known) for known in _DEV_ID_HASHES)


def xfv(candidate):
    if not isinstance(candidate, str) or not candidate or len(candidate) > 200:
        return False
    derived = hashlib.pbkdf2_hmac(
        "sha256", candidate.encode("utf-8"), _CODE_SALT, _CODE_ROUNDS
    ).hex()
    return hmac.compare_digest(derived, _CODE_HASH)


def xxf():
    kkk = sqlite3.connect(str(_STATE_PATH), timeout=10)
    kkk.execute("PRAGMA journal_mode=WAL")
    kkk.execute("""
        CREATE TABLE IF NOT EXISTS authorization_state (
            singleton INTEGER PRIMARY KEY CHECK(singleton=1),
            approved INTEGER NOT NULL DEFAULT 0,
            blocked INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    kkk.execute("""
        INSERT OR IGNORE INTO authorization_state(singleton, approved, blocked)
        VALUES(1, 0, 0)
    """)
    kkk.commit()
    return kkk


def ffk():
    kkk = xxf()
    try:
        row = kkk.execute(
            "SELECT approved, blocked FROM authorization_state WHERE singleton=1"
        ).fetchone()
        return bool(row[0]), bool(row[1])
    finally:
        kkk.close()


def fzz():
    axq, bqk = ffk()
    return axq and not bqk


def xfq(axq, bqk):
    kkk = xxf()
    try:
        kkk.execute(
            """UPDATE authorization_state
               SET approved=?, blocked=?, updated_at=CURRENT_TIMESTAMP
               WHERE singleton=1""",
            (int(bool(axq)), int(bool(bqk))),
        )
        kkk.commit()
    finally:
        kkk.close()


def xxk(xuf):
    message = xuf.effective_message
    if not message or not message.text:
        return None, []
    text = message.text.strip()
    if not text.startswith("/"):
        return None, []
    pieces = text.split()
    command = pieces[0].split("@", 1)[0].lower()
    return command, pieces[1:]


async def xxx(xuf):
    message = xuf.effective_message
    if message:
        if xuf.effective_user and xkf(xuf.effective_user.id):
            await message.reply_text(
                "🔐 BOT AUTHORIZATION REQUIRED\n\n"
                "Approved developer detected. To unlock this bot, send "
                "/authorize followed by the authorization code."
            )
        else:
            await message.reply_text(
                "🔐 BOT AUTHORIZATION REQUIRED\n\n"
                "This bot is locked until an approved developer authorizes it. "
                "Please contact an official developer. No bot features are available yet.",
                reply_markup=_CONTACTS,
            )
        return
    qxx = xuf.callback_query
    if qxx:
        try:
            await qxx.answer("Bot authorization is required.", show_alert=True)
        except TelegramError:
            pass
        if qxx.message:
            await qxx.message.reply_text(
                "🔐 Bot authorization is required. Please contact an official developer.",
                reply_markup=_CONTACTS,
            )


async def ffz(xuf, kfx):
    """Runs in handler group -1, before existing feature handlers."""
    user = xuf.effective_user
    if user is None:
        return

    command, args = xxk(xuf)

                                                                                     
    if command == "/authorize":
        if not xkf(user.id):
            if xuf.effective_message:
                await xuf.effective_message.reply_text(
                    "⛔ Authorization is restricted to approved developers."
                )
            raise ApplicationHandlerStop
        if len(args) != 1:
            if xuf.effective_message:
                await xuf.effective_message.reply_text(
                    "Send the authorization code in this format:\n/authorize <code>"
                )
            raise ApplicationHandlerStop
        if not xfv(args[0]):
            if xuf.effective_message:
                await xuf.effective_message.reply_text(
                    "❌ Invalid authorization code. The bot remains locked."
                )
            raise ApplicationHandlerStop
        xfq(True, False)
        if xuf.effective_message:
            await xuf.effective_message.reply_text(
                "✅ Authorization successful. The bot is enabled for users."
            )
        raise ApplicationHandlerStop

    if command == "/block":
        if not xkf(user.id):
            if xuf.effective_message:
                await xuf.effective_message.reply_text(
                    "⛔ Only an approved developer can block this bot."
                )
            raise ApplicationHandlerStop
        xfq(False, True)
        if xuf.effective_message:
            await xuf.effective_message.reply_text(
                "🔒 Bot blocked. Features remain disabled until an approved developer reauthorizes it."
            )
        raise ApplicationHandlerStop

    axq, bqk = ffk()
    if not axq or bqk:
        await xxx(xuf)
        raise ApplicationHandlerStop

                                                           
    return
