import re

try:
    from telegram.ext import BaseFilter

    class RegexAnywhereFilter(BaseFilter):
        pattern = None

        def __init__(self, pattern):
            self.pattern = pattern

        def filter(self, message):
            return bool(re.findall(self.pattern, message.text))


except ModuleNotFoundError:
    pass
