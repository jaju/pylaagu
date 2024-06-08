import os
import sys

DEBUG = os.environ.get("DEBUG", False)


def debug(*args):
    if DEBUG:
        print(*args, file=sys.stderr)


def is_public(name: str) -> bool:
    return not name.startswith("_")
