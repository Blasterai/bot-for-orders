from telegram import Update, Bot, User
from telegram.ext import RegexHandler, CallbackContext


def unknown(update: Update, context: CallbackContext, **kwargs):
    bot: Bot = context.bot
    usr: User = update.effective_user

    bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, what?")
    bot.send_sticker(chat_id=usr.id, sticker="CAADBAADVgADLbceEsd4yvVL5yohAg")


unknown_h = RegexHandler(r"/.*", unknown)
