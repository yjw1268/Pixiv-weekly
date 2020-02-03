# -*- coding:utf-8 -*-
import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import re, time
import json
from multiprocessing import Pool
from configparser import ConfigParser


se = requests.Session()  # 模拟登陆
requests.adapters.DEFAULT_RETRIES = 15
se.mount('http://', HTTPAdapter(max_retries=3))  # 重联
se.mount('https://', HTTPAdapter(max_retries=3))
cp = ConfigParser()
cp.read('config.conf',encoding='utf-8')

class Pixiv():

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
            'RG': 'r18g'
        }
        self.mode=cp.get("rank","mode")
        self.proxies = {
            'https': 'https://127.0.0.1:1080',
            'http': 'http://127.0.0.1:1080'
        }
        self.pixiv_id = cp.get("rank", "pixiv_id"),  # 2664504212@qq.com
        self.password = cp.get("rank", "password"),  # knxy0616
        self.post_key = []
        self.return_to = 'https://www.pixiv.net/'
        self.load_path = cp.get("rank", "download_path")  # 存放图片路径
        self.get_number = int(cp.get("rank", "get_number"))

    def login(self):
        # 登录部分由于有谷歌人机检测，暂时无法使用
        pass

    def validateTitle(self, title):
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        new_title = re.sub(rstr, "_", title)  # 替换为下划线
        return new_title

    def rank(self):
        s = se.get(self.target_url_1 + self.modebase[self.mode],
                   proxies=self.proxies)  # 修改modebase改变排行榜类型
        # with open(self.load_path + 'Re.html', 'w', encoding='utf-8') as f:
        #     f.write(s.text)
        soup = BeautifulSoup(s.text, features="html.parser")  # 初始化
        # with open(self.load_path + 'Re_soup.html', 'w', encoding='utf-8') as f:
        #     f.write(soup.prettify())
        # soup = BeautifulSoup(open(self.load_path + 'Re.html', 'r', encoding='utf-8'), features="html.parser")  # 初始化
        return soup

    def getid(self, soup):
        item = soup.find_all("div", class_="ranking-image-item", limit=self.get_number)
        ids = []
        for i in item:
            ids.append(i.img["data-id"])
        return ids

    def getpagecount(self, soup):
        item = soup.find_all("div", class_="ranking-image-item", limit=self.get_number)
        types = []
        for i in item:
            try:
                types.append(int(i.find(class_="page-count").text))
            except:
                types.append(1)
        return types

    def getdetailurl(self, soup):
        item = soup.find_all("div", class_="ranking-image-item", limit=self.get_number)
        detail_url = []
        for i in item:
            detail_url.append(i.a["href"])
        return detail_url

    def gettitle(self, soup):
        item = soup.find_all("a", class_="title", limit=self.get_number)
        titles = []
        for i in item:
            name = self.validateTitle(i.string)
            titles.append(name)
        return titles

    def getthumbnailurl(self, soup):
        item = soup.find_all("div", class_="ranking-image-item", limit=self.get_number)
        urls = []
        for i in item:
            urls.append(i.img["data-src"])
        return urls

    def getuserid(self, soup):
        item = soup.find_all("div", class_="ranking-image-item", limit=self.get_number)
        users = []
        for i in item:
            users.append(i.img["data-user-id"])
        return users

    def gettag(self, soup):
        item = soup.find_all("div", class_="ranking-image-item", limit=self.get_number)
        tags = []
        for i in item:
            tags.append(i.img["data-tags"])
        return tags

    def getusername(self, soup):
        item = soup.find_all("a", class_="user-container ui-profile-popup", limit=self.get_number)
        names = []
        for i in item:
            names.append(i["data-user_name"])
        return names

    def getuseravatar(self, soup):
        item = soup.find_all("a", class_="user-container ui-profile-popup", limit=self.get_number)
        urls = []
        for i in item:
            urls.append(i["data-profile_img"])
        return urls

    def download(self, url, title):
        src_headers = self.headers
        # print(title+url)
        img = requests.get(url, headers=src_headers)  # 下载图片
        with open(self.load_path + title + '.jpg', 'wb') as f:
            f.write(img.content)  # 保存图片

    def downloadcomic(self, id, type, title):
        adapt_url = 'https://pixiv.cat/'  # 利用反向代理接口获得图片
        for j in range(type):
            url = adapt_url + id + '-' + str(j + 1) + '.jpg'
            src_headers = self.headers
            # print(title+url)
            img = requests.get(url, headers=src_headers)  # 下载图片
            with open(self.load_path + title + '-' + str(j + 1) + '.jpg', 'wb') as f:
                f.write(img.content)  # 保存图片

    def getdate(self, soup):
        item = soup.find("ul", class_="sibling-items")
        return item.a.string

    def setjson(self, soup):
        pages = self.getpagecount(soup)
        titles = self.gettitle(soup)
        detailurls = self.getdetailurl(soup)
        ids = self.getid(soup)
        tags = self.gettag(soup)
        userids = self.getuserid(soup)
        thumbnailurls = self.getthumbnailurl(soup)
        useravatars = self.getuseravatar(soup)
        usernames = self.getusername(soup)
        date = self.getdate(soup)
        result = [{'rankdate': date}, {'returnnumber': self.get_number}]
        for i in range(0, self.get_number):
            output = {
                'rank': i + 1,
                'title': titles[i],
                'id': ids[i],
                'thumbnailurl': thumbnailurls[i],
                'page': pages[i],
                'tag': tags[i],
                'userid': userids[i],
                'detailurl': detailurls[i],
                'username': usernames[i],
                'useravatar': useravatars[i],
            }
            result.append(output)
        result.append({'returntime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
        result = json.dumps(result)
        # print(result)
        return result

    def main(self):
        print("Initializing...")
        soup = self.rank()
        print("获取信息如下：\n"+self.setjson(soup))
        thumbnailurls = self.getthumbnailurl(soup)
        titles = self.gettitle(soup)
        ids = self.getid(soup)
        types = self.getpagecount(soup)
        # download_all_thumbnail(thumbnailurls,titles) # 多线程下载所有缩略图
        # download_thumbnail(thumbnailurls, titles)  # 单线程下载所有缩略图
        # download_original(ids, types, titles)  # 单线程下载原图
        download_all_original(ids, types, titles) #多线程下载原图
        print("Done.")


def download_all_thumbnail(url, title):  # 多线程下载所有缩略图,在一些IDLE可能无法使用，命令行可用
        p = Pool(8)
        for i in range(len(url)):
            print(url[i])
            p.apply_async(pixiv.download, args=(url[i],title[i]))
        p.close()
        p.join()
        print('done')


def download_thumbnail(url, title):  # 单线程下载缩略图
    for i in range(len(url)):
        pixiv.download(url[i], title[i])
    print('done')


def download_original(id, type, title):
    adapt_url = 'https://pixiv.cat/'  # 利用反向代理接口获得图片
    print("正在下载原图中...")
    for i in range(len(id)):
        if (type[i] > 1):
            pixiv.downloadcomic(id[i], type[i], title[i])
        elif (type[i] == 1):
            url = adapt_url + id[i] + '.jpg'
            pixiv.download(url, title[i])
        else:
            raise TypeError


def download_all_original(id, type, title):  # 多线程下载所有原图,在一些IDLE可能无法使用，命令行可用
    p = Pool(8)
    adapt_url = 'https://pixiv.cat/'  # 利用反向代理接口获得图片
    for i in range(len(id)):
        if (type[i] > 1):
            p.apply_async(pixiv.downloadcomic, args=(id[i], type[i], title[i]))
        elif (type[i] == 1):
            url = adapt_url + id[i] + '.jpg'
            p.apply_async(pixiv.download, args=(url, title[i]))
        else:
            raise TypeError
    p.close()
    p.join()
    print('done')


if __name__ == '__main__':
    pixiv = Pixiv()
    pixiv.main()
