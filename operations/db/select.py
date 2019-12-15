import datetime as dt
from typing import List

from db.establish_connection import create_postgres_engine
import pandas as pd


def select_all_orders() -> pd.DataFrame:
    db_engine = create_postgres_engine()
    query = f"""
    SELECT * 
    FROM reports.all_mdnt45_orders
    """
    return pd.read_sql_query(query, db_engine)


def select_orders_by_start_end_dates(
    start_date: dt.datetime, end_date: dt.datetime
) -> pd.DataFrame:
    db_engine = create_postgres_engine()
    query = f"""
    SELECT * 
    FROM reports.all_mdnt45_orders
    WHERE dt_created >= '{start_date}' and dt_created < '{end_date}'
    """
    return pd.read_sql_query(query, db_engine)


def select_orders_by_start_date(start_date: dt.datetime) -> pd.DataFrame:
    db_engine = create_postgres_engine()
    query = f"""
    SELECT * 
    FROM reports.all_mdnt45_orders
    WHERE dt_created >= '{start_date}'
    """
    return pd.read_sql_query(query, db_engine)


def select_orders_by_order_ids(order_ids: List[int]) -> pd.DataFrame:
    db_engine = create_postgres_engine()
    query = f"""
    SELECT * 
    FROM reports.all_mdnt45_orders
    WHERE order_id::text = ANY(ARRAY{order_ids})
    """
    return pd.read_sql_query(query, db_engine)
