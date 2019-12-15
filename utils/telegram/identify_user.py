from typing import Sequence

from decorator import decorator
from loguru import logger
from telegram import Update, User

from services import api_users


@decorator
def check_rights(func, groups: Sequence = ("sales_data_read",), *args, **kwargs):
    update: Update = args[0]
    usr: User = update.effective_user

    user = api_users.find_by_telegram_id(usr.id)
    if not user:
        logger.info(f"User not found: {usr.id}")
        return

    if user.is_admin or user.is_owner:
        return func(*args, **kwargs)

    for level in groups:
        if user.id in api_users.get_group_member_ids(level):
            logger.info(f"Fetched members for {level}")
            return func(*args, **kwargs)
    logger.info(f"No rights to run {func.__name__} for user {usr.id}")
    return
