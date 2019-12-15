import os
import argparse

from loguru import logger

from definitions import CONFIG_DIR


def _get_bot_token(bot_name: str):
    logger.info(f"Loading token for {bot_name}")
    credentials = gu.open_yml(os.path.join(CONFIG_DIR, "bot_credentials.yml"))
    if not credentials.get(bot_name):
        raise LookupError(f"credentials for {bot_name} not found")

    else:
        return credentials[bot_name]


def parse_run_args():
    logger.info("Parsing run arguments")
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("bot", type=str, help="Specify bot")
    args_parser.add_argument("mode", type=str, help="Specify run mode")

    run_args = args_parser.parse_args()

    if not run_args.bot:
        logger.error("No bot specified")
        exit(1)

    if not run_args.mode:
        logger.error("No mode specified")
        exit(1)

    try:
        token = _get_bot_token(run_args.bot)
    except LookupError as e:
        logger.error(f"{e}")
        exit(1)

    bot = run_args.bot
    mode = run_args.mode

    return mode, bot, token


# MODE, BOT, TOKEN = parse_run_args()
MODE = os.environ.get("MODE")
