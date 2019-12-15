import datetime as dt

from utils.google.sheets import get_cell_value, write_to_cell
import settings


def get_last_update_dt_of_orders_google_sheet():
    last_update_dt = get_cell_value(
        settings.ORDERS_SPREADSHEET_ID, settings.ORDERS_CONFIG_SHEET_NAME, 1, "B"
    )[0][0]
    last_update_dt = dt.datetime.strptime(last_update_dt, settings.DT_FORMAT)
    return last_update_dt


def change_last_update_dt_of_orders_google_sheet(new_last_update_dt: str):
    write_to_cell(
        settings.ORDERS_SPREADSHEET_ID,
        settings.ORDERS_CONFIG_SHEET_NAME,
        1,
        "B",
        new_last_update_dt,
    )
    return new_last_update_dt
