#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import time
import sys
import re
import pymysql

se = requests.Session()  # 模拟登陆
requests.adapters.DEFAULT_RETRIES = 15
se.mount('http://', HTTPAdapter(max_retries=3))  # 重联
se.mount('https://', HTTPAdapter(max_retries=3))


class Pixiv(object):

    def __init__(self):
        self.base_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
        self.login_url = 'https://accounts.pixiv.net/api/login?lang=zh'
        self.modebase = {
            '1': 'daily',
            '2': 'weekly',
            '3': 'monthly',
            'R1': 'daily_r18',
            'R2': 'weekly_r18',
            'RG': 'r18g',
        }
        self.target_url_1 = 'https://www.pixiv.net/ranking.php?mode='
        self.main_url = 'https://www.pixiv.net'
        self.headers = {
            'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                          ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
        }
        self.pixiv_id = '835437423@qq.com',  # 2664504212@qq.com
        self.password = 'yjw3616807',  # knxy0616
        self.post_key = []
        self.return_to = 'https://www.pixiv.net/'
        self.load_path = './rank_pic/'  # 存放图片路径

    def login(self):
        post_key_xml = se.get(self.base_url, headers=self.headers).text
        post_key_soup = BeautifulSoup(post_key_xml, 'lxml')
        self.post_key = post_key_soup.find('input')['value']
        data = {
            'pixiv_id': self.pixiv_id,
            'password': self.password,
            'post_key': self.post_key,
            'return_to': self.return_to
        }
        se.post(self.login_url, data=data, headers=self.headers)

    def choosemode(self):
        text = str(sys.argv[1])
        mode = self.modebase[text]
        # print(mode)
        return mode

    def getnum(self, mode):
        if mode == 'daily_r18' or mode == 'weekly_r18':
            # print("?")
            getnumber = str(sys.argv[2])
            if (getnumber.isdigit()):
                if int(getnumber) > 5 or int(getnumber) < 1:
                    # print("-1")
                    sys.exit()
            elif (getnumber == ''):
                getnumber = 3
            else:
                # print("-1")
                sys.exit()
        elif mode == 'r18g':
            # print("!")
            getnumber = 1
        else:
            getnumber = str(sys.argv[2])
            if (getnumber.isdigit()):
                if int(getnumber) > 5 or int(getnumber) < 1:
                    # print("-1")
                    sys.exit()
            elif (getnumber == ''):
                getnumber = 5
            else:
                # print("-1")
                sys.exit()
        return int(getnumber)

    def validateTitle(self, title):
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        new_title = re.sub(rstr, "_", title)  # 替换为下划线
        return new_title

    def beautifulsoup(self, get_number, target_url):
        s = se.get(self.target_url_1 + str(target_url))
        soup = BeautifulSoup(s.text, features="html.parser")  # 初始化
        # 数据库操作
        db = pymysql.connect("localhost", "root", "psd", "Study")
        cursor = db.cursor()
        # 图片处理
        pic_dl = soup.find_all("img", class_="_thumbnail ui-scroll-view", limit=get_number)
        title = soup.find_all("a", class_="title", limit=get_number)
        i = 0
        for j in pic_dl:
            pic_dl_url = j["data-src"]  # 缩略图的url
            pic_id = j["data-id"]  # 图片id
            img = requests.get(pic_dl_url, headers=self.headers)  # 下载图片
            # 命名格式：mode_date_number.jpg
            dlname = str(target_url) + '_' + time.strftime("%Y-%m-%d", time.localtime()) + '_' + str(i) + '.jpg'
            with open(self.load_path + dlname, 'wb') as f:  # 图片要用wb,对text要合法化处理
                f.write(img.content)  # 保存图片
            # 获取原图url
            temp_url = self.main_url + '/' + title[i]['href']
            temp_clear = se.get(temp_url, headers=self.headers)
            clear_soup = BeautifulSoup(temp_clear.text, features="html.parser")
            name = self.validateTitle(title[i].text)  # 图片名称
            op = clear_soup.prettify().find('"original":"')
            ed = clear_soup.prettify().find('},"tags')
            original_url = clear_soup.prettify()[op + 12:ed - 1]
            adapt_url = original_url.replace('\/', '/')
            local_url = 'http://study.imoe.club/Try/rank_pic/' + dlname
            # print(local_url)
            # print("<br>")
            sql = "INSERT INTO pixiv_rank(raw_url, pixiv_id,original_url,local_url,title, love) VALUES ('%s', '%s','%s','%s','%s', '%s')" % \
                  (str(pic_dl_url), pic_id, str(adapt_url), str(local_url), name, 0)
            # 执行sql语句
            cursor.execute(sql)
            db.commit()
            i += 1
        db.close()


if __name__ == '__main__':
    pixiv = Pixiv()
    pixiv.login()
    mode = pixiv.choosemode()
    pixiv.beautifulsoup(pixiv.getnum(mode), mode)
    print("System Exit")
