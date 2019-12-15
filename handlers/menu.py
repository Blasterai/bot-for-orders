from telegram import Message, Update, User
from telegram.ext import CallbackContext

from handlers.main_commander import main_commander
from utils.telegram import ui_text


@main_commander.register("/ordersmenu")
def start(update: Update, context: CallbackContext, **kwargs):
    usr: User = update.effective_user
    msg: Message = update.effective_message

    return msg.reply_markdown(ui_text.bot.text.menu.orders_menu)


@main_commander.register("/availablereports")
def start(update: Update, context: CallbackContext, **kwargs):
    usr: User = update.effective_user
    msg: Message = update.effective_message

    return msg.reply_markdown(ui_text.bot.text.menu.reports_menu)
