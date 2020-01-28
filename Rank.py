import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import re

se = requests.Session()  # 模拟登陆
requests.adapters.DEFAULT_RETRIES = 15
se.mount('http://', HTTPAdapter(max_retries=3))  # 重联
se.mount('https://', HTTPAdapter(max_retries=3))


class Pixiv(object):

    def __init__(self):
        self.base_url = 'https://accounts.pixiv.net/login?return_to=https%3A%2F%2Fwww.pixiv.net%2F&lang=zh&source=pc&view_type=page'
        self.login_url = 'https://accounts.pixiv.net/api/login?lang=zh'
        self.target_url_1 = 'https://www.pixiv.net/ranking.php?mode='
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
        self.modebase = {
            '1': 'daily',
            '2': 'weekly',
            '3': 'monthly',
            'R1': 'daily_r18',
            'R2': 'weekly_r18',
            'RG': 'r18g',
        }
        self.proxies = {
            'https': 'https://127.0.0.1:1080',
            'http': 'http://127.0.0.1:1080'
        }
        self.pixiv_id = '835437423@qq.com',  # 2664504212@qq.com
        self.password = '3616807',  # knxy0616
        self.post_key = []
        self.return_to = 'https://www.pixiv.net/'
        self.load_path = 'D:\Software\pythonload\pixiv_pic\\'  # 存放图片路径
        self.get_number = 5

    def login(self):
        # 登录部分由于有谷歌人机检测，暂时无法使用
        pass

    def validateTitle(self, title):
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        new_title = re.sub(rstr, "_", title)  # 替换为下划线
        return new_title

    def rank(self):
        s = se.get(self.target_url_1 + self.modebase['1'],
                   proxies=self.proxies)  # https://www.pixiv.net/setting_user.php
        with open(self.load_path + 'Re.html', 'w', encoding='utf-8') as f:
            f.write(s.text)

    def getthumbnail(self):
        soup = BeautifulSoup(open(self.load_path + 'Re.html', 'r', encoding='utf-8'), features="html.parser")  # 初始化
        pic_dl = soup.find_all("img", class_="_thumbnail ui-scroll-view", limit=self.get_number)
        i = 0  # 命名需要
        # with open(self.load_path + 'Re_soup.html', 'w', encoding='utf-8') as f:
        #     f.write(soup.prettify())  # 保存soup以便check
        title = soup.find_all("a", class_="title", limit=self.get_number)  # 寻找每周前get_number
        src_headers = self.headers
        for j in pic_dl:
            pic_dl_url = j["data-src"]
            # print(pic_dl_url)  # 缩略图的url
            img = requests.get(pic_dl_url, headers=src_headers)  # 下载图片
            with open(self.load_path + title[i].text + '.jpg', 'wb') as f:  # 图片要用b,对text要合法化处理
                f.write(img.content)  # 保存图片
            i += 1

    def getoriginal(self):
        soup = BeautifulSoup(open(self.load_path + 'Re.html', 'r', encoding='utf-8'), features="html.parser")  # 初始化
        adapt_url = 'https://pixiv.cat/'  # 利用反向代理接口获得图片
        title = soup.find_all("a", class_="title", limit=self.get_number)  # 寻找每周前get_number
        pic_dl = soup.find_all("img", class_="_thumbnail ui-scroll-view", limit=self.get_number)
        j = 0
        for i in title:
            name = self.validateTitle(i.string)
            img = requests.get(adapt_url + pic_dl[j]["data-id"] + '.jpg')
            if (img.status_code == 200):
                print(img.url)
                with open(self.load_path + name + '.jpg', 'wb') as f:  # 图片要用b,对text要合法化处理
                    f.write(img.content)  # 保存图片
            elif (img.status_code == 404):
                img = requests.get(adapt_url + pic_dl[j]["data-id"] + '-1.jpg')
                print(img.url)
                with open(self.load_path + name + '.jpg', 'wb') as f:  # 图片要用b,对text要合法化处理
                    f.write(img.content)  # 保存图片
            j += 1


if __name__ == '__main__':
    pixiv = Pixiv()
    print("Initializing...")
    pixiv.rank()
    # pixiv.getthumbnail() # 获取缩略图
    pixiv.getoriginal()  # 获取原图
