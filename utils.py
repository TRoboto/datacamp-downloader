import json
import os
import re
import sys

from bs4 import BeautifulSoup

import helper
from classes import Template
from config import Config as con
from helper import bcolors


def download_track(url, folder, videos_download, slides_download, datasets_download, exercise_download):
    page = con.session.get(helper.fix_link(url))
    soup = BeautifulSoup(page.text, 'html.parser')
    all_courses = soup.findAll('a', {
        'href': re.compile('^/courses/'),
        'class': re.compile('^course')
    })
    track_title = soup.find('title').getText().split('|')[0].strip()
    folder = os.path.join(folder, track_title)

    all_links = ['https://www.datacamp.com' + x['href'] for x in all_courses]
    for i in all_links:
        if i.endswith('/continue'):
            all_links.remove(i)
    all_links = list(dict.fromkeys(all_links))
    sys.stdout.write(
        f'{bcolors.BKBLUE}  {track_title}  {bcolors.BKENDC}\n')
    for i, link in enumerate(all_links):
        download_course(link, folder, videos_download, slides_download, datasets_download, exercise_download, i + 1)


def download_course(url, folder, videos_download, slides_download, datasets_download, exercise_download, number=None):
    course_id, title = get_course_id_and_title(url)
    title = helper.format_filename(title)

    if number is not None:
        title = str(number) + ". " + title

    sys.stdout.write(
        f'{bcolors.BKGREEN} {title}  {bcolors.BKENDC}\n')

    if slides_download:
        download_slides(course_id, os.path.join(folder, title))

    if exercise_download:
        download_exercises(course_id, os.path.join(
            folder, title))
    if videos_download:
        download_videos(course_id, os.path.join(
            folder, title))
    if datasets_download:
        download_datasets(url, os.path.join(
            folder, title))


def get_chapter_exercises(course_id, chapter_id):
    page = con.session.get('https://campus-api.datacamp.com/api/courses/{}/chapters/{}/progress'
                           .format(course_id, chapter_id))
    return page.json()


def get_course_chapters(course_id):
    page = con.session.get(
        'https://campus-api.datacamp.com/api/courses/{}/progress'.format(course_id))
    return page.json()


def get_course_id_and_title(course_url):
    page = con.session.get(helper.fix_link(course_url))
    soup = BeautifulSoup(page.text, 'html.parser')
    try:
        title = soup.find('title').getText().split('|')[0].strip()
    except Exception as e:
        message = e.args
        return
    course_id = re.search(r'/course_(\d+)/', page.text).group(1)
    return course_id, title


@helper.memoize
def get_completed_tracks():
    profile = con.session.get(
        'https://www.datacamp.com/profile/' + con.data['slug'])
    soup = BeautifulSoup(profile.text, 'html.parser')
    tracks_name = soup.findAll('div', {'class': 'track-block__main'})
    tracks_link = soup.findAll('a', {'href': re.compile('^/tracks'),
                                     'class': 'shim'})
    tracks = []
    for i in range(len(tracks_link)):
        link = 'https://www.datacamp.com' + tracks_link[i]['href']
        tracks.append(
            Template(i + 1, tracks_name[i].getText().replace('\n', ' ').strip(), link))
    return tracks


@helper.memoize
def get_completed_courses():
    profile = con.session.get(
        'https://www.datacamp.com/profile/' + con.data['slug'])
    soup = BeautifulSoup(profile.text, 'html.parser')
    courses_name = soup.findAll('h4', {'class': 'course-block__title'})
    courses_link = soup.findAll('a', {'class': 'course-block__link ds-snowplow-link-course-block'})
    courses = []
    for i in range(len(courses_link)):
        link = 'https://www.datacamp.com' + courses_link[i]['href']
        courses.append(
            Template(i + 1, courses_name[i].getText().strip(), link))
    return courses


def download_slides(course_id, folder):
    page = con.session.get('https://www.datacamp.com/courses/{}/continue'
                           .format(course_id))
    slide_links = set(re.findall(
        r'(https?://s3.[/|\w|:|.|-]+[^/])&', page.text))
    slide_links = slide_links.union(set(re.findall(
        r'(https?://projector[/|\w|:|.|-]+[^/])&', page.text)))
    if len(slide_links) == 0:
        sys.stdout.write(
            f'{bcolors.FAIL}No slides found!{bcolors.ENDC}\n')
        return

    sys.stdout.write(
        f'{bcolors.BOLD}Downloading slides...{bcolors.ENDC}\n')
    for link in slide_links:
        helper.download_file(con, link,
                             os.path.join(folder, link.split('/')[-1]))


