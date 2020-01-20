import re

from loguru import logger
from telegram import Message, Update
from telegram.ext import (
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
)

from utils.telegram.decorators import conversation_next

STATUS_RECEIVED = range(1)


def change_order_status(update: Update, context: CallbackContext, **kwargs):
    msg: Message = update.effective_message
    user_data: dict = context.user_data

    order_id = re.findall("/changestatus(\d+)", msg.text)[0]
    logger.info(f"Changing order status. Order ID: {order_id}")

    return request_status(update, context)


@conversation_next(next_step=STATUS_RECEIVED)
def request_status(update: Update, context: CallbackContext, **kwargs):
    msg: Message = update.effective_message
    user_data: dict = context.user_data

    return msg.reply_markdown(f"Status changed")


change_order_status_conv_handler: ConversationHandler = ConversationHandler(
    entry_points=[
        MessageHandler(Filters.regex(r"/changestatus\d+"), change_order_status)
    ],
    states={},
    fallbacks=[],
    persistent=False,
    name="change_order_status",
    allow_reentry=True,
)
