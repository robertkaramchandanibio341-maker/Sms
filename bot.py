import logging
import threading
import os
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== CONFIG (Render Environment Variables Se Lega) ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8872190748:AAH4I-yRjxJIPs9YKya6i61n8ssrIUqgQxY")
OWNER_ID = int(os.environ.get("OWNER_ID", "8586849798"))
# ===================================================================

# Flask app (Render health check ke liye)
app_flask = Flask(__name__)

@app_flask.route('/')
@app_flask.route('/health')
def health():
    return "✅ Bot is running!", 200

# Telegram Bot Setup
logging.basicConfig(level=logging.INFO)

def is_authorized(user_id):
    return user_id == OWNER_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 Access Denied! This bot is for owner only.")
        return
    
    await update.message.reply_text(
        "✅ *VENOM X SMS Bot Active!*\n\n"
        "Your SMS will be forwarded here automatically.\n"
        "This bot is private and only you can use it.\n\n"
        "📌 *Commands:*\n"
        "• /start - Show this message\n"
        "• /id - Get your Telegram ID\n\n"
        "🔐 *Security:* Only approved users can access this bot.",
        parse_mode="Markdown"
    )

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 Access Denied!")
        return
    await update.message.reply_text(f"🆔 Your Telegram ID: `{user_id}`", parse_mode="Markdown")

async def handle_sms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        print(f"⚠️ Unauthorized attempt from user: {user_id}")
        await update.message.reply_text("🚫 Access Denied!")
        return
    
    sms_text = update.message.text
    formatted = f"📱 *New SMS Received*\n\n📝 {sms_text}"
    await update.message.reply_text(formatted, parse_mode="Markdown")

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 Access Denied!")
        return
    
    await update.message.reply_text("❌ Unknown command. Use /start")

def run_bot():
    """Bot ko polling mode mein chalao"""
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_sms))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    print("🤖 VENOM X SMS Bot started in polling mode...")
    print(f"✅ Owner ID: {OWNER_ID}")
    app.run_polling()

if __name__ == "__main__":
    # Bot ko background thread mein start karo
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Flask app run karo (Render ke liye port listen karna zaroori hai)
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Flask server running on port {port}...")
    app_flask.run(host="0.0.0.0", port=port)