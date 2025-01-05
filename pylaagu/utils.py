import os
import sys

def to_snake(sym: str) -> str:
    return sym.replace("-", "_")


def to_kebab(sym: str) -> str:
    return sym.replace("_", "-")


def traverse_decode(v):
    if type(v) == dict:
        return filter_non_none(v)
    elif type(v) == list:
        return [traverse_decode(item) for item in v if item is not None]
    else:
        return v


def filter_non_none(m):
    return {k: traverse_decode(v) for k, v in m.items() if v is not None}


def filter_non_none_kwargs(**kwargs):
    return {k: traverse_decode(v) for k, v in kwargs.items() if v is not None}


DEBUG = os.environ.get("DEBUG", False)
def debug(*args):
    if DEBUG:
        print(*args, file=sys.stderr)


def is_public(sym: str) -> bool:
    return not sym.startswith("_")
