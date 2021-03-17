from constants import *
import requests
import cloudscraper
from termcolor import colored
from bs4 import BeautifulSoup
import os
import pickle
import codecs
import subprocess


class Logger:
    @staticmethod
    def error(text):
        print(colored("ERROR:", "red"), text)

    @staticmethod
    def warning(text):
        print(colored("WARNING:", "yellow"), text)

    @staticmethod
    def info(text):
        print(colored("INFO:", "green"), text)


class Session:
    def __init__(self) -> None:
        self.has_active_subscription = False
        self.loggedin = False
        self.data = None
        self.session = None

    def login(self, username, password):
        if self.loggedin:
            Logger.info("Already logged in!")
            return

        self.restart_session()
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

    def set_token(self, token):
        if self.loggedin:
            Logger.normal("Already logged in!")
            return

        self.token = token
        self.restart_session()
        cookie = {
            "name": "_dct",
            "value": token,
            "domain": ".datacamp.com",
            "secure": True,
        }
        self.add_cookie(cookie)
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
        self.data = data
        self.has_active_subscription = data["has_active_subscription"]

        self.save()

    def save(self):
        pickled = codecs.encode(pickle.dumps(self), "base64").decode()
        os.putenv("DATACAMP_SESSION", pickled)

    @staticmethod
    def load():
        session = os.environ.get("DATACAMP_SESSION")
        print(session)
        if session:
            session = pickle.loads(codecs.decode(session.encode(), "base64"))
            return session
        return Session()

    def restart_session(self):
        headers = {
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "en-US,en;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Referer": "https://learn.datacamp.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site",
            "DNT": "1",
            "Sec-GPC": "1",
            "TE": "Trailers",
        }
        s = requests.Session()
        s.headers = headers
        self.session = cloudscraper.create_scraper(s)

    def add_cookie(self, **cookie):
        self.session.cookies.set(**cookie)
