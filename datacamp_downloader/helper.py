import os
import string
import sys
import time
import inspect
import threading
import itertools

from termcolor import colored


class Logger:
    @staticmethod
    def error(text):
        Logger.clear()
        print(colored("\rERROR:", "red"), text)

    @staticmethod
    def clear():
        sys.stdout.write("\r" + " " * 100)

    @staticmethod
    def warning(text):
        Logger.clear()
        print(colored("\rWARNING:", "yellow"), text)

    @staticmethod
    def info(text):
        Logger.clear()
        print(colored("\rINFO:", "green"), text)


def animate_wait(f):
    done = False

    def animate():
        for c in itertools.cycle(list("/—\|")):
            if done:
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


def download_file(con, video_link, location):
    # start = time.clock()
    while True:
        try:
            response = con.session.get(video_link, stream=True)
            break
        except:
            handle_error(con)
    mkdir(location)
    if file_exist(location):
        return
    with open(location, "wb") as f:
        total_length = response.headers.get("content-length")
        if total_length is None:  # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=1024 * 1024):  # 1MB
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write(
                    "'{}{}{}' {}[%s%s] %d%% {}\r".format(
                        bcolors.OKBLUE,
                        os.path.basename(location),
                        bcolors.ENDC,
                        bcolors.WARNING,
                        bcolors.ENDC,
                    )
                    % ("=" * done, " " * (50 - done), done * 2)
                )
                #  dl//(time.clock() - start) / 800000))
                sys.stdout.flush()
    sys.stdout.write("\n")


def save_file(filename, content):
    mkdir(filename)
    f = open(filename, "w", encoding="utf-8")
    f.write(content)
    f.close()


def file_exist(file):
    return os.path.isfile(file)


def format_filename(name):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = "".join(c for c in name if c in valid_chars)
    return filename


def mkdir(location):
    if not os.path.isdir(os.path.dirname(location)):
        if "/" in location or "\\" in location:
            os.makedirs(os.path.dirname(location))
        else:
            os.mkdir(location)


def fix_link(link):
    if "?" in link:
        link += "&embedded=true"
    else:
        link += "?embedded=true"
    return link


def handle_error(con):
    print(bcolors.FAIL + "Error occurred, trying again...")
    con.set_new_session()
    time.sleep(5)


def memoize(func):
    memo = []

    def wrapper():
        if not memo:
            value = func()
            for x in value:
                memo.append(x)
        return memo

    return wrapper
