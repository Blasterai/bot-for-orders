from functools import update_wrapper

from loguru import logger
from telegram import Update
from telegram.ext import CallbackContext


def command_dispatch(func):
    """
    Decorator to register commands. Similar to functools.singledispatch.

    If command contains '_' it will split it into command (before '_') and kwargs['target'] (after '_').
    To be used as prefix for generated commands e.g. /reg_ads324asdf3242

    Will put all args (/command arg1 arg2) into kwargs['args']

    :param func:
    :return:
    """
    registry = {}

    def unregistered_command(update: Update, context: CallbackContext, **kwargs):
        return

    def dispatch(command):
        nonlocal registry

        real_command = command.split("_")[0]

        try:
            impl = registry[real_command]
        except KeyError:
            logger.warning(f"Unregistered command: {command}")
            return unregistered_command

        return impl

    def save_to_registry(command, func):
        real_command = command.split("_")[0]

        if real_command in registry.keys():
            raise KeyError(
                f"Duplicate command {command} in {func.__module__}.{func.__name__}. "
                f"Command already registered in {registry[command].__module__}.{registry[command].__name__}"
            )
        registry[real_command] = func

    def register(command, func=None):
        nonlocal registry

        if func is None:
            return lambda c: register(command, c)

        if isinstance(command, list):
            for subcommand in command:
                save_to_registry(subcommand, func)
        elif isinstance(command, str):
            save_to_registry(command, func)
        else:
            raise ValueError(
                f"command must be str, or list of str, not {type(command)}"
            )

        return func

    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        text = update.message.text
        if len(text.split()) == 1:
            command = text
        else:
            command = text.split()[0]
            kwargs["args"] = text.split()[1:]

        if "_" in command:
            kwargs["target"] = text.split("_")[1]

        logger.info(
            f"Command: {command} from {update.effective_user.full_name} ({update.effective_user.id})"
        )

        return dispatch(command)(update, context, *args, **kwargs)

    registry[object] = func
    wrapper.register = register
    wrapper.dispatch = dispatch
    wrapper.registry = registry
    update_wrapper(wrapper, func)

    return wrapper
