#!/usr/bin/env python
from loguru import logger
from redis import Redis
from telegram.ext import BasePersistence

from collections import defaultdict
import redis

try:
    import dill

    logger.info("Using dill as pickling engine")
    pickling_engine = dill
except ModuleNotFoundError:
    import pickle

    logger.info("Dill not installed. Using pickle as pickling engine.")
    pickling_engine = pickle


class RedisPersistence(BasePersistence):
    def __init__(
        self,
        redis_connection_dict=None,
        redis_connection_uri=None,
        *,
        redis_key,
        store_user_data=True,
        store_chat_data=True,
        singe_file=True,
        on_flush=False,
        redis_instance: Redis = None,
    ):
        """

        :param redis_connection_dict: A dictionary with 'redis_host', 'redis_port' and 'redis_pwd' keys.
        :param redis_key:
        :param store_user_data:
        :param store_chat_data:
        :param singe_file:
        :param on_flush:
        """
        self.redis_key = redis_key
        self.store_user_data = store_user_data
        self.store_chat_data = store_chat_data
        self.single_file = singe_file
        self.on_flush = on_flush
        self.user_data = None
        self.chat_data = None
        self.conversations = None

        if redis_instance:
            self.redis_client = redis_instance
        elif redis_connection_dict:
            self.redis_client = redis.Redis(
                host=redis_connection_dict["redis_host"],
                port=redis_connection_dict["redis_port"],
                password=redis_connection_dict["redis_pwd"],
            )
        elif redis_connection_uri:
            self.redis_client = redis.from_url(redis_connection_uri)
        else:
            raise ValueError("no redis connection data provided")

    def load_singlefile(self):
        try:
            loaded_value = self.redis_get_value(self.redis_key)
            if loaded_value:
                all = loaded_value
                self.user_data = defaultdict(dict, all["user_data"])
                self.chat_data = defaultdict(dict, all["chat_data"])
                self.conversations = all["conversations"]
            else:
                raise IOError("No record found")
        except IOError:
            self.conversations = {}
            self.user_data = defaultdict(dict)
            self.chat_data = defaultdict(dict)
        except dill.UnpicklingError:
            raise TypeError(
                f"Redis record {self.redis_key} does not contain valid pickle data"
            )
        except Exception as e:
            raise RuntimeError(
                f"Something went wrong unpickling {self.redis_key}.\n{e}"
            )

    def load_file(self, redis_key):
        try:
            return self.redis_get_value(redis_key)
        except IOError:
            return None
        except dill.UnpicklingError:
            raise TypeError(
                "File {} does not contain valid pickle data".format(redis_key)
            )
        except Exception:
            raise TypeError("Something went wrong unpickling {}".format(redis_key))

    def dump_singlefile(self):
        all = {
            "conversations": self.conversations,
            "user_data": self.user_data,
            "chat_data": self.chat_data,
        }
        return self.redis_set_value(self.redis_key, all)

    def dump_file(self, redis_key, data):
        self.redis_set_value(redis_key, data)

    def get_user_data(self):
        """Returns the user_data from the pickle file if it exsists or an empty defaultdict.
        Returns:
            :obj:`defaultdict`: The restored user data.
        """
        if self.user_data:
            pass
        elif not self.single_file:
            redis_key = f"{self.redis_key}_user_data"
            data = self.load_file(redis_key)
            if not data:
                data = defaultdict(dict)
            else:
                data = defaultdict(dict, data)
            self.user_data = data
        else:
            self.load_singlefile()
        return self.user_data.copy()

    def get_chat_data(self):
        """Returns the chat_data from the pickle file if it exsists or an empty defaultdict.
        Returns:
            :obj:`defaultdict`: The restored chat data.
        """
        if self.chat_data:
            pass
        elif not self.single_file:
            redis_key = f"{self.redis_key}_chat_data"
            data = self.load_file(redis_key)
            if not data:
                data = defaultdict(dict)
            else:
                data = defaultdict(dict, data)
            self.chat_data = data
        else:
            self.load_singlefile()
        return self.chat_data.copy()

    def get_conversations(self, name):
        """Returns the conversations from the pickle file if it exsists or an empty defaultdict.
        Args:
            name (:obj:`str`): The handlers name.
        Returns:
            :obj:`dict`: The restored conversations for the handler.
        """
        if self.conversations:
            pass
        elif not self.single_file:
            redis_key = f"{self.redis_key}_conversations"
            data = self.load_file(redis_key)
            if not data:
                data = {name: {}}
            self.conversations = data
        else:
            self.load_singlefile()
        return self.conversations.get(name, {}).copy()

    def update_conversation(self, name, key, new_state):
        """Will update the conversations for the given handler and depending on :attr:`on_flush`
        save the pickle file.
        Args:
            name (:obj:`str`): The handlers name.
            key (:obj:`tuple`): The key the state is changed for.
            new_state (:obj:`tuple` | :obj:`any`): The new state for the given key.
        """
        if self.conversations.setdefault(name, {}).get(key) == new_state:
            return
        self.conversations[name][key] = new_state
        if not self.on_flush:
            if not self.single_file:
                redis_key = "{}_conversations".format(self.redis_key)
                self.dump_file(redis_key, self.conversations)
            else:
                self.dump_singlefile()

    def update_user_data(self, user_id, data):
        """Will update the user_data (if changed) and depending on :attr:`on_flush` save the
        pickle file.
        Args:
            user_id (:obj:`int`): The user the data might have been changed for.
            data (:obj:`dict`): The :attr:`telegram.ext.dispatcher.user_data`[user_id].
        """
        if self.user_data.get(user_id) == data:
            return
        self.user_data[user_id] = data
        if not self.on_flush:
            if not self.single_file:
                redis_key = "{}_user_data".format(self.redis_key)
                self.dump_file(redis_key, self.user_data)
            else:
                self.dump_singlefile()

    def update_chat_data(self, chat_id, data):
        """Will update the chat_data (if changed) and depending on :attr:`on_flush` save the
        pickle file.
        Args:
            chat_id (:obj:`int`): The chat the data might have been changed for.
            data (:obj:`dict`): The :attr:`telegram.ext.dispatcher.chat_data`[chat_id].
        """
        if self.chat_data.get(chat_id) == data:
            return
        self.chat_data[chat_id] = data
        if not self.on_flush:
            if not self.single_file:
                redis_key = "{}_chat_data".format(self.redis_key)
                self.dump_file(redis_key, self.chat_data)
            else:
                self.dump_singlefile()

    def flush(self):
        """If :attr:`on_flush` is set to ``True``. Will save all data in memory to pickle file(s). If
        it's ``False`` will just pass.
        """
        if not self.on_flush:
            pass
        else:
            if self.single_file:
                self.dump_singlefile()
            else:
                self.dump_file("{}_user_data".format(self.redis_key), self.user_data)
                self.dump_file("{}_chat_data".format(self.redis_key), self.chat_data)
                self.dump_file(
                    "{}_conversations".format(self.redis_key), self.conversations
                )

    def redis_set_value(self, key, value):
        if not self.redis_client:
            raise RuntimeError(f"No redis connection")
        dumped = pickling_engine.dumps(value)
        return self.redis_client.set(key, dumped)

    def redis_get_value(self, key):
        if not self.redis_client:
            raise RuntimeError(f"No redis connection")

        pickled_value = self.redis_client.get(key)
        try:
            if pickled_value:
                return pickling_engine.loads(pickled_value)
        except TypeError as e:
            logger.error(f"Error unpickling {key}: {e}")
        except Exception as e:
            logger.error(f"Error unpickling {key}: {e}")
