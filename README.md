# Pixiv-weekly
### 注意：2019.12 Pixiv登录引入谷歌人机验证reCAPTCHA，通过用户登陆获取原图方法失效，缩略图仍可以获取，原图改为通过pixiv.cat获取。
## 简介
一个简单的Python后端爬虫，有爬取pixiv的排行榜和搜索等功能，能获取缩略图、压缩图和原画并保存到本地。
## 依赖外部库
* requests
* BeautifulSoup
## 使用
首先，你的电脑得能访问到[Pixiv社区](https://www.pixiv.net)（翻墙什么的方法都有啦）。如果是部署在服务器上，可以参考这个[demo](https://github.com/yjw1268/Web-learning/tree/Try/SQL/pythonload)。  
- 打开config.conf文件，修改load_path等后直接运行rank.py主函数按提示步骤即可按需获取当日排行榜图片。可以设置日排行，周排行，月排行及获取数目等等。  
- 打开search.py文件，修改self.pixiv_id，self.password，self.load_path后直接运行主函数按提示步骤搜索关键词图片，并按star数目从高到低获取。
- 保存的图片都在self.load_path路径中。 

出于减轻目标服务器压力等原因，目前程序较为简易，限制较多，可按需修改限制数目（如爬取页数，获取图片数等）。
