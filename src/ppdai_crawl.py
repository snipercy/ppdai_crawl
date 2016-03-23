# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import socket
import requests

socket.setdefaulttimeout(10)

start_url_list = ["http://invest.ppdai.com/loan/list_safe", 'http://invest.ppdai.com/loan/list_payfor',
                  'http://invest.ppdai.com/loan/list_riskmiddle',
                  'http://invest.ppdai.com/loan/list_riskhigh']
# start_url_list = ["http://invest.ppdai.com/loan/list_payfor"]
page_range = [(1, 2), (1, 2), (1, 2)]

request_params = {'Connection': 'keep-alive',
                  'Cache-Control': 'max-age=0',
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36',
                  'Accept-Encoding': 'gzip, deflate, sdch',
                  'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4'
                  }


# 用于去除重复的地址
def unique(items):
    keep = []
    for item in items:
        if item not in keep:
            keep.append(item)
    return keep

# 发送链接请求
def do_request(url):
    while True:
        try:
            r = requests.get(url, request_params)
            if r.status_code != 200:
                print ("Http request error: " + str(r.status_code) + " ---- " + url)
                return ""
            return r.content
        except Exception:
            continue


def parse_load_list_page(url):
    # print url
    html_content = do_request(url)
    if html_content == "":
        print 'no content'
        return []
    soup = BeautifulSoup(html_content, 'lxml')
    ret = []

    p = soup.find_all(name='p', class_='userInfo clearfix')
    for item in p:
        ret.append(item.find(name='a')['href'])

    return ret


def parse_user_page(url):

    html_content = do_request(url)
    if html_content == "":
        return []
    soup = BeautifulSoup(html_content, "lxml")
    ret_info = []
    user_info = []

    # Get user information
    li = soup.find(name='li', class_='honor_li')
    span = li.find_all(name='span', class_='cf7971a')
    for item in span:
        user_info.append(item.text)

    li = soup.find(name='li', class_='user_li')
    span = li.find_all(name='span')
    user_info.append(span[0].text)

    # Get load urls
    div = soup.find_all(name='div', class_='rightlist fl')
    for items in div:
        if items.text.find('100%') == -1:
            continue
        host = 'http://www.ppdai.com'
        s_url = host + items.find(name='a')['href']
        ret_info.append(parse_load_single_page(s_url, user_info))

    return ret_info


def parse_load_single_page(url, info):
    html_content = do_request(url)
    if html_content == "":
        return []
    soup = BeautifulSoup(html_content, "lxml")
    ret_info = []

    # 借款总额，年利率，期限
    div = soup.find(name='div', class_='newLendDetailInfo clearfix')
    dd = div.find_all(name='dd')
    for item in dd:
        item.text.encode('utf-8')
        ret_info.append(item.text)

    # 还款方式
    # div = soup.find_all(name='div', class_='item item1')
    div = soup.find('div', 'item w260')
    content = div.text.strip()
    ret_info.append(content)

    # 借入信用等级，借出信息等级，性别
    ret_info = ret_info + info

    # 历史成功次数，历史流标次数
    div = soup.find('div', 'newLendDetailInfoLeft')
    # p = div.find('p')
    span = div.find('span', 'bidinfo')
    content = span.text.strip().split(u'｜')
    ret_info.append(content[0])
    ret_info.append(content[1])

    # 借款进度
    div = soup.find('div', 'part clearfix')
    ret_info.append(div.text)

    # 投标数
    a = soup.find_all(name='a', class_='listname')
    ret_info.append(str(len(a)))


    # 信用等级
    span = soup.find(name='span', title='魔镜等级：AAA至F等级依次降低，等级越高逾期率越低。点击等级了解更多。')
    # haha
    ret_info.append(span['class'][1])
    return ret_info


# 写入指定文件
def output_to_file(file, info):
    for item in info:
        file.write(item.encode('utf-8').replace('\n', '').replace('\r', '').replace(' ', '') + ", ")
    file.write('\n')

def main():
    socket.setdefaulttimeout(10)
    data_file = open('res13.txt', 'a')

    # get user_url_list from links
    links = ['http://www.ppdai.com/list/%d' % i for i in range(4627000,4629000)]

    for url in links:
        print url
        try:
            r = requests.get(url)
            if r.status_code != 200:
                print ("Http request error: " + str(r.status_code) + " ---- " + url)
                continue

            soup = BeautifulSoup(r.content, "lxml")
            a = soup.find(name='input', id='usernameHidden')
            item = 'http://www.ppdai.com/user/' + a['value']

            info_list = parse_user_page(item)

            for info in info_list:
                output_to_file(data_file, info)

            print (str(len(info_list)) + " items added")

        except:
            print 'error'
            pass

if __name__ == '__main__':
    main()

