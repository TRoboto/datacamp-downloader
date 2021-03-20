from pathlib import Path
import sys
import time
import threading
import itertools
import re

from texttable import Texttable
from termcolor import colored


class Logger:
    show_warnings = True

    @classmethod
    def error(cls, text):
        Logger.print(text, "ERROR:", "red")

    @classmethod
    def clear(cls):
        sys.stdout.write("\r" + " " * 100 + "\r")

    @classmethod
    def warning(cls, text):
        if cls.show_warnings:
            Logger.print(text, "WARNING:", "yellow")

    @classmethod
    def info(cls, text):
        Logger.print(text, "INFO:", "green")

    @classmethod
    def print(cls, text, head, color=None, background=None, end="\n"):
        Logger.clear()
        print(colored(f"{head}", color, background), text, end=end)

    @classmethod
    def print_table(cls, rows):
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


def correct_path(path: str):
    return re.sub("[^-a-zA-Z0-9_.() /]+", "", path)


def download_file(
    session, link: str, path: Path, progress=True, max_retry=10, overwrite=False
):
    # start = time.clock()
    if not overwrite and path.exists():
        Logger.warning(f"{path.absolute()} is already downloaded")
        return

    for i in range(max_retry):
        try:
            response = session.get(link, stream=True)
            i = -1
            break
        except Exception:
            Logger.print(f"", f"Retry [{i+1}/{max_retry}]", "magenta", end="")

    if i != -1:
        Logger.error(f"Failed to download {link}")
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
                if progress:
                    print_progress(dl, total_length, path.name)
    if progress:
        sys.stdout.write("\n")


def print_progress(progress, total, name, max=50):
    done = int(max * progress / total)
    Logger.print(
        "[%s%s] %d%%" % ("=" * done, " " * (max - done), done * 2),
        f"Downloading [{name}]",
        "blue",
        end="\r",
    )
    sys.stdout.flush()


def save_text(path: Path, content: str, overwrite=False):
    if not path.is_file:
        Logger.error(f"{path.absolute()} isn't a file")
        return
    if not overwrite and path.exists():
        Logger.warning(f"{path.absolute()} is already downloaded")
        return
    path.parent.mkdir(exist_ok=True, parents=True)
    path.write_text(content, encoding="utf8")
    # Logger.info(f"{path.name} has been saved.")


def fix_track_link(link):
    if "?" in link:
        link += "&embedded=true"
    else:
        link += "?embedded=true"
    return link