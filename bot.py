import logging
import os
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters

# --- Configuration ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8872190748:AAH4I-yRjxJIPs9YKya6i61n8ssrIUqgQxY")
OWNER_ID = int(os.environ.get("OWNER_ID", "8586849798"))

# --- Logging & Flask App ---
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# --- Telegram Bot Setup ---
bot = Bot(token=BOT_TOKEN)

# --- Authorization Check ---
def is_authorized(user_id):
    return user_id == OWNER_ID

# --- Command Handlers ---
async def start(update: Update, context):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 Access Denied! This bot is for owner only.")
        return
    await update.message.reply_text("✅ *VENOM X SMS Bot Active!*\n\nYour SMS will be forwarded here automatically.\n\n📌 *Commands:*\n• /start - Show this message",
                                    parse_mode="Markdown")

async def handle_sms(update: Update, context):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 Access Denied!")
        return
    sms_text = update.message.text
    formatted = f"📱 *New SMS Received*\n\n📝 {sms_text}"
    await update.message.reply_text(formatted, parse_mode="Markdown")

# --- Dispatcher Setup ---
dp = Dispatcher(bot, None)
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_sms))

# --- Webhook Endpoint for Telegram ---
@app.route('/webhook', methods=['POST'])
async def webhook():
    if request.method == 'POST':
        update = Update.de_json(request.get_json(force=True), bot)
        await dp.process_update(update)
        return 'ok', 200
    return 'Method Not Allowed', 405

@app.route('/')
def home():
    return "Bot is running!", 200

# --- Set Webhook (Run Once) ---
def set_webhook():
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    bot.delete_webhook()
    bot.set_webhook(url=webhook_url)
    logging.info(f"Webhook set to: {webhook_url}")

# --- Main Entry Point ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Only set webhook when running on Render (not locally)
    if os.environ.get('RENDER'):
        set_webhook()
    else:
        logging.info("Running locally, webhook not set.")
        # You can add app.run_polling() here for local testing if needed
    app.run(host='0.0.0.0', port=port)
