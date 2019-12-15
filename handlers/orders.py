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

    orders_df = get_df_from_google_sheets(
        settings.ORDERS_SPREADSHEET_ID, settings.ORDERS_SHEET_RANGE_NAME
    )
    active_orders_df = orders_df[orders_df["Status"] == "ACTIVE"].copy()

    # active_orders_ids = active_orders_df["Order ID"].tolist()
    # active_orders_df_from_etl = select_orders_by_order_ids(active_orders_ids)

    orders = Orders.from_google_sheets_dataframe(active_orders_df)
    return msg.reply_text(orders.to_str())


@log_this
@catch_exceptions
@main_commander.register("/readytodeliverorders")
def active_orders(update: Update, context: CallbackContext, **kwargs) -> Message:
    msg: Message = update.effective_message

    orders_df = get_df_from_google_sheets(
        settings.ORDERS_SPREADSHEET_ID, settings.ORDERS_SHEET_RANGE_NAME
    )
    active_orders_df = orders_df[orders_df["Status"] == "READY TO DELIVER"].copy()

    # active_orders_ids = active_orders_df["Order ID"].tolist()
    # active_orders_df_from_etl = select_orders_by_order_ids(active_orders_ids)

    orders = Orders.from_google_sheets_dataframe(active_orders_df)
    return msg.reply_text(orders.to_str())


@log_this
@catch_exceptions
@main_commander.register("/todayorders")
def today_orders(update: Update, context: CallbackContext, **kwargs) -> Message:
    msg: Message = update.effective_message

    df = get_df_from_google_sheets(
        settings.ORDERS_SPREADSHEET_ID, settings.ORDERS_SHEET_RANGE_NAME
    )
    df["Datetime created"] = df["Datetime created"].apply(
        lambda x: dt.datetime.strptime(x, settings.DT_FORMAT)
    )
    today_orders_df = df[
        df["Datetime created"] >= dt.datetime.today().date()
    ].copy()  # TODO: Fix warning

    # today_orders_ids = today_orders_df["Order ID"].tolist()
    # today_orders_df_from_etl = select_orders_by_order_ids(today_orders_ids)

    orders = Orders.from_google_sheets_dataframe(
        today_orders_df
    )  # TODO: Fix status handling

    return msg.reply_text(orders.to_str())
