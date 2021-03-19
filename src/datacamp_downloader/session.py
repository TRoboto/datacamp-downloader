import requests
import cloudscraper
import pickle
from pathlib import Path
from .datacamp_utils import Datacamp
from .constants import SESSION_FILE


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
        # remove old session
        self.savefile.unlink(missing_ok=True)
        return self

    def get(self, *args, **kwargs):
        return self.session.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.session.post(*args, **kwargs)

    def add_cookie(self, cookie: dict):
        self.session.cookies.set(**cookie)
        return self
