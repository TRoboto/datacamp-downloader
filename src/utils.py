from config import Config as con
import sys
import os
import helper
from helper import bcolors
from bs4 import BeautifulSoup
import json
import re
from classes import Track


def download_track(track, folder, videos_download):
    page = con.session.get(helper.embbed_link(track.link))
    soup = BeautifulSoup(page.text, 'html.parser')
    all_courses = soup.findAll('a', {
        'href': re.compile('^/courses/'),
        'class': re.compile('^course')
    })
    track_title = soup.find('title').getText().split('|')[0].strip()
    folder = os.path.join(folder, track_title)

    all_links = ['https://www.datacamp.com' + x['href'] for x in all_courses]
    sys.stdout.write(
        f'{bcolors.BKBLUE}  {track_title}  {bcolors.BKENDC}\n')
    for i, link in enumerate(all_links):
        download_course(link, folder, videos_download, i + 1)


def download_course(url, folder, videos_download, number=None):
    course_id, title = get_course_id_and_title(url)
    title = helper.format_filename(title)
    if number is not None:
        title = str(number) + ". " + title
    sys.stdout.write(
        f'{bcolors.BKGREEN} {title}  {bcolors.BKENDC}\n')
    download_slides(course_id, os.path.join(
        folder, title))
    if videos_download:
        download_videos(course_id, os.path.join(
            folder, title))


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

    # sys.stdout.write(
    #     f'{bcolors.OKGREEN}Slides has been successfully downloaded!{bcolors.ENDC}\n')


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


def get_chapter_content(course_id, chapter_id):
    page = con.session.get('https://campus-api.datacamp.com/api/courses/{}/chapters/{}/progress'
                           .format(course_id, chapter_id))
    return page.json()


def get_course_chapters(course_id):
    page = con.session.get(
        'https://campus-api.datacamp.com/api/courses/{}/progress'.format(course_id))
    return page.json()


def get_course_id(course_url):
    page = con.session.get(course_url)
    return re.search(r'/course_(\d+)/', page.text).group(1)


def get_course_id_and_title(course_url):
    page = con.session.get(helper.embbed_link(course_url))
    soup = BeautifulSoup(page.text, 'html.parser')
    try:
        title = soup.find('title').getText().split('|')[0].strip()
    except Exception as e:
        message = e.args
        return
    id = soup.find(
        "input", {"name": "course_id"})['value']
    return id, title


completed_tracks = None


def get_completed_tracks():
    global completed_tracks
    if completed_tracks is not None:
        return completed_tracks
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
            Track(i + 1, tracks_name[i].getText().replace('\n', ' ').strip(), link))
    completed_tracks = tracks
    return tracks


completed_courses = None


def get_completed_courses():
    global completed_courses
    if completed_courses is not None:
        return completed_courses
    profile = con.session.get(
        'https://www.datacamp.com/profile/' + con.data['slug'])
    soup = BeautifulSoup(profile.text, 'html.parser')
    courses_name = soup.findAll('h4', {'class': 'course-block__title'})
    courses_link = soup.findAll('a', {'class': 'course-block__link ds-snowplow-link-course-block'})
    courses = []
    for i in range(len(courses_link)):
        link = 'https://www.datacamp.com' + courses_link[i]['href']
        courses.append(
            Track(i + 1, courses_name[i].getText().strip(), link))
    completed_courses = courses
    return courses
