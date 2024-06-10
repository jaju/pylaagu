import os
import jsonpickle
import sqlite3
from platformdirs import user_cache_dir


__appname = None
__cachedir = None
__conn = None
memoize_store = {}


def cache_get(key):
    cursor = __conn.cursor()
    cursor.execute("SELECT value FROM cache WHERE key=?", (key,))
    row = cursor.fetchone()
    if row:
        return jsonpickle.decode(row[0])
    return None


def cache_set(key, value):
    cursor = __conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO cache (key, value) VALUES (?, ?)",
                   (key, jsonpickle.encode(value)))
    __conn.commit()


# Thanks to https://stackoverflow.com/a/815160/1330548
# for the decorator idea

def init_app(name):
    global __appname
    global __cachedir
    global __conn
    __appname = name
    __cachedir = user_cache_dir(name)
    if not os.path.exists(__cachedir):
        os.makedirs(__cachedir)
    __conn = sqlite3.connect(__cachedir + '/cache.db')
    __conn.cursor().execute("CREATE TABLE IF NOT EXISTS cache"
                            " (key TEXT PRIMARY KEY, value TEXT)")


def appname():
    if not __appname:
        raise ValueError("Appname not set")
    return __appname


def diskcache(f):
    def wrapper(*args, **kwargs):
        key = jsonpickle.encode(args, kwargs)
        value = cache_get(key)
        if value is None:
            value = f(*args)
            cache_set(key, value)
        return value
    return wrapper
