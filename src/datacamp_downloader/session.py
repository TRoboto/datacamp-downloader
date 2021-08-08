import json
import os
import pickle
from pathlib import Path

# import chromedriver_autoinstaller
import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By

from .constants import HOME_PAGE, SESSION_FILE
from .datacamp_utils import Datacamp

# Check if the current version of chromedriver exists
# and if it doesn't exist, download it automatically,
# then add chromedriver to path
# chromedriver_autoinstaller.install()


class Session:
    def __init__(self) -> None:
        self.savefile = Path(SESSION_FILE)
        self.datacamp = self.load_datacamp()
        self.start()
        if self.datacamp.token:
            self.add_token(self.datacamp.token)

    def save(self):
        self.datacamp.session = None
        pickled = pickle.dumps(self.datacamp)
        self.savefile.write_bytes(pickled)

    def load_datacamp(self):
        if self.savefile.exists():
            datacamp = pickle.load(self.savefile.open("rb"))
            datacamp.session = self
            return datacamp
        return Datacamp(self)

    def reset(self):
        try:
            os.remove(SESSION_FILE)
        except:
            pass

    def start(self):
        self.driver = uc.Chrome()
        self.driver.get(HOME_PAGE)

    def bypass_cloudflare(self, url):
        with self.driver:
            self.driver.get(url)

    def get(self, url):
        self.driver.get(url)
        try:
            self.driver.find_element(By.ID, "cf-spinner-allow-5-secs")
            self.bypass_cloudflare(url)
        except:
            pass
        return self.driver.page_source

    def get_json(self, url):
        page = self.get(url)
        page = self.driver.find_element(By.TAG_NAME, "pre").text
        parsed_json = json.loads(page)
        return parsed_json

    def post(self, *args, **kwargs):
        return self.session.post(*args, **kwargs)

    def add_token(self, token: str):
        cookie = {
            "name": "_dct",
            "value": token,
            "domain": ".datacamp.com",
            "secure": True,
        }
        self.driver.add_cookie(cookie)
        return self
