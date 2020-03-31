from config import Config as con
from utils import download_course, download_track, get_completed_tracks, get_completed_courses
import colorama
import sys
from helper import bcolors
import threading
import time


def main(argv):
    if not con.active:
        if argv[0] == 'settoken':
            print_dash()
            con.settoken(argv[1])
        else:
            return
    print_dash()
    print_desc()
    while True:
        print_dash()
        s = input('>> ')
        if s == 'list':
            thread = threading.Thread(target=print_tracks)
            thread.start()
            if print_waiting(thread):
                if len(get_completed_tracks()) == 0:
                    continue
                (s, v) = wait_download()
                if s is not None:
                    path, nums = split_download_command(s)
                    for i in nums:
                        track = list(filter(lambda x: x.id == int(i),
                                            get_completed_tracks()))[0]
                        download_track(track, path, v)
        elif s == 'listc':
            thread = threading.Thread(target=print_courses)
            thread.start()
            if print_waiting(thread):
                if len(get_completed_courses()) == 0:
                    continue
                (s, v) = wait_download()
                if s is not None:
                    path, nums = split_download_command(s)
                    for i in nums:
                        track = list(filter(lambda x: x.id == int(i),
                                            get_completed_courses()))[0]
                        download_course(track.link, path, v)


def wait_download():
    while True:
        s = input('>>> ')
        if s.split()[0] == 'download':
            return s, False  # False for don't download videos
        elif s.split()[0] == 'downloadv':
            return s, True  # Download videos
        elif s == 'back':
            return None, False


def print_waiting(thread):
    i = 1
    while thread.isAlive():
        print('Waiting %s%s' % ('.' * i, ' ' * (3 - i)), end='\r')
        i = i + 1 if i < 3 else 1
        time.sleep(0.4)
    print('', end='\r')
    return True


def split_download_command(text):
    if "'" in text:
        path = text.split("'")
        if '-' in path[2]:
            nums = list(range(
                int(path[2].split('-')[0]),
                int(path[2].split('-')[1]) + 1))
        else:
            nums = path[2].split()
        return path[1], nums
    else:
        path = text.split()
        if '-' in path[2]:
            nums = list(range(
                int(path[2].split('-')[0]),
                int(path[2].split('-')[1]) + 1))
        else:
            nums = path[2:]
        return path[1], nums


def print_courses():
    courses = get_completed_courses()
    if len(courses) == 0:
        sys.stdout.write(
            f'{bcolors.FAIL} No courses found!  {bcolors.BKENDC}\n')
    for course in courses:
        sys.stdout.write(
            f'{bcolors.BKGREEN} {course.id}. {course.name}  {bcolors.BKENDC}\n')


def print_tracks():
    tracks = get_completed_tracks()
    if len(tracks) == 0:
        sys.stdout.write(
            f'{bcolors.FAIL} No tracks found!  {bcolors.BKENDC}\n')

    for track in tracks:
        sys.stdout.write(
            f'{bcolors.BKBLUE} {track.id}. {track.name}  {bcolors.BKENDC}\n')


def print_desc():
    desc = 'Use the following commands in order.\n' +\
           f'1. {bcolors.BKBLUE}list{bcolors.BKENDC}     : to print your completed tracks.\n' +\
           f'   or {bcolors.BKBLUE}listc{bcolors.BKENDC} : to print your completed courses.\n' +\
           f'2. {bcolors.BKBLUE}download{bcolors.BKENDC} followed by the destination and the id(s) of the ' +\
           f'track(s)/course(s).\n\tThis command downloads {bcolors.OKBLUE}slides{bcolors.ENDC} only.\n' +\
           f'   or {bcolors.BKBLUE}downloadv{bcolors.BKENDC} followed by the destination and the id(s) of the ' +\
           f'track(s)/course(s).\n\tThis command downloads both {bcolors.OKBLUE}slides and videos{bcolors.ENDC}.\n' +\
           f'{bcolors.OKGREEN}Note: you can type 1-13 in the download command to download courses from 1 to 13.{bcolors.ENDC}\n' +\
           '=' * 100 + '\n' + \
           f'{bcolors.BKGREEN} Example {bcolors.BKENDC}\n' + \
           '>> listc\n 1. Introduction to Databases in Python' + \
           '\n 2. Building Chatbots in Python \n' + \
           ">>> downloadv 'C:/' 2"
    print(desc)


def print_dash():
    print('=' * 100, end='\n')


colorama.init()
if __name__ == "__main__":
    # print(sys.argv)
    main(sys.argv[1:])
