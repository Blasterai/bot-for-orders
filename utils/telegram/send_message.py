import time

try:
    # pip install python-telegram-bot
    import telegram
    from telegram import MAX_MESSAGE_LENGTH, TelegramError
    from telegram.error import BadRequest, NetworkError
except ModuleNotFoundError:
    pass


def send_message(
    bot,
    user_id,
    response,
    parse_mode="MARKDOWN",
    reply_markup=None,
    disable_web_page_preview=True,
):
    """
    Sends message to user_id.

    Splits message into shorter messages of MAX_MESSAGE_LENGTH (set by Telegram). If message is shorter, splits into
    list of 1 item. Send messages from list. Handles all kinds of possible errors while sending and tries to deliver
    anyway. Doesn't guarantee delivery.

    :param bot:
    :param user_id:
    :param response:
    :param parse_mode:
    :param reply_markup:
    :param disable_web_page_preview:
    :return: sent object of the last message sent
    """

    split_message = _split_message_by_telegram_requirements(response)
    return _send_split_message(
        bot,
        user_id,
        split_message,
        parse_mode=parse_mode,
        reply_markup=reply_markup,
        disable_web_page_preview=disable_web_page_preview,
    )


def _send_single_message(
    bot,
    telegram_id,
    message,
    parse_mode="MARKDOWN",
    reply_markup=None,
    disable_web_page_preview=True,
):
    sent = None
    try:
        sent = bot.send_message(
            chat_id=telegram_id,
            text=message,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview,
        )
    except BadRequest as e:
        logger.error(f"{e}: {telegram_id}")
    except NetworkError:
        logger.error(NetworkError)
    except TelegramError as e:
        error_msg = f"TelegramError while sending message: {e}"
        logger.error(error_msg)
        sent = bot.send_message(
            chat_id=telegram_id,
            text=message.replace("\\", ""),
            parse_mode=None,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview,
        )
    except UnicodeEncodeError as e:
        logger.warning(f"send_message: {e}")

    return sent


def _split_message_by_telegram_requirements(message):
    chunks, chunk_size = len(message), MAX_MESSAGE_LENGTH
    split_message = [message[i : i + chunk_size] for i in range(0, chunks, chunk_size)]
    return split_message


def _send_split_message(
    bot,
    telegram_id,
    split_message,
    parse_mode=None,
    reply_markup=None,
    disable_web_page_preview=None,
):
    for i in range(len(split_message)):
        if i < (len(split_message) - 1):
            _send_single_message(
                bot,
                telegram_id,
                split_message[i],
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                disable_web_page_preview=disable_web_page_preview,
            )
            time.sleep(1)
        else:
            return _send_single_message(
                bot,
                telegram_id,
                split_message[i],
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                disable_web_page_preview=disable_web_page_preview,
            )
