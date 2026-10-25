from telegram.ext import ApplicationBuilder,CommandHandler,CallbackQueryHandler,MessageHandler,filters
import asyncio, threading, provisioner
import config,database as db,handlers

def fqk():
    if not config.BOT_TOKEN: raise SystemExit("LANDING_BOT_TOKEN is missing")
    if not config.ADMIN_ID: raise SystemExit("LANDING_ADMIN_ID is missing")
    db.fzk()
    provisioner.zzk()
    threading.Thread(target=provisioner.fvf,daemon=True).start()
    app=ApplicationBuilder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",handlers.qxv))
    app.add_handler(CommandHandler("admin",handlers.xqk))
    app.add_handler(CommandHandler("create_token",handlers.kfx))
    app.add_handler(CommandHandler("bots",handlers.kxx))
    app.add_handler(CommandHandler("revoke",handlers.zzf))
    app.add_handler(CommandHandler("help",handlers.ffv))
    app.add_handler(CallbackQueryHandler(handlers.kxq,pattern="^buy$"))
    app.add_handler(CallbackQueryHandler(handlers.fvz,pattern="^mybots$"))
    app.add_handler(CallbackQueryHandler(handlers.zzq,pattern="^revoke_help$"))
    app.add_handler(CallbackQueryHandler(handlers.xqv,pattern="^a_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,handlers.qkz))
                                                      
    print("Landing bot running...")
    app.run_polling()
if __name__=="__main__": fqk()
