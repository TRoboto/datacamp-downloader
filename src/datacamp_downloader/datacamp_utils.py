from pathlib import Path
import sys
from bs4 import BeautifulSoup
import re
import requests

from .constants import (
    COURSE_DETAILS_API,
    EXERCISE_DETAILS_API,
    LOGIN_DATA,
    LOGIN_DETAILS_URL,
    LOGIN_URL,
    PROFILE_URL,
    PROGRESS_API,
)
from .helper import Logger, animate_wait, download_file, print_progress, save_text
from .templates.track import Track
from .templates.course import Chapter, Course
from .templates.exercise import Exercise


def login_required(f):
    def wrapper(*args):
        self = args[0]
        if not isinstance(self, Datacamp):
            Logger.error(f"{login_required.__name__} can only decorate Datacamp class.")
            return
        if not self.loggedin:
            Logger.error("Login first!")
            return
        # if not self.has_active_subscription:
        #     Logger.error("No active subscription found.")
        #     return
        return f(*args)

    return wrapper


def try_except_request(f):
    def wrapper(*args):
        self = args[0]
        id = args[1]
        if not isinstance(self, Datacamp):
            Logger.error(f"{login_required.__name__} can only decorate Datacamp class.")
            return

        try:
            return f(*args)
        except (ValueError, requests.exceptions.RequestException):
            Logger.warning(f"Couldn't get the course with id {id}")
        return

    return wrapper


