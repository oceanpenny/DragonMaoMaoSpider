# -*- coding:UTF-8 -*-
import socket
from bs4 import BeautifulSoup
import requests
import random
from DragonMaoMaoSpider.anticrawl.user_agents import agents
from DragonMaoMaoSpider.dao.redisdb import redis_cli
import logging

#redis_key where we store http/https proxies
http_key = 'proxy:http'
https_key = 'proxy:https'
logger = logging.getLogger(__name__)

class proxy(object):
    def __init__(self):
        self.pool_size = 15
        self.header = {'Upgrade-Insecure-Requests': '1',
                          'User-Agent': random.choice(agents),
                          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                          'Referer': 'http://www.xicidaili.com/nn/',
                          'Accept-Encoding': 'gzip, deflate, sdch',
                          'Accept-Language': 'zh-CN,zh;q=0.8',}

    #http or https, update when pool_size < threshold or pool_size==0
    def get_proxy(self, key, update=True):
        try:
            if (update and redis_cli.scard(key) < self.pool_size / 3) or redis_cli.scard(key) == 0:
                self.crawl_proxy(key)

            ip = redis_cli.srandmember(key).decode('utf8')
            while not self.check_proxy(ip):
                self.delete_proxy(key, ip)
                ip = redis_cli.srandmember(key).decode('utf8')

            if key == http_key:
                return 'http://%s' % ip
            elif key == https_key:
                return 'https://%s' % ip
        except Exception as e:
            logger.error('get proxy failed, reason:%s' % e)
            return  None

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
        logger.info('crawl %s proxy begin' % key)
        page = 1
        while 1:
            url = 'http://www.xicidaili.com/nn/%d' % page
            self.pares(url, key)
            if redis_cli.scard(key) >= self.pool_size:
                logger.info('crawl %s proxy end' % key)
                return
            page += 1

    #pares html and if failed try proxies, default = None
    def pares(self, url, key, proxies=None):
        try:
            html = requests.get(url, headers=self.header, proxies=proxies).content
            soup = BeautifulSoup(html, 'lxml')
            ip_list = soup.find(id='ip_list')
            if not ip_list:
                raise ValueError
            for odd in ip_list.find_all(class_='odd'):
                protocol = odd.find_all('td')[5].get_text().lower()
                if key == http_key and protocol != 'http':
                    continue
                if key == https_key and protocol != 'https':
                    continue
                ip = ':'.join([x.get_text() for x in odd.find_all('td')[1:3]])
                if not redis_cli.sismember(key, ip) and self.check_proxy(ip):
                    redis_cli.sadd(key, ip)
                    logger.debug('add ip: %s:%s' % (key, ip))
        except:
            #this method is called to update ip_pool, so we need to ture out update=False
            proxies_ip = self.get_proxy(http_key, update=False)
            proxies = {'http': proxies_ip.split('//')[1]}
            logger.debug('crawl faield and try again by use proxy: ', proxies)
            self.pares(url,key,proxies)

     #delte proxy if its impossible
    def delete_proxy(self, key, ip):
        try:
            redis_cli.srem(key, ip)
            logger.debug('delte successed: %s:%s' % (key, ip))
        except:
            logger.error('delete failed: %s:%s' %(key, ip))

#singleton
proxy = proxy()

if __name__ == '__main__':
    print(proxy.get_proxy(http_key))
    print(proxy.get_proxy(https_key))