import datetime as dt
from telegram import Update, Message
from telegram.ext import CallbackContext

import settings
from handlers.main_commander import main_commander
from operations.db.select import select_orders_by_order_ids
from operations.orders import Orders
from utils import log_this
from utils.google.sheets import get_df_from_google_sheets
from utils.telegram.decorators import catch_exceptions


@log_this
@catch_exceptions
@main_commander.register("/activeorders")
def active_orders(update: Update, context: CallbackContext, **kwargs) -> Message:
    msg: Message = update.effective_message

    df = get_df_from_google_sheets(
        settings.ORDERS_SPREADSHEET_ID, settings.ORDERS_SHEET_RANGE_NAME
    )
    active_orders_ids = df[df["Status"] == "ACTIVE"]["Order ID"].tolist()
    active_orders_df = select_orders_by_order_ids(active_orders_ids)
    orders = Orders.from_etl_dataframe(active_orders_df)

    return msg.reply_text(orders.to_str())


@log_this
@catch_exceptions
@main_commander.register("/todayorders")
def active_orders(update: Update, context: CallbackContext, **kwargs) -> Message:
    msg: Message = update.effective_message

    df = get_df_from_google_sheets(
        settings.ORDERS_SPREADSHEET_ID, settings.ORDERS_SHEET_RANGE_NAME
    )
    df["Date created"] = df["Date created"].apply(
        lambda x: dt.datetime.strptime(x, settings.DT_FORMAT)
    )
    active_orders_ids = df[df["Date created"] >= dt.datetime.today().date()][
        "Order ID"
    ].tolist()
    active_orders_df = select_orders_by_order_ids(active_orders_ids)
    orders = Orders.from_etl_dataframe(active_orders_df)

    return msg.reply_text(orders.to_str())
