import requests

from helper import bcolors


class Config:
    session = None
    data = {}
    active = False
    token = ''

    @staticmethod
    def set_token(token):
        Config.token = token
        Config.set_new_session()
        page = Config.session.get('https://www.datacamp.com/api/users/signed_in')
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

        Config.data = data
        Config.active = data['has_active_subscription']

    @staticmethod
    def set_new_session():
        headers = {
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8',
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
        }
        cookie = {'name': '_dct', 'value': Config.token, 'domain': '.datacamp.com',
                  'secure': True}
        s = requests.Session()
        s.headers = headers
        s.cookies.set(**cookie)
        Config.session = s
