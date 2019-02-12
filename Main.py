import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import time

se = requests.Session()  # 模拟登陆
requests.adapters.DEFAULT_RETRIES = 15
se.mount('http://', HTTPAdapter(max_retries=3))  # 重联
se.mount('https://', HTTPAdapter(max_retries=3))


class Pixiv(object):

    def __init__(self):
        self.base_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
        self.login_url = 'https://accounts.pixiv.net/api/login?lang=zh'
        self.target_url = 'https://www.pixiv.net/ranking.php?mode=weekly'
        self.main_url = 'https://www.pixiv.net'
        self.headers = {
            # 'Host': 'accounts.pixiv.net',
            # 'Origin': 'https://accounts.pixiv.net',
            'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                          ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
            # 'X-Requested-With': 'XMLHttpRequest'
            # 'Connection': 'close',
        }
        self.proxies = {
            'https': 'https://127.0.0.1:1080',
            'http': 'http://127.0.0.1:1080'
        }
        self.pixiv_id = '835437423@qq.com',  # 2664504212@qq.com
        self.password = 'yjw3616807',  # knxy0616
        self.post_key = []
        self.return_to = 'https://www.pixiv.net/'
        self.html_path = 'D:\Software\pythonload\Re.html'
        self.load_path = 'D:\Software\pythonload'  # 存放图片路径
        self.get_number = 10

    def login(self):
        post_key_xml = se.get(self.base_url, headers=self.headers).text
        post_key_soup = BeautifulSoup(post_key_xml, 'lxml')
        self.post_key = post_key_soup.find('input')['value']
        # 构造请求体
        data = {
            'pixiv_id': self.pixiv_id,
            'password': self.password,
            'post_key': self.post_key,
            'return_to': self.return_to
        }
        se.post(self.login_url, data=data, headers=self.headers)

    def secontect(self):
        s = se.get(self.target_url,proxies=self.proxies)  # https://www.pixiv.net/setting_user.php
        with open(self.html_path, 'w', encoding='utf-8') as f:
            f.write(s.text)

    def beautifulsoup(self):
        soup = BeautifulSoup(open(self.html_path, 'r', encoding='utf-8'), features="html.parser")  # 初始化
        with open('D:\Software\pythonload\Re_soup.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())  # 保存soup以便check
        title = soup.find_all("a", class_="title", limit=self.get_number)  # 寻找每周前self.get_number
        src_headers = self.headers
        for i in title:
            temp_url = self.main_url + '/' + i['href']
            # print(temp_url)  # 详细页的url
            temp_clear = se.get(temp_url, headers=src_headers,proxies=self.proxies)
            clear_soup = BeautifulSoup(temp_clear.text, features="html.parser")
            with open('D:\\Software\\pythonload\\' + i.string + '.html', 'w', encoding='utf-8') as f:
                f.write(clear_soup.prettify())
                op = clear_soup.prettify().find('"original":"')
                ed = clear_soup.prettify().find('},"tags')
                # print(op)
                # print(ed)
                original_url = clear_soup.prettify()[op + 12:ed - 1]
                # print(original_url)
                adapt_url = original_url.replace('\/', '/')
                print(adapt_url)
                img = se.get(adapt_url, headers=src_headers,proxies=self.proxies)
                with open('D:\\Software\\pythonload\\' + i.text + '.jpg', 'wb') as f:  # 图片要用b,对text要合法化处理
                    f.write(img.content)  # 保存图片
                print("Finish")
            time.sleep(4)

        # 拉取缩略图
        # pic_dl = soup.find_all("img", class_="_thumbnail ui-scroll-view", limit=self.get_number)
        # i = 0  # 命名需要
        # for j in pic_dl:
        #     pic_dl_url = j["data-src"]
        #     print(pic_dl_url)  # 缩略图的url
        #     img = requests.get(pic_dl_url, headers=src_headers)  # 下载图片
        #     with open('D:\\Software\\pythonload\\' + title[i].text + '.jpg', 'wb') as f:  # 图片要用b,对text要合法化处理
        #         f.write(img.content)  # 保存图片
        #     i += 1
        # print("Read.")


if __name__ == '__main__':
    pixiv = Pixiv()
    pixiv.login()
    print("Loggin")
    pixiv.secontect()
    print("Get page content")
    pixiv.beautifulsoup()
