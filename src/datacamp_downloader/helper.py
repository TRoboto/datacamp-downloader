import os
from pathlib import Path
import string
import sys
import time
import threading
import itertools

from texttable import Texttable
from termcolor import colored


class Logger:
    @staticmethod
    def error(text):
        Logger.print(text, "ERROR:", "red")

    @staticmethod
    def clear():
        sys.stdout.write("\r" + " " * 100 + "\r")

    @staticmethod
    def warning(text):
        Logger.print(text, "WARNING:", "yellow")

    @staticmethod
    def info(text):
        Logger.print(text, "INFO:", "green")

    @staticmethod
    def print(text, head, color=None, background=None, end="\n"):
        Logger.clear()
        print(colored(f"{head}", color, background), text, end=end)

    @staticmethod
    def print_table(rows):
        Logger.clear()
        table = Texttable()
        table.set_max_width(100)
        table.add_rows(rows)
        print(table.draw())


def animate_wait(f):
    done = False

    def animate():
        for c in itertools.cycle(list("/—\|")):
            if done:
                sys.stdout.write("\r")
                break
            sys.stdout.write("\rPlease wait " + c)
            time.sleep(0.1)
            sys.stdout.flush()

    def wrapper(*args):
        nonlocal done
        done = False
        t = threading.Thread(target=animate)
        t.start()
        output = f(*args)
        done = True
        return output

    return wrapper


def download_file(session, link: str, path: Path):
    # start = time.clock()
    while True:
        try:
            response = session.get(link, stream=True)
            break
        except Exception as e:
            Logger.warning("Cannot download: " + link)
            return

    if not path.is_file():
        path = path / link.split("/")[-1]
    if path.exists():
        Logger.warning(f"{path.absolute()} has already been downloaded")
        return

    path.parent.mkdir(exist_ok=True, parents=True)
    total_length = response.headers.get("content-length")

    with path.open("wb") as f:
        if total_length is None:  # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=1024 * 1024):  # 1MB
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                Logger.print(
                    "[%s%s] %d%%" % ("=" * done, " " * (50 - done), done * 2),
                    f"Downloading [{path.name}]",
                    "blue",
                    end="\r",
                )
                sys.stdout.flush()
    sys.stdout.write("\n")


def format_filename(name):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = "".join(c for c in name if c in valid_chars)
    return filename
