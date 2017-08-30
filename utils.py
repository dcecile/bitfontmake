from tempfile import TemporaryDirectory
from pathlib import Path
from itertools import takewhile

class TemporaryWorkingDirectory():
    def __init__(self):
        self.temporaryDirectory = None
        self.path = None

    def __enter__(self):
        self.temporaryDirectory = TemporaryDirectory()
        self.path = Path(
            self.temporaryDirectory.__enter__())
        self.path.__enter__()

    def __exit__(self, *args):
        self.temporaryDirectory.__exit__(*args)
        self.temporaryDirectory = None
        self.path.__exit__(*args)
        self.path = None

def count_while(test, iterable):
    return len(list(takewhile(test, iterable)))
