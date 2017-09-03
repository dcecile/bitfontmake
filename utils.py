from contextlib import contextmanager
from itertools import takewhile, chain
from tempfile import TemporaryDirectory
import os

@contextmanager
def change_cwd(path):
    original_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original_cwd)

@contextmanager
def temporary_cwd():
    with TemporaryDirectory() as path:
        with change_cwd(path):
            yield

def count_while(test, iterable):
    return len(list(takewhile(test, iterable)))

def flatten(list_of_lists):
    return list(chain.from_iterable(list_of_lists))

def distinct_by(selector, iterable):
    keys = set()
    for value in iterable:
        key = selector(value)
        if key not in keys:
            keys.add(key)
            yield value
