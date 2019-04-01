import time
import requests
from logging import getLogger, basicConfig, INFO
from datetime import date, timedelta
from .tester import Tester

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .db import DbClient
from .settings import DISABLE_IMAGE, HEADLESS, USERNAME, PASSWORD

# config logging level
basicConfig(level=INFO)

TB_LOGIN_URL = 'https://login.taobao.com/member/login.jhtml'

headers = {
    'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/73.0.3683.86 Safari/537.36',
}

class CookieGetter():

    def __init__(self):
        self.browser = None
        self.db = DbClient()
        self.cookies = None
        self.username = USERNAME
        self.password = PASSWORD
        self.tester = Tester()
        self.logger = getLogger(__name__)

    def get_cookie(self):
        """
        Get cookies from db.
        :return: if exist return True, else False
        """
        cookie = self.db.get_cookies()
        if cookie:
            return cookie
 
    def init_browser(self):
        options = Options()
        if HEADLESS:
            options.add_argument("--headless")
        prefs = {"profile.managed_default_content_settings.images": 1}
        options.add_experimental_option("prefs", prefs)
        options.add_argument('--proxy-server=http://127.0.0.1:9000')
        options.add_argument('disable-infobars')
        options.add_argument('--no-sandbox')
        self.browser = webdriver.Chrome(options=options)
        self.browser.maximize_window()
        self.browser.implicitly_wait(3)
        self.cookies = self.get_cookie()

    def add_cookies(self):
        """
        Add cookies to browser if exist.
        :return:
        """
        if self.cookies:
            for d in self.cookies:
                self.browser.add_cookie(d)

    def switch_to_password_mode(self):
        """
        切换到密码模式
        :return:
        """
        if self.browser.find_element_by_id('J_QRCodeLogin').is_displayed():
            self.browser.find_element_by_id('J_Quick2Static').click()

    def wait_for_main_page(self):
        try:
            WebDriverWait(self.driver, 10).until(EC.title_contains('我的淘宝'))
        except Exception as e:
            print(e)

    #def wait_for_main_page(self):
    #    try:
    #        element = WebDriverWait(self.driver,10).until(
    #            EC.presence_of_element_located(
    #                By.CSS_SELECTOR,'a[title="我的淘宝"]'
    #            )
    #        )
    #    except Exception as e:
    #        print(e)

    def login(self):
        self.browser.get(TB_LOGIN_URL)
        print("Switch to password input.")
        self.switch_to_password_mode()
        time.sleep(0.5)
        print("Sending username.")
        self.write_username(self.username)
        time.sleep(2.5)
        print("Sending password.")
        self.write_password(self.password)
        time.sleep(2.5)
        print("Slide lock.")
        if self.lock_exist():
            self.unlock()
        print("Submit.")
        time.sleep(3.5)
        self.submit()
        self.wait_for_main_page()
        print("Login success.")
        print(self.browser.get_cookies())
        print("Save cookies")
        self.save_cookies()

    def save_cookies(self):
        cookies = self.browser.get_cookies()
        t = str(int(time.time()))
        d = {}
        d['time'] = t
        d['cookies'] = cookies
        self.db.insert(d)

    def set_cookies(self):
        self.navigate_to_target_page()

    def run(self):
        self.logger.info("Init date.")
        self.init_date()
        self.logger.info('Test cookies')
        flag = self.tester.test()

        if flag:
            self.logger.info('Cookie is avaliable')
            #self.navigate_to_target_page()
            #self.add_cookies()
        else:
            self.logger.info('Cookie is avaliable')
            self.logger.info("Init browser.")
            self.init_browser()
            self.logger.info('Strart login')
            self.login()
            self.logger.info('Get cookies:')
            self.logger.info(self.browser.get_cookies())
            self.browser.quit()

        # 登录成功，直接请求页面
        #self.navigate_to_target_page()

    def write_username(self, username):
        """
        输入账号
        :param username:
        :return:
        """
        username_input_element = self.browser.find_element_by_id('TPL_username_1')
        username_input_element.clear()
        username_input_element.send_keys(username)

    def write_password(self, password):
        """
        输入密码
        :param password:
        :return:
        """
        password_input_element = self.browser.find_element_by_id("TPL_password_1")
        password_input_element.clear()
        password_input_element.send_keys(password)

    def lock_exist(self):
        """
        判断是否存在滑动验证
        :return:
        """
        return self.is_element_exist('#nc_1_wrapper') and self.browser.find_element_by_id(
            'nc_1_wrapper').is_displayed()

    def unlock(self):
        """
        执行滑动解锁
        :return:
        """
        bar_element = self.browser.find_element_by_id('nc_1_n1z')
        ActionChains(self.browser).drag_and_drop_by_offset(bar_element, 800, 0).perform()
        time.sleep(1.5)
        self.browser.get_screenshot_as_file('error.png')
        if self.is_element_exist('.errloading > span'):
            error_message_element = self.browser.find_element_by_css_selector('.errloading > span')
            error_message = error_message_element.text
            self.browser.execute_script('noCaptcha.reset(1)')
            raise SessionException('滑动验证失败, message = ' + error_message)

    def is_element_exist(self, selector):
        """
        Check if the element exist
        :param selector: string of CSS selector.
        :return: if exist return True, else false.
        """
        try:
            self.browser.find_element_by_css_selector(selector)
            return True
        except NoSuchElementException:
            return False

    def submit(self):
        """
        提交登录
        :return:
        """
        self.browser.find_element_by_id('J_SubmitStatic').click()
        time.sleep(0.5)
        if self.is_element_exist("#J_Message"):
            self.write_password(self.password)
            self.submit()
            #error_message_element = self.browser.find_element_by_css_selector('#J_Message > p')
            #error_message = error_message_element.text
            #raise SessionException('Login Failed, message = ' + error_message)

    def navigate_to_target_page(self):
        print('Current Page {}'.format( self.browser.current_url))
        self.browser.get('https://www.taobao.com/')

    def search_keyword(self, keyword):
        search_box_element = self.browser.find_element_by_id("search-combobox-input-wrap")
        search_box_element.clear()
        search_box_element.send_keys(keyword)
        button_element = self.browser.find_element_by_xpath('//button')
        button_element.click()

    def init_date(self):
        date_offset = 0
        self.today_date = (date.today() + timedelta(days=-date_offset)).strftime("%Y-%m-%d")
        self.yesterday_date = (date.today() + timedelta(days=-date_offset-1)).strftime("%Y-%m-%d")

if __name__ == "__main__":
    CookieGetter().run()
