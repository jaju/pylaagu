import os
import sys

DEBUG = os.environ.get("DEBUG", False)


def to_snake(sym: str) -> str:
    return sym.replace("-", "_")


def to_kebab(sym: str) -> str:
    return sym.replace("_", "-")


def debug(*args):
    if DEBUG:
        print(*args, file=sys.stderr)


def is_public(sym: str) -> bool:
    return not sym.startswith("_")
