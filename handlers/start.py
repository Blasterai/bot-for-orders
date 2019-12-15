from loguru import logger
from telegram import Message, Update, User
from telegram.ext import CallbackContext

from handlers.components.menu import start_menu_maker
from handlers.main_commander import main_commander


@main_commander.register("/start")
def start(update: Update, context: CallbackContext, **kwargs):
    usr: User = update.effective_user
    msg: Message = update.effective_message

    logger.info(f"Handling /start from {usr.full_name} ({usr.id}) with {kwargs}")

    return msg.reply_markdown(start_menu_maker())
