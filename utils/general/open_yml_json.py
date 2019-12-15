from collections import abc, UserDict
from functools import lru_cache
from keyword import iskeyword

import json
from ruamel import yaml


@lru_cache(maxsize=32)
def open_yml(filename, as_dict=False, top_key=None):
    """
    Opens a YML file and returns it's content either as dictionary or as instance of MyNamespace. Cached by
    built-in lru_cache module.
    :param filename: filename to open
    :param frozen_js: True to return MyNamespace, False to return dict
    :param top_key: if specified the returned instance will only include items from this key onwards.
    :return:
    """
    with open(filename, "r", encoding="UTF8") as f:
        if not top_key:
            yaml_file = yaml.safe_load(f)
        else:
            yaml_file = yaml.safe_load(f)[top_key]
    if as_dict:
        return yaml_file
    return MyNamespace(yaml_file)


@lru_cache(maxsize=32)
def open_json(filename, as_dict=False, top_key=None):
    """
    Opens a YML file and returns it's content either as dictionary or as instance of MyNamespace. Cached by
    built-in lru_cache module.
    :param filename: filename to open
    :param frozen_js: True to return MyNamespace, False to return dict
    :param top_key: if specified the returned instance will only include items from this key onwards.
    :return:
    """
    with open(filename, "r", encoding="UTF-8") as f:
        if not top_key:
            dic = json.load(f)
        else:
            dic = json.load(f)[top_key]
    if as_dict:
        return dic
    return MyNamespace(dic)


class MyNamespace(UserDict):
    def __init__(self, mapping):
        self.__keys = set()
        for key, value in mapping.items():
            if iskeyword(key):
                key += "_"
            setattr(self, key, self.build(value))
            self.__keys.add(key)

    @classmethod
    def build(cls, value):
        if isinstance(value, abc.Mapping):
            return cls(value)
        elif isinstance(value, abc.MutableSequence):
            return [cls.build(item) for item in value]
        else:
            return value

    def keys(self):
        return list(self.__keys)

    def values(self):
        return [getattr(self, key) for key in self.__keys]

    def items(self):
        return [(key, getattr(self, key)) for key in self.__keys]

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        raise AttributeError(f"{item}")

    def __repr__(self):
        copy = self.__dict__.copy()
        del copy["_MyNamespace__keys"]
        return f"MyNamespace({copy})"

    def __delitem__(self, key):
        raise TypeError("MyNamespace object does not support item assignment")

    def __setitem__(self, key, value):
        raise TypeError("MyNamespace object does not support item assignment")

    def __len__(self):
        return len(self.__keys)

    def __iter__(self):
        for i in self.__keys:
            yield i
