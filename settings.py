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
ORDERS_SHEET_RANGE_NAME = "Orders!A:D"
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
