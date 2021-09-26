from enum import Enum, unique
from typing import Any, Dict

__all__ = [
    'alert',
    'biginform',
    'indicate',
    'inform',
    'warn',
]

@unique
class Color(Enum):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def cprint(txt: str, format=Color, *, print_arg: Dict[str, Any] = {}):
    print(f'{format.value}{txt}{Color.ENDC.value}', **print_arg)


class inform():
    def __init__(self, txt: str, prefix:str ='# ', suffix:str = ''):
        self.txt = txt
        self.prefix = prefix
        self.suffix = suffix
        cprint(f'{self.prefix}{self.txt}{self.suffix}', Color.OKCYAN)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa
        if exc_value is None:
            cprint(f'{" " * len(self.prefix)}Done', Color.OKBLUE)


class indicate():
    def __init__(self, txt: str, prefix:str ='  ', suffix:str = ''):
        self.txt = txt
        self.prefix = prefix
        self.suffix = suffix
        for t in txt.rstrip().split('\n'):
            cprint(f'{self.prefix}{t}{self.suffix}', Color.OKGREEN)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa
        pass
        # cprint(f'', Color.OKGREEN)


class biginform():
    def __init__(self, txt: str, prefix:str ='########## ', suffix:str = ' ##########'):
        self.txt = txt
        self.prefix = prefix
        self.suffix = suffix
        print()
        cprint(f'{self.prefix}{self.txt}{self.suffix}', Color.HEADER)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa
        if exc_value is None:
            cprint(f'{self.prefix}DONE::{self.txt}{self.suffix}', Color.HEADER)


class alert():
    def __init__(self, txt: str, prefix:str ='$$$$$$$$$$ ', suffix:str = ' $$$$$$$$$$'):
        self.txt = txt
        self.prefix = prefix
        self.suffix = suffix
        cprint(f'{self.prefix}{self.txt}{self.suffix}', Color.FAIL)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa
        if exc_value is None:
            cprint(f'{self.prefix}End Of Message{self.suffix}', Color.OKBLUE)


class warn():
    def __init__(self, txt: str, prefix:str ='$ ', suffix:str = ''):
        self.txt = txt
        self.prefix = prefix
        self.suffix = suffix
        cprint(f'{self.prefix}{self.txt}{self.suffix}', Color.WARNING)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa
        pass
        # cprint(f'', Color.WARNING)

