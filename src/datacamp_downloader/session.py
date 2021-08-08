import os
import pickle
from pathlib import Path

import cloudscraper
import requests

from .constants import SESSION_FILE
from .datacamp_utils import Datacamp


class Session:
    def __init__(self) -> None:
        self.savefile = Path(SESSION_FILE)
        self.datacamp = Datacamp(self)

    def save(self):
        pickled = pickle.dumps(self)
        self.savefile.write_bytes(pickled)

    @staticmethod
    def load():
        savefile = Path(SESSION_FILE)
        if savefile.exists():
            return pickle.load(savefile.open("rb"))
        return Session()

    def restart(self):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Referer": "https://www.google.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "sec-fetch-user": "?1",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            "Upgrade-Insecure-Requests": "1",
        }
        s = requests.Session()
        s.headers = headers
        self.session = cloudscraper.create_scraper(s)
        # remove old session
        try:
            os.remove(self.savefile)
        except:
            pass
        return self

    def get(self, *args, **kwargs):
        return self.session.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.session.post(*args, **kwargs)

    def add_cookie(self, cookie: dict):
        self.session.cookies.set(**cookie)
        return self
