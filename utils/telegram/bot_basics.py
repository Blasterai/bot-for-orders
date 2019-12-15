import os
import time
from collections import namedtuple, Iterable
from math import ceil

import telegram
from loguru import logger
from telegram import (
    MAX_MESSAGE_LENGTH,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.error import BadRequest, NetworkError, TimedOut, TelegramError

from utils.general import open_yml
from utils.telegram import ui_msg

Buttons = namedtuple("Buttons", "main_buttons, header_buttons, footer_buttons")


def send_message(
    bot,
    user_id,
    response,
    parse_mode=telegram.ParseMode.MARKDOWN,
    reply_markup=None,
    disable_web_page_preview=True,
):
    if not response:
        logger.error("No response to send")
        return

    try:
        if len(response) < MAX_MESSAGE_LENGTH:
            return bot.send_message(
                chat_id=user_id,
                text=response,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                disable_web_page_preview=disable_web_page_preview,
            )
        else:
            chunks, chunk_size = len(response), MAX_MESSAGE_LENGTH
            split_message = [
                response[i : i + chunk_size] for i in range(0, chunks, chunk_size)
            ]
            for i in range(len(split_message)):
                if i < (len(split_message) - 1):
                    bot.send_message(
                        chat_id=user_id,
                        text=split_message[i],
                        parse_mode=parse_mode,
                        reply_markup=reply_markup,
                        disable_web_page_preview=disable_web_page_preview,
                    )
                    time.sleep(1)
                else:
                    return bot.send_message(
                        chat_id=user_id,
                        text=split_message[i],
                        parse_mode=parse_mode,
                        reply_markup=reply_markup,
                        disable_web_page_preview=disable_web_page_preview,
                    )
    except UnicodeEncodeError as e:
        logger.warning(f"send_message: {e}")
    except BadRequest as e:
        logger.error(f"{e}: {user_id}")
    except NetworkError:
        logger.error(NetworkError)


def reply(update, message, reply_markup=None):
    if not reply_markup:
        reply_markup = ReplyKeyboardRemove()
    try:
        return update.message.reply_text(
            message, reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN
        )
    except AttributeError as e:
        logger.error(f"Failed to reply: {e}")


def alert_admin(bot, message, reply_markup=None):
    log_message = message.replace("\n", "").replace("```", "")
    logger.warning(f"Alerting admin: {log_message}")
    send_message(
        bot,
        os.environ["ADMINS"][0],
        f"*ADMIN ALERT*:\n\n{message.lstrip()}",
        reply_markup=reply_markup,
    )


def error_callback(bot, update, error):
    try:
        try:
            # Check if update is present in error callback and include it in report
            if update.effective_user:
                alert_admin(
                    bot,
                    f"`{error}` on {update.effective_user.full_name} ({update.effective_user.id})",
                )
        except AttributeError:
            alert_admin(bot, f"`{error}`")

        logger.error(error)
        raise error
    # except Unauthorized:
    #     # remove update.message.chat_id from conversation list
    except BadRequest:
        logger.error("BadRequest: {}\n{}".format(BadRequest, update))
    except TimedOut:
        logger.error("TimedOut: {}".format(TimedOut))
    except NetworkError:
        logger.error(f"NetworkError: {NetworkError}")
    # except ChatMigrated as e:
    #     # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        logger.error(f"{TelegramError}. Update: {update}")
    except AttributeError as e:
        alert_admin(bot, f"{e}")
    except ModuleNotFoundError as e:
        logger.error(e)


def remove_reply_markup(bot, chat_data: dict):
    if not isinstance(chat_data, dict):
        raise ValueError(f"chat_data must be dict, not {type(chat_data)}")
    if chat_data.get("sent"):
        try:
            logger.debug("Removing markup")
            bot.edit_message_reply_markup(
                chat_id=chat_data["sent"]["chat_id"],
                message_id=chat_data["sent"]["message_id"],
                reply_markup=None,
            )
            del chat_data["sent"]
            return True
        except BadRequest as e:
            logger.warning(e)
            return False


def build_menu(main_buttons, n_cols, header_buttons=None, footer_buttons=None):
    header_keyboard, footer_keyboard = None, None

    main_keyboard = [
        InlineKeyboardButton(v, callback_data=k) for k, v in main_buttons.items()
    ]

    if footer_buttons:
        footer_keyboard = [
            InlineKeyboardButton(v, callback_data=k) for k, v in footer_buttons.items()
        ]

    if header_buttons:
        header_keyboard = [
            InlineKeyboardButton(v, callback_data=k) for k, v in header_buttons.items()
        ]

    menu = [main_keyboard[i : i + n_cols] for i in range(0, len(main_keyboard), n_cols)]
    if header_keyboard:
        menu.insert(0, header_keyboard)
    if footer_keyboard:
        menu.append(footer_keyboard)
    return menu


def get_info_from_user(
    bot, update, chat_data, message_text, buttons, replace_prev_message=False
):
    logger.debug(f"Generating information request {update.effective_user.full_name}")
    reply_markup = InlineKeyboardMarkup(
        build_menu(
            main_buttons=buttons.main_buttons,
            footer_buttons=buttons.footer_buttons,
            header_buttons=buttons.header_buttons,
            n_cols=1,
        )
    )

    logger.debug("Checking for callback query")
    query = None
    if update.callback_query:
        query = update.callback_query

    logger.debug(f"Query found: {bool(query)}")

    if not query:
        logger.debug("Sending reply (no query found)")
        chat_data["sent"] = reply(update, message_text, reply_markup)
        logger.debug("Reply sent, returning.")
        return chat_data["sent"]

    logger.debug("Checking if replace previous is True")
    if replace_prev_message is True:
        logger.debug("Replacing previous")
        try:
            logger.debug("Trying to edit previous message")
            chat_data["sent"] = bot.edit_message_text(
                text=message_text,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                reply_markup=reply_markup,
                parse_mode=telegram.ParseMode.MARKDOWN,
            )
            return chat_data["sent"]
        except BadRequest as e:
            logger.debug(f"Failed to edit. Error: {e}")

        logger.debug("Deleting previous message")
        bot.delete_message(
            chat_id=query.message.chat_id, message_id=query.message.message_id
        )

        logger.debug("Sending message (query found)")
        chat_data["sent"] = bot.send_message(
            text=message_text,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=reply_markup,
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
        logger.debug("Message sent. Returning.")
        return chat_data["sent"]

    logger.debug("Replace previous is False")
    try:
        logger.debug("Sending message (query found, no replace)")
        chat_data["sent"] = bot.send_message(
            text=message_text,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=reply_markup,
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
        logger.debug(f"Message sent, returning")
        return chat_data["sent"]
    except BadRequest as e:
        logger.error(f"Failed to send message: {e}")
        raise


def buttons_from_config(inline_dict, current_func, override_main_buttons=None):
    header_buttons, footer_buttons = None, None

    all_buttons = {
        k: v
        for k, v in inline_dict.items()
        if current_func in v["step"] or "all" in v["step"]
    }

    if not override_main_buttons:
        main_buttons = {
            k: v["text"] for k, v in all_buttons.items() if v["type"] == "main_buttons"
        }
    else:
        main_buttons = override_main_buttons
    footer_buttons = {
        k: v["text"] for k, v in all_buttons.items() if v["type"] == "footer_buttons"
    }
    header_buttons = {
        k: v["text"] for k, v in all_buttons.items() if v["type"] == "header_buttons"
    }

    return Buttons(
        main_buttons=main_buttons,
        header_buttons=header_buttons,
        footer_buttons=footer_buttons,
    )


def make_buttons_dict(
    list_of_models: Iterable,
    page_length: int,
    attribute_for_text: str,
    attribute_for_destination: str,
    destination_prefix: str,
) -> dict:
    """
    Takes list of models and returns a dictionary for building inline navigation.

    First sorts the list according to the __lt__ method of the class. After that splits it
    into pages of 10 items each, and returns a dictionary:

    {
    'total_pages': n,
    'pages':
        {
        1:
            {
            prefix_destination1: text1,
            prefix_destination2: text2
            ...
            }
        2:
            {
            prefix_destination11: text11
            prefix_destination12: text12
            ...
            }
        ...
        }
    }

    Prefix is the content of destination_prefix argument, used for identification with .startswith()
    in the callback handler of conversation. E.g. if choosing instructor you can use 'inst' prefix and
    uid destination attribute. This will generate destination 'inst_uid'

    :param list_of_models: An iterable of models (e.g. UserModel)
    :param page_length: Desired number of items per page
    :param attribute_for_text: Name of the class attribute to be used as button text,
    e.g. full_name
    :param attribute_for_destination: Name of the class attribute to be used as destination,
    e.g. uid
    :return: dict
    """
    if not isinstance(list_of_models, Iterable):
        raise ValueError(f"list_of_models must be iterable, not {type(list_of_models)}")

    if not isinstance(page_length, int):
        raise ValueError(f"page_length must be int, not {type(page_length)}")

    if not isinstance(attribute_for_text, str) or not isinstance(
        attribute_for_destination, str
    ):
        raise ValueError(
            f"attribute_for_text and attribute_for_destination must both be str"
        )

    if not isinstance(destination_prefix, str):
        raise ValueError(
            f"destination_prefix must be str, not {type(destination_prefix)}"
        )

    try:
        check = eval(f"list_of_models[0].{attribute_for_text}")
    except AttributeError:
        raise RuntimeError(f"{attribute_for_text} not found")
    else:
        if not check:
            raise RuntimeError(f"{attribute_for_text} not found")

    try:
        check = eval(f"list_of_models[0].{attribute_for_destination}")
    except AttributeError:
        raise RuntimeError(f"{attribute_for_destination} not found")
    else:
        if not check:
            raise RuntimeError(f"{attribute_for_destination} not found")

    # Sort the list
    try:
        list_of_models.sort()
    except AttributeError as e:
        raise RuntimeError(f"Failed to sort list_of_models: {e}")
    else:
        list_of_models = tuple(list_of_models)

    # Calculate number of pages
    total_pages = ceil(len(list_of_models) / page_length)
    if len(list_of_models) / total_pages > page_length:
        total_pages += 1

    pages = {}
    for page_number in range(1, total_pages + 1):
        pages[page_number] = {
            f"{destination_prefix}_"
            + eval(f"str(model.{attribute_for_destination})"): eval(
                f"model.{attribute_for_text}"
            )
            for model in list_of_models[
                page_number * page_length - page_length : page_number * page_length
            ]
        }

    return {"total_pages": total_pages, "pages": pages}


def command_menu_from_config(user, config_file: str, menu_type: str, group=None):
    import datetime  # Used during evals, do not remove

    logger.debug("Constructing command menu")
    options = open_yml(config_file)[menu_type]
    logger.debug(f"Loading config from {config_file}")
    menu_template = "\n{header}\n\n{selection}"
    selection = ""
    for k, v in options["options"].items():
        logger.debug(f'Evaluating condition: {v["condition"]}')
        eval_result = eval(v["condition"])
        logger.debug(f"Evaluation result: {eval_result}")
        if eval_result:
            selection += f"{v['text']}\n{v['command']}\n\n"
    logger.debug("Command menu ready")
    return menu_template.format(
        header=options["header"], selection=selection.format(user=user, group=group)
    )


def send_video_from_s3(
    bot, telegram_id, url, caption=None, parse_mode=telegram.ParseMode.MARKDOWN
):
    logger.info("Sending video from S3")
    try:
        bot.send_video(
            telegram_id,
            video=url,
            caption=caption,
            supports_streaming=False,
            parse_mode=parse_mode,
        )
    except TimedOut:
        logger.error("Timed out on send video from S3")
        alert_admin(bot, "Timed out on send photo from S3")
        send_message(bot, telegram_id, ui_msg.general["TIMED_OUT_FILE"].format(url=url))
        raise


def send_photo_from_s3(
    bot, telegram_id, url, caption=None, parse_mode=telegram.ParseMode.MARKDOWN
):
    logger.info("Sending photo from S3")
    try:
        bot.send_photo(telegram_id, photo=url, caption=caption, parse_mode=parse_mode)
    except TimedOut:
        logger.error("Timed out on send photo from S3")
        alert_admin(bot, "Timed out on send photo from S3")
        send_message(bot, telegram_id, ui_msg.general["TIMED_OUT_FILE"].format(url=url))
        raise
    except TelegramError as e:
        logger.error(f"{e}")
        from . import gu

        file = gu.download_file_from_url(url)
        logger.info("Sending downloaded file")
        bot.send_photo(
            telegram_id, open(file, "rb"), caption=caption, parse_mode=parse_mode
        )
        os.remove(file)


def send_photo(
    bot, telegram_id, filename, caption=None, parse_mode=telegram.ParseMode.MARKDOWN
):
    logger.info("Sending photo.")
    with open(filename, "rb") as f:
        return bot.send_photo(telegram_id, f, caption=caption, parse_mode=parse_mode)
