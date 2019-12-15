from random import randint
import datetime as dt

from envparse import env

# Bot
BOT_TOKEN = env("BOT_TOKEN")
ADMINS = env("ADMINS", cast=tuple, subcast=int)
APP_NAME = env("APP_NAME", default=None)

# Google API
SCOPES = env(
    "SCOPES",
    default=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ],
)
ORDERS_SPREADSHEET_ID = env(
    "SPREADSHEET_ID", default="1jRUWHa7SQuG1KymwNp9uipga_5CSlnjBFQS7lNbjGRI"
)
ORDERS_SHEET_RANGE_NAME = "Orders!A:F"
ORDERS_CONFIG_SHEET_NAME = "Config"


def random_with_n_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


TEST_NEW_ORDER_DATA = [
    random_with_n_digits(10),
    dt.datetime.today().strftime("%d.%m.%Y %H:%M"),
    "TEST",
]

DT_FORMAT = "%d.%m.%Y %H:%M"

ETL_ATTR_DICT = {
    "platform": "platform",
    "order_id": "order_id",
    "dt_created": "dt_created",
    "status": "status",
    "skus": "order_skus",
    "total_amount": "total_amount",
}

GOOGLE_SHEETS_ATTR_DICT = {
    "platform": "Platform",
    "order_id": "Order ID",
    "dt_created": "Datetime created",
    "status": "Status",
    "skus": "SKUs",
    "total_amount": "Total amount",
}
