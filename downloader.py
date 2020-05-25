import os
import sys
import threading
import time
from argparse import ArgumentParser

import colorama

from config import Config as con
from helper import bcolors
from utils import download_course, download_track, get_completed_tracks, get_completed_courses


def login_parser():
    parser = ArgumentParser()
    parser.add_argument("-t", "--token", required=False, type=str,
                        help="Specify your Datacamp authentication token.")
    parser.add_argument("-l", "--list", action='store_true',
                        help="List completed tracks")
    parser.add_argument("-lc", "--listc", action='store_true',
                        help="List completed courses")
    parser.add_argument("-p", "--path", required=False, default=os.getcwd(), type=str,
                        help="Path to download the contents, default is the current directory")
    parser.add_argument("-v", "--video", action='store_true',
                        help="Include it if you want to download the videos")
    parser.add_argument("-s", "--slide", action='store_true',
                        help="Include it if you want to download the slides")
    parser.add_argument("-d", "--dataset", action='store_true',
                        help="Include it if you want to download the datasets")
    parser.add_argument("-e", "--exercise", action='store_true',
                        help="Include it if you want to download the exercises")
    parser.add_argument("-a", "--all", action='store_true',
                        help="Include it if you want to download all the content")
    return parser


def is_link(l):
    return '/' in l


def get_to_download():
    #     inp = input('Enter the id(s) you want to download separated by a space or '
    #                 "you can enter 'a-b' to download courses from a to b: ")
    inp = input('Enter the id(s)/link(s) you want to download separated by a space or '
                "you can enter 'a-b' to download courses from a to b(if you have completed them): ")

    output = inp.split()
    output_links = [x for x in output if is_link(x)]
    output_numbers = [x for x in output if not is_link(x)]
    result = []
    for i in output_numbers:
        if '-' in i:
            result = i.split('-')
            result = [*range(int(result[0]), int(result[1]) + 1)]
        else:
            result.append(int(i))
    print(output_links, result)
    return (output_links, result)


def main():
    args = login_parser().parse_args()
    if os.path.exists('./token.txt'):
        with open('./token.txt', 'r') as f:
            token = f.readline()
        con.set_token(token)
    else:
        con.set_token(args.token)
        with open('./token.txt', 'w') as f:
            f.write(args.token)

    if not con.sub_active:
        return

    print_dash()

    while True:
        if args.list:
            handle_tracks(args)
        elif args.listc:
            handle_courses(args)


def handle_courses(args):
    thread = start_thread(print_courses)
    if wait(thread):
        if len(get_completed_courses()) == 0:
            exit()
        links = get_to_download()
        required_courses_by_id = links[1]
        required_courses_by_link = links[0]
        if(len(required_courses_by_id) > 0):
            for course_id in required_courses_by_id:
                course = list(filter(lambda x: x.id == course_id,
                                     get_completed_courses()))[0]
                if(args.all):
                    download_course(course.link, args.path, args.all, args.all, args.all, args.all)
                else:
                    download_course(course.link, args.path, args.video, args.slide, args.dataset, args.exercise)
        if(len(required_courses_by_link) > 0):
            for course_link in required_courses_by_link:
                if(args.all):
                    download_course(course_link, args.path, args.all, args.all, args.all, args.all)
                else:
                    download_course(course_link, args.path, args.video, args.slide, args.dataset, args.exercise)


def print_dash():
    print('=' * 100, end='\n')


def handle_tracks(args):
    thread = start_thread(print_tracks)
    if wait(thread):
        if len(get_completed_tracks()) == 0:
            exit()
        required_tracks_by_id = get_to_download()[1]
        required_tracks_by_link = get_to_download()[0]
        if(len(required_tracks_by_id) > 0):
            for track_id in required_tracks_by_id:
                track = list(filter(lambda x: x.id == track_id,
                                    get_completed_tracks()))[0]
                if args.all:
                    download_track(track.link, args.path, args.all, args.all, args.all, args.all)
                else:
                    download_track(track.link, args.path, args.video, args.slide, args.dataset, args.exercise)
        if(len(required_tracks_by_link) > 0):
            for course_link in required_tracks_by_link:
                if(args.all):
                    download_track(course_link, args.path, args.all, args.all, args.all, args.all)
                else:
                    download_track(course_link, args.path, args.video, args.slide, args.dataset, args.exercise)


def start_thread(func):
    thread = threading.Thread(target=func)
    thread.start()
    return thread


def wait(thread):
    i = 1
    while thread.isAlive():
        print('Waiting %s%s' % ('.' * i, ' ' * (3 - i)), end='\r')
        i = i + 1 if i < 3 else 1
        time.sleep(0.4)
    print('', end='\r')
    return True


def print_courses():
    courses = get_completed_courses()
    if len(courses) == 0:
        sys.stdout.write(
            f'{bcolors.FAIL} No completed courses found!  {bcolors.BKENDC}\n')
    for course in courses:
        sys.stdout.write(
            f'{bcolors.BKGREEN} {course.id}. {course.name}  {bcolors.BKENDC}\n')


def print_tracks():
    tracks = get_completed_tracks()
    if len(tracks) == 0:
        sys.stdout.write(
            f'{bcolors.FAIL} No completed tracks found!  {bcolors.BKENDC}\n')

    for track in tracks:
        sys.stdout.write(
            f'{bcolors.BKBLUE} {track.id}. {track.name}  {bcolors.BKENDC}\n')


colorama.init()
if __name__ == "__main__":
    main()
