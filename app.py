import os
import asyncio
import logging
from flask import Flask, jsonify
from threading import Thread
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
bot_status = {"status": "stopped", "thread": None}

@app.route('/')
def home():
    return "🦆 DUCK SPAM БОТ работает! Статус: " + str(bot_status)

@app.route('/status')
def status():
    return jsonify(bot_status)

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    try:
        logger.info("🚀 Запуск бота...")
        from main import main
        asyncio.run(main())
    except Exception as e:
        logger.error(f"❌ Ошибка бота: {e}")
        bot_status["status"] = "error"
        bot_status["error"] = str(e)

if __name__ == "__main__":
    bot_status["status"] = "starting"
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    time.sleep(2)
    bot_status["status"] = "running"
    bot_status["thread"] = str(bot_thread)
    
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"🌐 Веб-сервер запущен на порту {port}")
    app.run(host='0.0.0.0', port=port, threaded=True)
