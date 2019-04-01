from pymongo import MongoClient

from .settings import MONGO_PORT, MONGO_IP

class DbClient():
    def __init__(self, ip=MONGO_IP, port=MONGO_PORT):
        conn = MongoClient(ip, port)
        self.db = conn.taobao
        self.cookie_set = self.db.cookies

    def insert(self, cookies):
        """
        Insert cookies to collection.
        :cookie: dict of cookies
        """
        self.cookie_set.insert_one(cookies)


    def delete(self):
        """
        Delete cookies.
        """
        self.cookie_set.delete_one({})

    def get_cookies(self):
        """
        Get cookies
        :return: if cookies exist, return cookie, else return None
        """
        q = self.cookie_set.find_one()
        if q:
            return q['cookies']
        else:
            return None

    def get_requests_cookie(self):
        q = self.cookie_set.find_one({})
        d = {}
        if q:
            cookies = q['cookies']
            for cookie in cookies:
                d[cookie.get('name')] = cookie.get('value')
            return d
        else:
            return None


