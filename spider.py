# -*- coding = utf-8 -*-
# @Time : 2020/11/11 15:19
# @Author : DJT
# @File : spider.py
# @Software : PyCharm

from bs4 import BeautifulSoup  # 网页解析，获取数据
import re  # 正则表达式
import urllib.request  # 获取网页数据
import sqlite3  # 进行SQL数据库操作
import random
import time
import sys

# 伪造header
headers2 = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0"},
    {"User-Agent": "Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50"},
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"},
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1"},
    {
        "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)"},
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201"},
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"},
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"
    }
]

# 代理ip
proxy_ip_list = [
    {"https": "60.191.11.251:3128"},
    {"https": "59.36.10.79:3128"},
    {"https": "58.220.95.32:10174"},
]


# 爬取url
# url = "https://y.qq.com/"


# 随机UserAgent
def random_ua():
    return random.choice(headers)


# 随机代理ip
def random_ip():
    ranIP = random.choice(proxy_ip_list)
    print(ranIP)
    return ranIP


# 正则
findImgSrc = re.compile(r'<img src="(.*?)"', re.S)
findLink = re.compile(r'<a href="(.*?)"')


# 时间
def get_datetime():
    return time.strftime("%Y-%m-%d", time.localtime())


# 获取网页
def getWebData(url, save_html_path):
    request = urllib.request.Request(url, headers=random_ua())
    proxy_handler = urllib.request.ProxyHandler(random_ip())
    opener = urllib.request.build_opener(proxy_handler)
    try:
        response = opener.open(request, timeout=5).read().decode("utf-8")
        # print(response)
        # 写入html文件
        with open(save_html_path, "w", encoding="utf-8") as f:
            f.write(response)
            f.close()
    except Exception as e:
        print(e)


# 解析数据
def analysisFile(datetime):
    News = []
    file = open("./MusicNews/MusicNews%s.html" % datetime, "rb")
    html = file.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    li_list = soup.select("div > div > div > ul > li")
    for item in li_list:
        i = item
        item = str(item)
        try:
            # 标题
            for title in i.find_all("div", class_="titname"):
                data = [str(title.text).strip()]
            # 图片
            img = re.findall(findImgSrc, item)
            if len(img) == 1:
                data.append(str(img).replace("[", "").replace("]", "").replace("'", ''))
                News.append(data)
            # 信息
            for info in i.find_all("div", class_="introduce"):
                data.append(str(info.text).strip())
            # 时间
            for newsTime in i.find_all("span", id="time"):
                data.append(str(newsTime.text).strip())
            # 链接
            for linkList in i.find_all("div", class_="img"):
                linkList = str(linkList)
                link = re.findall(findLink, linkList)
                data.append(str(link).replace('[', "").replace("]", "").replace("'", ""))
        except Exception as e:
            print(e, sys._getframe().f_lineno)
            break
    print(News)
    if len(News) > 0:
        print("解析成功")
        saveDB(News, "./MusicNews.db")
    else:
        print('失败')


# 储存数据
def saveDB(datalist, db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for data in datalist:
        for index in range(len(data)):
            data[index] = '"' + data[index] + '"'
        sql = '''
                insert into MusicNews(title,picUrl,info,newTime,link)
                values(%s)''' % ",".join(data)
        try:
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            print("存储异常" + str(e))
    cur.close()
    conn.close()


# 初始化数据库
def init_db(db_path):
    sql = '''
    create table MusicNews(
    id integer primary key autoincrement,
    title text,
    picUrl text,
    info text,
    newTime text,
    link text
    )
    '''
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("drop table MusicNews")
    except Exception as e:
        print(e)

    cur.execute(sql)
    conn.commit()
    conn.close()


def getMusicNews():
    datalist = []
    conn = sqlite3.connect(r"C:\Users\DJT\Desktop\flaskProject\SpiderMusicNews\MusicNews.db")
    cur = conn.cursor()
    sql = "select title,picUrl,info,newTime,link from MusicNews"
    data = cur.execute(sql)
    for item in data:
        datalist.append(item)
    cur.close()
    conn.close()
    return datalist


if __name__ == "__main__":
    init_db("./MusicNews.db")
    getWebData("http://news.yule.com.cn/music/", "./MusicNews/MusicNews%s.html" % get_datetime())
    analysisFile(get_datetime())
    getMusicNews()