class Datacamp:
    def __init__(self, session) -> None:

        self.session = session
        self.username = None
        self.password = None
        self.token = None
        self.has_active_subscription = False
        self.loggedin = False
        self.login_data = None

        self.courses = []
        self.tracks = []

    @animate_wait
    def login(self, username, password):
        if username == self.username and self.password == password and self.loggedin:
            Logger.info("Already logged in!")
            return

        self.session.restart()
        self.username = username
        self.password = password

        req = self.session.get(LOGIN_URL)
        if not req or req.status_code != 200 or not req.text:
            Logger.error("Cannot access datacamp website!")
            return
        soup = BeautifulSoup(req.text, "html.parser")
        authenticity_token = soup.find("input", {"name": "authenticity_token"}).get(
            "value"
        )
        if not authenticity_token:
            Logger.error("Cannot find authenticity_token attribute!")
            return

        login_req = self.session.post(
            LOGIN_URL,
            data=LOGIN_DATA.format(
                email=username, password=password, authenticity_token=authenticity_token
            ).encode("utf-8"),
        )
        if (
            not login_req
            or login_req.status_code != 200
            or "/users/sign_up" in login_req.text
        ):
            Logger.error("Incorrent username/password")
            return

        self._set_profile()

    @animate_wait
    def set_token(self, token):
        if self.token == token and self.loggedin:
            Logger.info("Already logged in!")
            return

        self.session.restart()
        self.token = token
        cookie = {
            "name": "_dct",
            "value": token,
            "domain": ".datacamp.com",
            "secure": True,
        }
        self.session.add_cookie(cookie)
        self._set_profile()

    def _set_profile(self):
        page = self.session.get(LOGIN_DETAILS_URL)
        try:
            data = page.json()
        except:
            Logger.error("Incorrect input token!")
            return

        Logger.info("Hi, " + data["first_name"])

        if data["has_active_subscription"]:
            Logger.info("Active subscription found")
        else:
            Logger.warning("No active subscription found")

        self.loggedin = True
        self.login_data = data
        self.has_active_subscription = data["has_active_subscription"]

        self.session.save()

    @login_required
    def list_completed_tracks(self, refresh):
        if refresh or not self.tracks:
            self.get_completed_tracks()
        rows = [["#", "Title"]]
        for track in self.tracks:
            rows.append([track.id, track.name])
        Logger.print_table(rows)

    @login_required
    def list_completed_courses(self, refresh):
        if refresh or not self.courses:
            self.get_completed_courses()
        rows = [["#", "ID", "Title", "Datasets", "Exercises", "Videos"]]
        for i, course in enumerate(self.courses, 1):
            rows.append(
                [
                    i,
                    course.id,
                    course.title,
                    len(course.datasets),
                    sum([c.nb_exercises for c in course.chapters]),
                    sum([c.number_of_videos for c in course.chapters]),
                ]
            )
        Logger.print_table(rows)

    @login_required
    def download_courses(
        self,
        courses_ids,
        directory,
        slides,
        datasets,
        videos,
        exercises,
        subtitle,
        include_audios,
    ):
        courses_to_download = [self.get_course(id) for id in courses_ids]
        path = Path(directory)
        for course in courses_to_download:
            if not course:
                continue
            self._download_course(
                course,
                path,
                slides,
                datasets,
                videos,
                exercises,
                subtitle,
            )

    def _download_course(
        self,
        course: Course,
        path: Path,
        slides,
        datasets,
        videos,
        exercises,
        subtitle,
    ):
        download_path = path / course.slug
        if datasets:
            for dataset in course.datasets:
                download_file(
                    self.session, dataset.asset_url, download_path / "datasets"
                )
        for chapter in course.chapters:
            cpath = download_path / self._get_chapter_name(chapter)
            if slides:
                download_file(self.session, chapter.slides_link, cpath)
            if exercises:
                self.download_exercises(course.id, chapter, cpath)

    def _get_chapter_name(self, chapter: Chapter):
        if chapter.title and chapter.title_meta:
            return chapter.slug
        if chapter.title:
            return f"chapter-{chapter.number}-{chapter.slug}"
        return f"chapter-{chapter.number}"

    def download_exercises(self, course_id, chapter: Chapter, path: Path):
        ids = self._get_exercises_ids(course_id, chapter.id)
        counter = 1
        for i, id in enumerate(ids, 1):
            print_progress(i, len(ids), f"Chapter {chapter.number} exercises")
            exercise = self._get_exercise(id)
            if not exercise.is_video:
                save_text(path / "exercises" / f"ex{counter}.md", str(exercise))
                counter += 1
        sys.stdout.write("\n")

    @animate_wait
    def get_completed_tracks(self):
        self.tracks = []
        profile = self.session.get(PROFILE_URL.format(slug=self.login_data["slug"]))
        soup = BeautifulSoup(profile.text, "html.parser")
        tracks_name = soup.findAll("div", {"class": "track-block__main"})
        tracks_link = soup.findAll(
            "a", {"href": re.compile("^/tracks"), "class": "shim"}
        )
        for i in range(len(tracks_link)):
            link = "https://www.datacamp.com" + tracks_link[i]["href"]
            self.tracks.append(
                Track(i + 1, tracks_name[i].getText().replace("\n", " ").strip(), link)
            )
        self.session.save()
        return self.tracks

    @animate_wait
    def get_completed_courses(self):
        self.courses = []
        profile = self.session.get(PROFILE_URL.format(slug=self.login_data["slug"]))
        soup = BeautifulSoup(profile.text, "html.parser")
        courses_id = soup.findAll("article", {"class": re.compile("^js-async")})
        for id_tag in courses_id:
            id = id_tag.get("data-id")
            course = self._get_course(id)
            if course:
                self.courses.append(course)

        self.session.save()
        return self.courses

    @try_except_request
    def _get_exercises_ids(self, course_id, chapter_id):
        if not course_id or not chapter_id:
            raise ValueError("ID tags not found.")
        res = self.session.get(
            PROGRESS_API.format(course_id=course_id, chapter_id=chapter_id)
        )
        data = res.json()
        if "error" in data:
            raise ValueError("Cannot get info.")
        ids = [e["exercise_id"] for e in data]
        return ids

    @try_except_request
    def _get_exercise(self, id):
        if not id:
            raise ValueError("ID tag not found.")
        res = self.session.get(EXERCISE_DETAILS_API.format(id=id))
        if "error" in res.json():
            raise ValueError("Cannot get info.")
        return Exercise(**res.json())

    @try_except_request
    def _get_course(self, id):
        if not id:
            raise ValueError("ID tag not found.")
        res = self.session.get(COURSE_DETAILS_API.format(id=id))
        if "error" in res.json():
            raise ValueError("Cannot get info.")
        return Course(**res.json())

    @animate_wait
    def get_course(self, id):
        for course in self.courses:
            if course.id == id:
                return course
        return self._get_course(id)