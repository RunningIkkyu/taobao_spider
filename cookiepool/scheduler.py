import time
from multiprocessing import Process
from cookiepool.api import app
from cookiepool.tester import Tester
from cookiepool.db import DbClient
from cookiepool.login import CookieGetter
from cookiepool.settings import TEST_CYCLE, LOGIN_CYCLE
from cookiepool.settings import TESTER_ENABLE, LOGIN_ENABLE, API_ENABLE
from cookiepool.settings import API_HOST, API_PORT

class Scheduler():

    def schedule_tester(self, cycle=TEST_CYCLE):
        tester = Tester()
        while True:
            tester.run()
            time.sleep(cycle)
 
    def schedule_login(self, cycle=LOGIN_CYCLE):
        login = CookieGetter()
        while True:
            login.run()
            time.sleep(cycle)

    def schedule_api(self):
        app.run(API_HOST, API_PORT)

    def run(self):
        if TESTER_ENABLE:
            tester_process = Process(target=self.schedule_tester)
            tester_process.start()
        if LOGIN_ENABLE:
            login_process = Process(target=self.schedule_login)
            login_process.start()
        if API_ENABLE:
            api_process = Process(target=self.schedule_api)
            api_process.start()
