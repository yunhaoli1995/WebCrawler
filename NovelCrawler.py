# -*- coding: UTF-8 -*-
import requests
import os
from bs4 import BeautifulSoup
import requests
import time
from threading import Thread
from queue import Queue
    
# headers中user-agent的作用是告诉服务器使用者是通过什么工具访问的
headers = {"User-Agent":"Mozilla/5.0 (Platform; Encryption; OS-or-CPU; Language) AppleWebKit/AppleWebKitVersion (KHTML, like Gecko) Chrome/ChromeVersion Safari/SafariVersionChrome 0.2"}
server = "https://www.bqktxt.com/" # 小说主站地址
target = "https://www.bqktxt.com/0_243/" # 目标小说地址        

def run_time(func):
    def wrapper(*args, **kw):
        start = time.time()
        func(*args, **kw)
        end = time.time()
        print('running', end-start, 's')
    return wrapper

class Spider():

    def __init__(self):
        self.qurl = Queue()
        self.data = list()
        self.thread_num = 32

    def produce_url(self, url_list):
        for url in url_list:
            self.qurl.put(url) # 生成URL存入队列，等待其他线程提取

    def get_info(self):
        # 让线程从队列中读取url以及对应参数
        while not self.qurl.empty(): # 保证url遍历结束后能退出线程
            url = self.qurl.get() # 从队列中获取URL
            req = requests.get(url['url'],headers=headers)
            req.encoding = 'gbk'     # 解决中文乱码问题
            html = req.text
            bf = BeautifulSoup(html,"html.parser")
            texts = bf.find_all("div",class_="showtxt")

            texts = texts[0].text.replace('\xa0'*8,'\n\n').replace('\u3000','')
            texts = texts.replace('(https://www.bqktxt.com/0_243/657851432.html)请记住本书首发域名：www.bqktxt.com。','')
            texts = texts.replace('笔趣阁手机版阅读网址：m.bqktxt.com','')
            texts = '。\n'.join(texts.split('。'))

            result = {
                'title': '第{}章 {}'.format(str(url['count']),url['name'].split()[-1]),
                'text': texts
            }

            f = open('小说2/'+result['title'],'w')
            f.writelines(result['title']+'\n\n')
            f.writelines(result['text'])
            f.close()

            self.data.append(result)

    @run_time
    def run(self,url_list):
        # 定义每个线程的行为
        self.produce_url(url_list)

        ths = []
        for _ in range(self.thread_num):
            th = Thread(target=self.get_info)
            th.start()
            ths.append(th)
            
        for th in ths:
            th.join()

        for d in self.data:
            print(d['title'])

        print('Data crawling is finished.')

def get_url():
    # 先爬取url列表
    web = []
    req = requests.get(target,headers=headers)
    req.encoding = 'gbk' # 解决中文乱码问题
    html = req.text
    bf = BeautifulSoup(html,"html.parser")
    texts = bf.find_all("div",class_="listmain")
    a_bf = BeautifulSoup(str(texts[0]),"html.parser")
    aa = a_bf.find_all('a')

    flag = False
    count = 1
    for item in aa:
        
        it_url = item.get('href')
        it_name = item.string

        if flag or "第一章" in it_name:
            if '第' in it_name:
                web.append({
                    'url': server+it_url, 
                    'name': it_name, 
                    'count': count,
                })
                count+=1
                flag = True

    return web

if __name__ == "__main__":

    url_list = get_url()
    Spider().run(url_list)