def download_exercises(course_id, folder):
    chapters = get_course_chapters(course_id)
    sys.stdout.write(
        f'{bcolors.BOLD}Downloading exercises...{bcolors.ENDC}\n')
    for ind, chapter in enumerate(chapters['user_chapters'], 1):
        exr_string = ''
        counter = 1
        exrs = get_chapter_exercises(course_id, chapter['chapter_id'])
        for exr in exrs:
            if not exr['completed']:
                continue
            if len(exr['subexercises']) > 0:
                exr_string += f'# Exercise_{counter} \n'
                for i, sub in enumerate(exr['subexercises'], 1):
                    exr_string += '#' + str(i) + "\n"
                    exr_string += sub['last_attempt'] + '\n'
                exr_string += '\n\n'
                exr_string += '-' * 50 + '\n'
                counter += 1
            elif exr['last_attempt'] and 'selected_option' not in exr['last_attempt']:
                exr_string += f'# Exercise_{counter} \n'
                exr_string += exr['last_attempt']
                exr_string += '\n\n'
                exr_string += '-' * 50 + '\n'
                counter += 1
        if exr_string:
            helper.save_file(os.path.join(folder, f'ch{ind}_exercises.py'), exr_string)


def download_videos(course_id, folder):
    chapters = get_course_chapters(course_id)
    display_text = True
    for chapter in chapters['user_chapters']:
        page = con.session.get('https://www.datacamp.com/courses/{}/chapters/{}/continue'
                               .format(course_id, chapter['chapter_id']))
        video_ids = set(re.findall(
            r';(course_{}_[\d|\w]+)&'.format(course_id), page.text))
        video_type = 1
        if len(video_ids) == 0:
            video_ids = set(re.findall(
                r'(//videos.[/|\w|:|.|-]+[^/])&', page.text))
            video_type = 2
        if len(video_ids) == 0:
            sys.stdout.write(
                f'{bcolors.FAIL}No videos found!{bcolors.ENDC}\n')
            return

        if display_text:
            sys.stdout.write(
                f'{bcolors.BOLD}Downloading videos...{bcolors.ENDC}\n')
            display_text = False

        for video_id in video_ids:
            while True:
                try:
                    if video_type == 1:
                        video_page = con.session.get(
                            'https://projector.datacamp.com/?projector_key=' + video_id)
                    elif video_type == 2:
                        video_page = con.session.get(
                            'https://projector.datacamp.com/?video_hls=' + video_id)
                except:
                    helper.handle_error(con)
                    continue
                break
            soup = BeautifulSoup(video_page.text, 'html.parser')
            video_url = json.loads(soup.find(
                "input", {"id": "videoData"})['value'])

            link = video_url['video_mp4_link']

            if link is None:
                sys.stdout.write(
                    f'{bcolors.FAIL}Videos cannot be downloaded!{bcolors.ENDC}\n')
                return
            if link.endswith('mp4') and not link.startswith('http'):
                link = 'https://' + link[2:]
                name = link.split('/')[-1]
            else:
                if video_type == 1:
                    video_name_url = json.loads(soup.find(
                        "input", {"id": "slideDeckData"})['value'])
                    link_name = video_name_url['plain_video_mp4_link']
                    if link_name is not None:
                        name = link_name.split('/')[-1]
                    else:
                        name = video_url['audio_link'].split(
                            '/')[-1].split('.')[0] + '.mp4'
                elif video_type == 2:
                    link_name = video_url['video_mp4_link']
                    name = link_name.split('/')[-1]
                if name.count('_') > 1:
                    name = name.split('_')[1:]
                    name = '_'.join(name)
            file_path = os.path.join(folder, name)

            if helper.file_exist(file_path):
                continue
            helper.download_file(con, link, file_path)


def download_datasets(link, folder):
    page = con.session.get(helper.fix_link(link))
    soup = BeautifulSoup(page.text, 'html.parser')

    dataset = soup.findAll('a', {
        'href': re.compile('^https'),
        'class': re.compile('^link-borderless')
    })
    if len(dataset) == 0:
        sys.stdout.write(
            f'{bcolors.FAIL}No dataset found!{bcolors.ENDC}\n')
        return

    titles = [x.text.strip() for x in dataset]
    all_links = [x['href'] for x in dataset]
    sys.stdout.write(
        f'{bcolors.BOLD}Downloading dataset...{bcolors.ENDC}\n')
    if not os.path.exists(folder):
        os.mkdir(folder)
    if(not os.path.exists(os.path.join(folder, 'Dataset'))):
        os.mkdir(os.path.join(folder, 'Dataset'))
    for link, title in zip(all_links, titles):
        dir = os.path.join(folder, 'Dataset', title) + '.' + link.split('.')[-1]
        helper.download_file(con, link, dir)
