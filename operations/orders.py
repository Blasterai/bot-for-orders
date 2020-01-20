import datetime as dt
from typing import List

import attr
import pandas as pd

import settings
from utils.google.sheets import add_row_to_google_sheets
from utils.telegram import ui_text

ui_orders = ui_text.bot.text.orders


@attr.s(auto_attribs=True)
class Order:
    dt_created: dt.datetime
    order_id: int
    status: str  # TODO: Change to Literal: NEW / IN PROGRESS / DELIVERED...
    platform: str

    skus: str = attr.ib(default=None)
    total_amount: float = attr.ib(default=None)

    def __attrs_post_init__(self):
        if self.skus and isinstance(self.skus, list):
            self.skus = self._handle_skus()

    def _handle_skus(self):
        if self.skus != [None]:
            return ", ".join(self.skus)
        return

    def to_str(self) -> str:
        return ui_orders.order_template.format(
            order=self, dt_created=self.dt_created.strftime(settings.DT_FORMAT)
        )

    def to_list(self):
        return [
            self.platform,
            self.order_id,
            self.dt_created.strftime(settings.DT_FORMAT),
            self.status,
            self.skus,
            self.total_amount,
        ]

    def add_order_to_google_sheets(self):
        add_row_to_google_sheets(
            spreadsheet_id=settings.ORDERS_SPREADSHEET_ID,
            input_data=self.to_list(),
            range_name=settings.ORDERS_SHEET_RANGE_NAME,
        )
        return

    def change_status(self, status):
        self.status = status

    def change_status_in_google_sheets(self):
        pass


@attr.s(auto_attribs=True)
class Orders:
    orders: List[Order]

    @classmethod
    def from_etl_dataframe(cls, orders_df: pd.DataFrame):
        return Orders(orders=cls._get_orders_from_etl_df(orders_df))

    @classmethod
    def from_google_sheets_dataframe(cls, orders_df: pd.DataFrame):
        return Orders(orders=cls._get_orders_from_google_sheets_df(orders_df))

    @classmethod
    def _get_orders_from_etl_df(cls, df) -> List[Order]:
        return cls._get_orders_from_df(df, settings.ETL_ATTR_DICT)

    @classmethod
    def _get_orders_from_google_sheets_df(cls, df) -> List[Order]:
        return cls._get_orders_from_df(df, settings.GOOGLE_SHEETS_ATTR_DICT)

    @classmethod
    def _get_orders_from_df(cls, df, attr_dict: dict) -> List[Order]:
        orders: List[Order] = []
        for i, row in df.iterrows():
            orders.append(
                Order(
                    platform=row.get(attr_dict["platform"]),
                    order_id=row.get(attr_dict["order_id"]),
                    dt_created=cls.handle_datetime(row.get(attr_dict["dt_created"])),
                    status=cls.handle_status(row.get(attr_dict["status"])),
                    skus=row.get(attr_dict["skus"]),
                    total_amount=row.get(attr_dict["total_amount"]),
                )
            )
        return orders

    @staticmethod
    def handle_datetime(input_dt) -> dt.datetime:
        if isinstance(input_dt, str):
            return dt.datetime.strptime(input_dt, settings.DT_FORMAT)
        return input_dt

    @staticmethod
    def handle_status(input_status) -> str:
        if not input_status:
            return "NEW"
        else:
            return input_status

    def to_str(self) -> str:
        result = (
            ui_orders.orders_template_header.format(
                dt_created=dt.datetime.today().strftime(settings.DT_FORMAT)
            )
            + "\n"
        )
        for order in self.orders:
            result += order.to_str() + "\n\n"

        return result

    def add_orders_to_google_sheets(self):
        for order in self.orders:
            order.add_order_to_google_sheets()
        return
