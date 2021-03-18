from typing import List
from bs4 import BeautifulSoup
import re

from .constants import LOGIN_DATA, LOGIN_DETAILS_URL, LOGIN_URL
from .helper import Logger, animate_wait
from .classes import Course, Track


def login_required(f):
    def wrapper(*args):
        self = args[0]
        if not isinstance(self, Datacamp):
            Logger.error(f"{login_required.__name__} can only decorate Datacamp class.")
            return
        if not self.loggedin:
            Logger.error("Login first!")
            return
        return f(*args)

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
            Logger.error("Please provide a valid token!")
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
        if refresh or not hasattr(self, "tracks"):
            self.get_completed_tracks()
        for track in self.tracks:
            Logger.print(track.name, f"{track.id}-", "blue")

    @login_required
    def list_completed_courses(self, refresh):
        if refresh or not hasattr(self, "courses"):
            self.get_completed_courses()
        for course in self.courses:
            Logger.print(course.name, f"{course.id}-", "blue")

    @login_required
    @animate_wait
    def get_completed_tracks(self):
        self.tracks = []
        profile = self.session.get(
            "https://www.datacamp.com/profile/" + self.login_data["slug"]
        )
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

    @login_required
    @animate_wait
    def get_completed_courses(self):
        self.courses = []
        profile = self.session.get(
            "https://www.datacamp.com/profile/" + self.login_data["slug"]
        )
        soup = BeautifulSoup(profile.text, "html.parser")
        courses_name = soup.findAll("h4", {"class": "course-block__title"})
        courses_link = soup.findAll("a", {"class": re.compile("^course-block__link")})
        for i in range(len(courses_link)):
            link = "https://www.datacamp.com" + courses_link[i]["href"]
            self.courses.append(Course(i + 1, courses_name[i].getText().strip(), link))

        self.session.save()
        return self.courses
