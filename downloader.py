from config import config as con
from utils import download_course, download_track, get_completed_tracks, get_completed_courses
import colorama
import sys
from helper import bcolors
import threading
import time


def main(argv):
    if con.active == False:
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
                s = input('>> ')
                path, nums = split_download_command(s)
                for i in nums:
                    track = list(filter(lambda x: x.id == int(i), get_completed_tracks()))[0]
                    download_track(track, path)
        elif s == 'listc':
            thread = threading.Thread(target=print_courses)
            thread.start()
            if print_waiting(thread):
                s = input('>> ')
                path, nums = split_download_command(s)
                for i in nums:
                    track = list(filter(lambda x: x.id == int(i),get_completed_courses()))[0]
                    download_course(track.link, path)

def print_waiting(thread):
    i = 1
    while thread.isAlive():
        print('Waiting %s%s' % ('.' * i, ' ' * (3-i)), end='\r')
        i = i + 1 if i < 3 else 1
        time.sleep(0.3)
    return True

def split_download_command(text):
    if "'" in text:
        path = text.split("'")
        return path[1], path[2].split()
    else:
        path = text.split()
        return path[1], path[2:]
def print_courses():
    courses = get_completed_courses()
    for course in courses:
        sys.stdout.write(
            f'{bcolors.BKGREEN} {course.id}. {course.name}  {bcolors.BKENDC}\n')

def print_tracks():
    tracks = get_completed_tracks()
    for track in tracks:
        sys.stdout.write(
            f'{bcolors.BKBLUE} {track.id}. {track.name}  {bcolors.BKENDC}\n')

def print_desc():
    desc = 'Use the following commands in order.\n' +\
    f'1. {bcolors.BKBLUE}list{bcolors.BKENDC}     : to print your completed tracks\n'+\
    f'   or {bcolors.BKBLUE}listc{bcolors.BKENDC} : to print your completed courses\n'+\
    f'2. {bcolors.BKBLUE}download{bcolors.BKENDC}   followed by the destination and the id(s) of the track(s)/course(s) you want to download\n'+\
    '=' * 100 + '\n' +\
    f'{bcolors.BKGREEN}Example{bcolors.BKENDC}\n' +\
    '>> list\n 1. Python Programming Track \n'+\
    ">> download 'C:/' 1"
    print(desc)

def print_dash():
    print('=' * 100, end='\n')
colorama.init()
if __name__ == "__main__":
    # print(sys.argv)
    main(sys.argv[1:])
