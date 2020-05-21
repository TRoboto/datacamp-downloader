import requests

from helper import bcolors


class Config:
    session = None
    data = {}
    sub_active = False
    token = ''

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
        }
        cookie = {'name': '_dct', 'value': cls.token, 'domain': '.datacamp.com',
                  'secure': True}
        s = requests.Session()
        s.headers = headers
        s.cookies.set(**cookie)
        cls.session = s
