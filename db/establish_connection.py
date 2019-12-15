import os

from sqlalchemy import engine

from loguru import logger


def create_postgres_engine():
    logger.debug("Creating postgresql engine")
    return engine.create_engine(
        f"""postgresql+psycopg2://{os.environ.get("DB_USER")}:{os.environ.get("DB_PASSWORD")}@{os.environ.get(
            "DB_HOST")}:{os.environ.get("DB_PORT")}/{os.environ.get("DB_NAME")}"""
    )
