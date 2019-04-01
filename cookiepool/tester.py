import requests
from logging import getLogger, basicConfig, DEBUG
from .db import DbClient
from .settings import TEST_URL, HEADERS

basicConfig(level=DEBUG)

class Tester():
    def __init__(self):
        self.test_url = TEST_URL
        self.db = DbClient()
        self.logger = getLogger(__name__)

    def __get_cookies(self):
        return self.db.get_requests_cookie()

    def test(self):
        """
        Test if cookies can work.
        :return: if cookies words, return True, else False
        """
        cookies = self.__get_cookies()
        print(cookies)
        if cookies is None:
            self.logger.debug('No cookies in db.')
            return False
        r = requests.get(self.test_url, cookies=cookies, headers=HEADERS)
        if (not r.ok) or (r.text.find('请输入密码') > 0):
            self.logger.info('Cookies does not work, delete it from database')
            self.db.delete()
            return False
        self.logger.info('Cookies works')
        return True

    def run(self):
        print('Testing...')
        self.test()

if __name__ == '__main__':
    Tester().test()
