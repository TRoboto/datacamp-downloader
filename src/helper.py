import os
import sys
import time
import string


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BKBLUE = '\x1b[7;37;44m'
    BKGREEN = '\x1b[7;37;42m'
    BKENDC = '\x1b[0m'


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
    with open(location, 'wb') as f:
        total_length = response.headers.get('content-length')
        if total_length is None:  # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=1024 * 1024):  # 1MB
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("'{}{}{}' {}[%s%s] %d%% {}\r"
                                 .format(bcolors.OKBLUE, os.path.basename(location),
                                         bcolors.ENDC, bcolors.WARNING, bcolors.ENDC) % ('=' * done,
                                                                                         ' ' * (50 - done), done * 2))
                #  dl//(time.clock() - start) / 800000))
                sys.stdout.flush()
    sys.stdout.write('\n')


def file_exist(file):
    return os.path.isfile(file)


def format_filename(name):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in name if c in valid_chars)
    return filename


def mkdir(location):
    if not os.path.isdir(os.path.dirname(location)):
        if '/' in location or '\\' in location:
            os.makedirs(os.path.dirname(location))
        else:
            os.mkdir(location)


def embbed_link(link):
    if '?' in link:
        link += '&embedded=true'
    else:
        link += '?embedded=true'
    return link


def handle_error(con):
    print(bcolors.FAIL + "Error occured, trying again...")
    con.set_new_session()
    time.sleep(5)
