from loguru import logger
from telegram import Update, User, Bot, Message
from telegram.ext import CallbackContext

from handlers.main_commander import main_commander
from utils import log_this
from utils.telegram import ui_msg
from utils.telegram.decorators import catch_exceptions

# from utils.telegram.identify_user import check_rights


@log_this
@catch_exceptions
@main_commander.register("/help")
def help_command(update: Update, context: CallbackContext, **kwargs) -> Message:
    msg: Message = update.effective_message

    logger.error("User is asking for help")
    return msg.reply_text(ui_msg.GENERAL.HELP_MENU)
