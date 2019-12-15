import os
from datetime import datetime

from loguru import logger
from telegram.ext import Updater, Dispatcher

import settings
from handlers import main_command_handler


def _make_updater(read_timeout: int = 15, connect_timeout: int = 20):
    logger.info("Making updater")

    updater: Updater = Updater(
        settings.BOT_TOKEN,
        request_kwargs={
            "read_timeout": read_timeout,
            "connect_timeout": connect_timeout,
        },
        use_context=True,
    )

    return updater


def main():
    updater: Updater = _make_updater()
    dp: Dispatcher = updater.dispatcher

    dp.add_handler(main_command_handler)

    start_log_message = (
        f'Blaster Bot: started on {datetime.now().strftime("%d.%m.%Y at %H:%M:%S")}'
    )

    logger.info("Starting in polling mode")
    if os.environ.get("SUPERADMIN"):
        updater.bot.send_message(os.environ.get("SUPERADMIN"), start_log_message)
    updater.start_polling()

    logger.info(start_log_message)


if __name__ == "__main__":
    main()
