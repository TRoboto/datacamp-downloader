import json
import os
import re
import sys

from . import helper
from . import datacamp
from bs4 import BeautifulSoup


def download_track(url, folder, videos_download, exercise_download, datasets_download):
    page = con.session.get(helper.fix_link(url))
    soup = BeautifulSoup(page.text, "html.parser")
    all_courses = soup.findAll(
        "a", {"href": re.compile("^/courses/"), "class": re.compile("^course")}
    )
    track_title = soup.find("title").getText().split("|")[0].strip()
    folder = os.path.join(folder, track_title)

    all_links = ["https://www.datacamp.com" + x["href"] for x in all_courses]
    for i in all_links:
        if i.endswith("/continue"):
            all_links.remove(i)
    all_links = list(dict.fromkeys(all_links))
    sys.stdout.write(f"{bcolors.BKBLUE}  {track_title}  {bcolors.BKENDC}\n")
    for i, link in enumerate(all_links):
        download_course(
            link, folder, videos_download, exercise_download, datasets_download, i + 1
        )
