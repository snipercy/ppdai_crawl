# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib2
import socket
import requests
import re

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


def unique(items):
    keep = []
    for item in items:
        if item not in keep:
            keep.append(item)
    return keep


def do_request(url):
    # print url
    while True:
        try:
            # req = urllib2.Request(url)
            # req.add_header('User-Agent',
            #                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36')
            # res = urllib2.urlopen(req)
            # return res.read()
            # r = requests.get(url, request_params)
            r = requests.get(url, request_params)
            # print r.status_code
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
    sub_div = div.find('div', 'item w260')
    ret_info.append(div.text)

    # 投标数
    a = soup.find_all(name='a', class_='listname')
    ret_info.append(str(len(a)))


    # 信用等级
    span = soup.find(name='span', title='魔镜等级：AAA至F等级依次降低，等级越高逾期率越低。点击等级了解更多。')
    # haha
    ret_info.append(span['class'][1])
    return ret_info


def output_to_file(file, info):
    for item in info:
        file.write(item.encode('utf-8').replace('\n', '').replace('\r', '').replace(' ', '') + ", ")
    file.write('\n')


def main():
    # Open data file in append mode
    # if len(sys.argv) < 2:
    # print ("Please specify output file name")
    # return
    # file_name = sys.argv[1]
    file_name = "res.txt"
    data_file = open(file_name, 'a')
    user_url_list = []

    s_len = len(start_url_list)
    for i in range(s_len):
        start_url = start_url_list[i]
        for page in range(page_range[i][0], page_range[i][1]):
            # print page
            page_url = start_url + "_s0_p" + str(page)
            ret_user = parse_load_list_page(page_url)
            # print 'ret_user:', ret_user[0]
            user_url_list = user_url_list + ret_user
            # print ('Parsing page: ' + page_url + '......')
            # res = parse_load_list_page(page_url)
            # if len(res) == 0:
            # 	break
            # for item in res:
            # 	info = parse_load_single_page(item)
            # 	if info[9].find('100%') != -1:
            # 		output_to_file(data_file, info)
            # 	handled_page_url.append(item)
            # print ('Finish page: ' + page_url)
            # page = page + 1

    # Remove duplicated user urls
    user_url_list = unique(user_url_list)

    out = open('list.txt', 'a')

    for item in user_url_list:
        #print ('Parsing user: ' + item)
        info_list = parse_user_page(item)
        for info in info_list:
            output_to_file(data_file, info)
        print (str(len(info_list)) + " items added")


def add1():
    socket.setdefaulttimeout(10)
    data_file = open('res13.txt', 'a')

    # get user_url_list from links
    links = ['http://www.ppdai.com/list/%d' % i for i in range(4627000,4629000)]
    for url in links:
        print url
        # link = get_user_id(url)
        try:
            r = requests.get(url)
            # print r.status_code
            if r.status_code != 200:
                print ("Http request error: " + str(r.status_code) + " ---- " + url)
                continue

            soup = BeautifulSoup(r.content, "lxml")
            a = soup.find(name='input', id='usernameHidden')
            item = 'http://www.ppdai.com/user/' + a['value']

            # print ('Parsing user: ' + item)
            info_list = parse_user_page(item)
            for info in info_list:
                output_to_file(data_file, info)
            print (str(len(info_list)) + " items added")
            # return re.find(pattern, r.content)
        except:
            print 'error'
            pass

def add_mutil(_from,_to,file_name,thread_id):
    socket.setdefaulttimeout(10)
    data_file = open(file_name, 'a')

    print thread_id
    # get user_url_list from links
    links = ['http://www.ppdai.com/list/%d' % i for i in range(_from,_to)]
    for url in links:
        print url
        # link = get_user_id(url)
        try:
            r = requests.get(url)
            # print r.status_code
            if r.status_code != 200:
                print ("Http request error: " + str(r.status_code) + " ---- " + url)
                continue

            soup = BeautifulSoup(r.content, "lxml")
            a = soup.find(name='input', id='usernameHidden')
            item = 'http://www.ppdai.com/user/' + a['value']

            # print ('Parsing user: ' + item)
            info_list = parse_user_page(item)
            for info in info_list:
                output_to_file(data_file, info)
            print (str(len(info_list)) + " items added")
            # return re.find(pattern, r.content)
        except:
            print 'error'
            pass

import threading
from multiprocessing import Process

# mutil processes
def mutil_proc():
    #thread.start_new_thread(add_mutil(self, 4301006, 43020000, 'res6.txt'))
    #thread.start_new_thread(add_mutil(self, 4302001, 43030000, 'res7.txt'))
    #thread.start_new_thread(add_mutil(self, 4303001, 43040000, 'res7.txt'))
    #t1 = thread.start_new_thread(add_mutil,(43030001, 43030013, 'restest1.txt'))
    #t2 = thread.start_new_thread(add_mutil,(43040001, 43040013, 'restest2.txt'))

    # p1 = Process(target=add_mutil,args=(4540001, 4541000, 'res2.txt'))
    # p2 = Process(target=add_mutil,args=(4541001, 4545000, 'res3.txt'))
    # p3 = Process(target=add_mutil,args=(4545001, 4547000, 'res4.txt'))
    p4 = Process(target=add_mutil,args=(3548101, 3549999, 'res5.txt'))
    p5 = Process(target=add_mutil,args=(3030452, 3132000, 'res6.txt'))
    p6 = Process(target=add_mutil,args=(3132101, 3133000, 'res7.txt'))
    p7 = Process(target=add_mutil,args=(3133101, 3134000, 'res8.txt'))
    p8 = Process(target=add_mutil,args=(3134101, 3135000, 'res9.txt'))

    #p1.start()
    #p2.start()
    #p3.start()
    p4.start()
    p5.start()
    p6.start()
    p7.start()
    p8.start()

    #p1.join()
    #p2.join()
    #p3.join()
    p4.join()
    p5.join()
    p6.join()
    p7.join()
    p8.join()

    print "Exiting Main procecss"

# mutil threads
def mutil_t():
    t1 = threading.Thread(target=add_mutil, args=(3450361,3541000,'res5.txt', 't1'))
    t2 = threading.Thread(target=add_mutil, args=(3451422,3542000,'res6.txt', 't2'))
    t3 = threading.Thread(target=add_mutil, args=(3453211,3544000,'res7.txt', 't3'))
    t4 = threading.Thread(target=add_mutil, args=(3454511,3545000,'res8.txt', 't4'))
    t5 = threading.Thread(target=add_mutil, args=(3455761,3549000,'res9.txt', 't5'))

    t = [t1,t2,t3,t4,t5]
    for i in t:
        i.start()

    for i in t:
        i.join()
        print '--------done'

if __name__ == '__main__':
    # file_name = "res.txt"
    # data_file = open(file_name, 'w')
    # info_list = parse_user_page('http://www.ppdai.com/user/shiyang696')
    # for info in info_list:
    #     output_to_file(data_file, info)
    # print (str(len(info_list)) + " items added")
    # main()
    # add1()
    # mutil_proc()
    # mutil_t()
    add1()
