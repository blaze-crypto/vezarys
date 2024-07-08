import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.handlers import router
from app.database.data import initialize_db
from dotenv import load_dotenv
import os
import signal

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Bot token not provided")

logging.basicConfig(level=logging.INFO)

async def main():
    initialize_db()

    storage = MemoryStorage()
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher(storage=storage)
    dp.include_router(router)

    async def on_shutdown(dispatcher: Dispatcher):
        logging.info("Shutting down dispatcher...")
        await dispatcher.storage.close()
        await dispatcher.storage.wait_closed()
        await bot.session.close()
        logging.info("Bot shutdown completed.")

    try:
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        logging.warning("Bot has been interrupted")
    finally:
        await on_shutdown(dp)

def handle_sigterm():
    raise KeyboardInterrupt

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, handle_sigterm)
    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        logging.warning("Bot has been interrupted")
    finally:
        loop.close()
