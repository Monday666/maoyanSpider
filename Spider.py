import requests
from bs4 import BeautifulSoup
import re
import csv


def Gethtml(url):
    """
    使用浏览器模拟的方式获取网页源码
    :param url: 网页URL地址
    :return:html
    """
    # 将cookies字符串组装为字典
    cookies_str = '__mta=208903469.1537876239606.1537966087518.1537966271718.11; uuid_n_v=v1; uuid=3851AE40C0B911E895764F985E386DE202DFFDFED118403EB9BA5E7A9C9D6698; _lxsdk_cuid=16610912361c8-07a50566ed1d0e-8383268-1fa400-16610912362c8; _lxsdk=3851AE40C0B911E895764F985E386DE202DFFDFED118403EB9BA5E7A9C9D6698; _csrf=33645a5e9922420ef22609cd9965dd58afac2d82a9caca9afd817c97d4a41563; _lx_utm=utm_source%3Dmeituanweb; __mta=208903469.1537876239606.1537964122287.1537964124676.6; _lxsdk_s=16615ccbec7-4dc-ef6-e2a%7C%7C20'
    cookies_dict = {}
    for cookie in cookies_str.split(";"):
        k, v = cookie.split("=", 1)
        cookies_dict[k.strip()] = v.strip()

    # 其他请求头参数
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

    # 访问页面
    page = requests.get(url=url, cookies=cookies_dict, headers=headers)

    # 返回页面HTML
    return page.text


def FindMovie(sp):
    """
    截取各部电影的所在标签返回列表，每个值是一部电影所在整个标签里的内容

    """
    movie = sp.find_all('div', attrs={'class': re.compile(r"show-list(\s\w+)?")})
    return movie


def FindPage(sp):
    """
    寻找并截取每个日期的界面
    :param sp:
    :return:
    """
    page = sp.find_all('div', attrs={'class': re.compile(r"plist-container(\s\w+)?")})
    return page


def FindName(sp):
    """
    找到电影名
    :param sp:soup
    :return:str name
    """
    name = sp.find('h3', class_='movie-name')
    return name.text


def FindDate(sp):
    """
    找到日期
    :param sp:
    :return:
    """
    lsdate = sp.find_all('span', attrs={'class': re.compile(r"date-item(\s\w+)?")})
    data = []
    for l in lsdate:
        data.append(l.text)
    return data


def FindTime(sp):
    """
    找到时间
    :param sp:
    :return:
    """
    time = []
    page = FindPage(sp)
    for i in range(len(page)):
         lstime = page[i].find_all('span', attrs={'class': 'begin-time'})
         timei = []
         if lstime == []:
             timei.append("无场次")
         else:
             for l in lstime:
                 timei.append(l.text)
         time.append(timei)
    return time


def FindPrice(sp):
    """
    找到价格
    :param sp:
    :return:
    """

    lsprice = sp.find('span', class_='value text-ellipsis', text=re.compile(r"(.\d+.\d.)张"))
    return lsprice.text


def FindPeople(sp):
    """
    找到人数，返回已售票，和未售票
    :param sp:
    :return:
    """
    Npeople = sp.find_all('span', class_='seat selectable')
    Hpeople = sp.find_all('span', class_='seat sold')
    return Npeople, Hpeople


def ReturnPrice(sp):
    """
    到价格界面找到价格并返回价格值
    :param sp:
    :return:
    """
    page = FindPage(sp)
    server = "http://maoyan.com"
    price = []

    for i in range(len(page)):
        pricei = []
        Url = []
        a = page[i].find_all('a', attrs={'class': 'buy-btn normal'})
        if a == []:
            pricei.append('无')
        else:
            for each in a:
                Url.append(server + each.get('href'))
            for j in Url:
                pricei.append(FindPrice(BeautifulSoup(Gethtml(j), 'html.parser')))
        price.append(pricei)
    return price


def ReturnPN(sp):
    """
    到人数界面找到人数并返回已售票之和未售票值
    :param sp:
    :return:
    """
    peopleN = []
    page = FindPage(sp)
    server = "http://maoyan.com"
    for i in range(len(page)):
        Url = []
        peopleNi = []
        a = page[i].find_all('a', attrs={'class': 'buy-btn normal'})
        if a == []:
            peopleNi.append('无')
        else:
            for each in a:
                Url.append(server + each.get('href'))
            for j in Url:
                people = FindPeople(BeautifulSoup(Gethtml(j), 'html.parser'))
                Npeople, Hpeople = people
                peopleNi.append("已售出：" + str(len(Hpeople)) + "剩余票数：" + str(len(Npeople)))
        peopleN.append(peopleNi)
    return peopleN


# 获取网页源码
URL = "http://maoyan.com/cinema/2714?poi=2367020"
sp1 = BeautifulSoup(Gethtml(URL), 'html.parser')
movie = FindMovie(sp1)
name = []
data = []
time = []
price = []
peopleN = []

# 获取数据
for i in range(len(movie)):
    name.append(FindName(movie[i]))
    data.append(FindDate(movie[i]))
    time.append(FindTime(movie[i]))
    price.append(ReturnPrice(movie[i]))
    peopleN.append(ReturnPN(movie[i]))


# 整合数据
info = []
for i in range(len(movie)):
        for j in range(len(data[i])):
                for k in range(len(time[i][j])):
                    infok = [name[i], data[i][j], time[i][j][k], price[i][j][k], peopleN[i][j][k]]
                    info.append(infok)


#存储数据
with open('myinfo.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['电影名', '日期', '时间', '票价', '余票'])
    for i in range(len(info)):
        csvwriter.writerow(info[i])
