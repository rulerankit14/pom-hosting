import sys
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, TypeHandler, filters
)

import config
import database as db
import handlers as h
import security_guard

async def zxv(application):
    application.create_task(h.fvk(application.bot))

def fqk():
    if not config.BOT_TOKEN:
        print("❌ Error: Cannot start bot without a valid BOT_TOKEN.")
        sys.exit(1)

    print("🤖 Initializing Bot Database...")
    db.fzk()

    print("🤖 Starting Bot Application Engine...")
    app = ApplicationBuilder().token(config.BOT_TOKEN).post_init(zxv).build()

                                                      
    app.add_handler(TypeHandler(Update, security_guard.ffz), group=-1)

                                
                        
                                
    app.add_handler(CommandHandler("start", h.qxv))
    app.add_handler(CommandHandler("admin", h.kfk))
    app.add_handler(CommandHandler("padmin", h.zxx))
    app.add_handler(CommandHandler("premiumkey", h.zkq))
    
                            
    app.add_handler(CommandHandler("welcome", h.qxf))
    app.add_handler(CommandHandler("setwelcome", h.qxf))
    app.add_handler(CommandHandler("setpremium", h.qxk))
    app.add_handler(CommandHandler("setapprove", h.zvk))
    
                   
    app.add_handler(CommandHandler("button", h.zvf))
    app.add_handler(CommandHandler("menu", h.kfv))
    app.add_handler(CommandHandler(["demo", "link"], h.qxq))
    app.add_handler(CommandHandler("setupi", h.qxz))
    app.add_handler(CommandHandler("addlink", h.xzf))
    app.add_handler(CommandHandler("remove", h.zff))
    app.add_handler(CommandHandler("menucolor", h.qxx))
    app.add_handler(CommandHandler("buttoncolor", h.zvz))
    app.add_handler(CommandHandler("addlogchnl", h.xzz))
    
                                     
    app.add_handler(CommandHandler("save", h.zqf))
    app.add_handler(CommandHandler("fset", h.kzv))
    
                          
    app.add_handler(CommandHandler(["broadcast", "sendall", "sms"], h.kxk))
    app.add_handler(CommandHandler("database", h.qfk))
    app.add_handler(CommandHandler("adddata", h.xzk))
    app.add_handler(CommandHandler("cmds", h.fzv))

                                
                        
                                
                                   
    app.add_handler(CallbackQueryHandler(h.xqf, pattern="^(app_|rej_)"))
                                                              
    app.add_handler(CallbackQueryHandler(h.zxk, pattern="^padmin_"))
    app.add_handler(CallbackQueryHandler(h.xqq, pattern="^admin_"))
                                      
    app.add_handler(CallbackQueryHandler(h.kxz))

                                
                        
                                
                                                          
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, h.xvk), group=1)
    
                                             
    app.add_handler(MessageHandler(filters.PHOTO, h.ffq), group=2)

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    fqk()
