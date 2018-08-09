# -*- coding:UTF-8 -*-
import socket
from bs4 import BeautifulSoup
import requests
import random
from DragonMaoMaoSpider.anticrawl.user_agents import agents
from DragonMaoMaoSpider.dao.redisdb import redis_cli

http_key = 'proxy:http'
https_key = 'proxy:https'

class proxy(object):
    def __init__(self):
        self.num = 10
        self.header = {'Upgrade-Insecure-Requests': '1',
                          'User-Agent': random.choice(agents),
                          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                          'Referer': 'http://www.xicidaili.com/nn/',
                          'Accept-Encoding': 'gzip, deflate, sdch',
                          'Accept-Language': 'zh-CN,zh;q=0.8',}

    #http or https
    def get_proxy(self, key):
        if redis_cli.scard(key) <  self.num/3:
            self.crawl_proxy(key)

        ip = redis_cli.srandmember(key).decode('utf8')
        while not self.check_proxy(ip):
            redis_cli.srem(key, ip)
            print('delte %s://%s' %(key, ip))
            ip = redis_cli.srandmember(key).decode('utf8')

        if key == http_key:
            return 'http://%s' % ip
        elif key == https_key:
            return 'https://%s' % ip

    #timout is useful even though its take crawl more time
    def check_proxy(self, ip):
        li = ip.split(':')
        try:
            sock = socket.create_connection((li[0], li[1]), 5)
            sock.close()
            return True
        except:
            return False

    #crawl http or https, and store set in redis
    def crawl_proxy(self, key):
        print('crawl %s proxy begin' % key)
        n = redis_cli.scard(key)
        page = 1
        while 1:
            url = 'http://www.xicidaili.com/nn/%d' % page
            html = requests.get(url, headers=self.header).content
            soup = BeautifulSoup(html, 'lxml')
            ip_list = soup.find(id='ip_list')
            for odd in ip_list.find_all(class_='odd'):
                protocol = odd.find_all('td')[5].get_text().lower()
                if key == http_key and protocol != 'http':
                    continue
                if key == https_key and protocol != 'https':
                    continue
                ip = ':'.join([x.get_text() for x in odd.find_all('td')[1:3]])
                if redis_cli.sismember(key,ip):
                    continue
                if self.check_proxy(ip):
                    #print('sucess:', ip)
                    redis_cli.sadd(key, ip)
                    n += 1
                #else:
                    #print('fail:', ip)
                if n >= self.num:
                    print('crawl %s proxy end' % key)
                    return
            page += 1

#singleton
proxy = proxy()

if __name__ == '__main__':
    print(proxy.get_proxy(http_key))
    print(proxy.get_proxy(https_key))