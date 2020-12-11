import requests
import cloudscraper
from helper import bcolors


class Config:
    session = None
    data = {}
    sub_active = False
    token = ''
    login = False

    @classmethod
    def set_token(cls, token):
        cls.token = token
        cls.set_new_session()
        page = cls.session.get('https://www.datacamp.com/api/users/signed_in')
        try:
            data = page.json()
        except:
            print(f'{bcolors.FAIL}Please provide a valid token!{bcolors.ENDC}')
            return

        print("Hi, " + data['first_name'])

        if data['has_active_subscription']:
            print(f'{bcolors.HEADER}Active subscription found{bcolors.ENDC}')
        else:
            print(f'{bcolors.FAIL}No active subscription found{bcolors.ENDC}')

        cls.login = True
        cls.data = data
        cls.sub_active = data['has_active_subscription']

    @classmethod
    def set_new_session(cls):
        headers = {
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8',
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Referer': 'https://learn.datacamp.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-site',
            'DNT': '1',
            'Sec-GPC': '1',
            'TE': 'Trailers'
        }
        cookie = {'name': '_dct', 'value': cls.token, 'domain': '.datacamp.com',
                  'secure': True}
        s = requests.Session()
        s.headers = headers
        s.cookies.set(**cookie)
        cls.session = cloudscraper.create_scraper(s)
