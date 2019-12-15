import datetime as dt

from loguru import logger

from operations.db.select import select_orders_by_start_date
from operations.google_sheets.orders import (
    get_last_update_dt_of_orders_google_sheet,
    change_last_update_dt_of_orders_google_sheet,
)
from operations.orders import Orders
import settings


def main_workflow():
    logger.info("Getting last update datetime")
    last_update_dt = get_last_update_dt_of_orders_google_sheet()
    new_last_update_dt = dt.datetime.now()

    logger.info("Checking for new orders")
    new_orders_df = select_orders_by_start_date(last_update_dt)

    if new_orders_df.shape[0]:
        logger.info(f"There are {new_orders_df.shape[0]} new orders")
        new_orders: Orders = Orders.from_etl_dataframe(new_orders_df)

        logger.info(f"Saving new orders to google sheet")
        new_orders.add_orders_to_google_sheets()
    else:
        logger.info("There is no new orders")

    logger.info("Changing last update datetime")
    change_last_update_dt_of_orders_google_sheet(
        new_last_update_dt.strftime(settings.DT_FORMAT)
    )
    return


if __name__ == "__main__":
    main_workflow()
