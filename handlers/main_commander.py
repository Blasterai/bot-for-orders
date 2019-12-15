from telegram import Update
from telegram.ext import MessageHandler, Filters, CallbackContext

from utils.telegram import command_dispatch


@command_dispatch
def main_commander(update: Update, context: CallbackContext):
    raise NotImplementedError


main_command_handler = MessageHandler(Filters.command, main_commander)
