import requests
import time
import json
import re
from db import Mongo
from settings import KEYWORD, HEADERS, MAX_PAGE, MONGO_IP, MONGO_PORT, API_URL

class Crawler():
    def __init__(self):
        self.db = Mongo()
        self.page = None
        self.session = None
        self.set_session()

    def set_session(self):
        s = requests.session()
        s.cookies.update(self.get_cookie())
        s.headers.update(HEADERS)
        self.session = s

    def get_cookie(self):
        r = requests.get(API_URL)
        return json.loads(r.text)

    def get_page(self, page, keyword=KEYWORD):
        url = 'https://s.taobao.com/search?q={}&s={}'.format(keyword, page)
        #r = self.session.get(url, headers=HEADERS, cookies=self.get_cookie())
        r = self.session.get(url)
        if r.text.find('请输入') > 0:
            print("Need Login!!!")
            return False
            #raise Exception('Get page failed!')
        self.page = r.text
        return True

    def parse(self):
        pattern = re.compile(r'g_page_config = ({.*});')
        m = re.search(pattern, self.page)
        if not m:
            print('Cannot fount data in this page.')
            with open('log_page.txt', 'w') as f:
                f.write(self.page)
            return Fasle
        g_page_config = json.loads(m.group(1))
        auctions = g_page_config['mods']['itemlist']['data']['auctions']
        for auction in auctions:
            d = {}
            d['nid'] = auction['nid']
            d['category'] = auction['category']
            d['comment_cnt'] = auction['comment_count']
            d['comment_url'] = auction['comment_url']
            d['shop_location']  = auction['item_loc']
            d['shop_name'] = auction['nick']
            d['price'] = auction['view_price']
            d['sales_cnt'] = auction['view_sales']
            d['is_tmall'] = auction['shopcard']['isTmall']
            d['title'] = auction['raw_title']
            print(d.get('nid'), d.get('title'))
            self.db.insert(d)

    def run(self):
        for i in range(21, MAX_PAGE+1):
            print('Crawling page {}'.format(i))
            flag = self.get_page(i)
            if not flag:
                return
            self.parse()
            time.sleep(4)

if __name__ == '__main__':
    Crawler().run()
