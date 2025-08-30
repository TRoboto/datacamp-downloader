import json
import os
import pickle
import json
from webdriver_manager.chrome import ChromeDriverManager
import re
from bs4 import BeautifulSoup
import os
from pathlib import Path

# Prefer top-level undetected_chromedriver (works with Selenium 4); fallback to v2.
try:
    import undetected_chromedriver as uc
except Exception:
    import undetected_chromedriver.v2 as uc

# Selenium helper imports (we use these to create Service/options safely)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .constants import HOME_PAGE, SESSION_FILE
from .datacamp_utils import Datacamp


class Session:
    def __init__(self) -> None:
        self.savefile = Path(SESSION_FILE)
        self.datacamp = self.load_datacamp()

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

    def _setup_driver(self, headless=True):
        try:
            options = uc.ChromeOptions()
        except Exception:
            options = ChromeOptions()

        try:
            options.headless = headless
        except Exception:
            if headless:
                options.add_argument("--headless=new")

        # existing flags...
        options.add_argument("--no-first-run")
        options.add_argument("--no-service-autorun")
        options.add_argument("--password-store=basic")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-browser-side-navigation")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-notifications")
        options.add_argument("--content-shell-hide-toolbar")
        options.add_argument("--top-controls-hide-threshold")
        options.add_argument("--force-app-mode")
        options.add_argument("--hide-scrollbars")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # get the absolute path of the installed package
        package_dir = os.path.dirname(os.path.abspath(__file__))
        
        # create a chrome profile folder inside the package directory
        profile_dir = os.path.join(package_dir, "dc_chrome_profile")

        # make sure it exists
        os.makedirs(profile_dir, exist_ok=True)

        # tell Chrome to use it
        options.add_argument(f"--user-data-dir={profile_dir}")


        service = ChromeService(executable_path=ChromeDriverManager().install())
        try:
            self.driver = uc.Chrome(service=service, options=options)
            return
        except Exception:
            self.driver = webdriver.Chrome(service=service, options=options)

    def start(self, headless=False):
        if hasattr(self, "driver"):
            return
        self._setup_driver(headless)
        self.driver.get(HOME_PAGE)
        self.bypass_cloudflare(HOME_PAGE)
        if self.datacamp.token:
            self.add_token(self.datacamp.token)

    def bypass_cloudflare(self, url):
        try:
            self.get_element_by_id("cf-spinner-allow-5-secs")
            with self.driver:
                self.driver.get(url)
        except:
            pass

    def get(self, url):
        self.start()
        self.driver.get(url)
        self.bypass_cloudflare(url)
        return self.driver.page_source



    def get_json(self, url):
        page = self.get(url).strip()

        # Parse with BeautifulSoup
        soup = BeautifulSoup(page, "html.parser")
        pre = soup.find("pre")

        if pre:
            page = pre.text  # ✅ grab only the JSON inside <pre>
        else:
            page = page  # maybe raw JSON already

        # Debug
        #print("\n\n[DEBUG get_json cleaned] First 200 chars:\n", page[:200], "\n\n")

        return json.loads(page)

    def to_json(self, page: str):
        return json.loads(page)

    def get_element_by_id(self, id: str) -> WebElement:
        return self.driver.find_element(By.ID, id)

    def get_element_by_xpath(self, xpath: str) -> WebElement:
        return self.driver.find_element(By.XPATH, xpath)

    def click_element(self, id: str):
        self.get_element_by_id(id).click()

    def wait_for_element_by_css_selector(self, *css: str, timeout: int = 10):
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_any_elements_located((By.CSS_SELECTOR, ",".join(css)))
        )

    def add_token(self, token: str):
        cookie = {
            "name": "_dct",
            "value": token,
            "domain": ".datacamp.com",
            "secure": True,
        }
        self.driver.add_cookie(cookie)
        return self
