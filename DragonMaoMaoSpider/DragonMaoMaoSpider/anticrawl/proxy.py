# -*- coding:UTF-8 -*-
import socket
import telnetlib
import urllib
import urllib.request

from bs4 import BeautifulSoup
import requests
import random
from DragonMaoMaoSpider.anticrawl.user_agents import agents
from DragonMaoMaoSpider.dao.redisdb import redis_cli
import logging
import threading
from time import ctime,sleep

#redis_key where we store http/https proxies
http_key = 'proxy:http'
https_key = 'proxy:https'
logger = logging.getLogger(__name__)

class proxy(object):
    def __init__(self):
        self.pool_size = 10
        self.header = {'Upgrade-Insecure-Requests': '1',
                          'User-Agent': random.choice(agents),
                          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                          'Referer': 'http://www.xicidaili.com/nn/',
                          'Accept-Encoding': 'gzip, deflate, sdch',
                          'Accept-Language': 'zh-CN,zh;q=0.8',}
        self.url = None

    #http or https, update when pool_size < threshold or pool_size==0
    def get_proxy(self, key, update=True, url=None):
        self.url = url
        try:
            if (update and redis_cli.hlen(key) < self.pool_size / 3) or redis_cli.hlen(key) == 0:
                self.crawl_proxy(key)

            for ip in  redis_cli.hkeys(key):
                if redis_cli.hget(key,ip).decode('utf-8') == 'False':
                    if self.check_proxy(ip.decode('utf-8')):
                        if key == http_key:
                            return 'http://%s' % ip.decode('utf-8')
                        elif key == https_key:
                            return 'https://%s' % ip.decode('utf-8')
                    else:
                        self.delete_proxy(key,ip)
                        #redis_cli.hdel(key,ip)
            self.get_proxy(key,update, url)
        except Exception as e:
            logger.error('get proxy failed, reason:%s' % e)
            return  None

    #timout is useful even though its take crawl more time
    def check_proxy(self, ip):
        li = ip.split(':')
        try:
            ##telnetlib.Telnet(li[0], port=li[1], timeout=2)
            sock = socket.create_connection((li[0], li[1]), 3)
            sock.close()
            if self.url is not None:
                proxies = {'https': ip}
                print(proxies)
                requests.get(url, headers={'User-Agent':random.choice(agents)}, proxies=proxies)
                print('......')
            return True
        except:
            return False

    #crawl http or https, and store set in redis
    def crawl_proxy(self, key):
        logger.info('crawl %s proxy begin' % key)
        page = random.randint(1,10)
        while 1:
            url = 'http://www.xicidaili.com/nn/%d' % page
            self.pares(url, key)
            if redis_cli.hlen(key) >= self.pool_size:
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
                if  self.check_proxy(ip):
                    redis_cli.hset(key,ip,False)
                    logger.debug('add ip: %s:%s' % (key, ip))
        except:
            #this method is called to update ip_pool, so we need to set update=False
            proxies_ip = self.get_proxy(http_key, update=False)
            proxies = {'http': proxies_ip.split('//')[1]}
            logger.debug('crawl faield and try again by use proxy: ', proxies)
            self.pares(url,key,proxies)

     #delte proxy if its impossible
    def delete_proxy(self, key, ip):
        try:
            redis_cli.hdel(key, ip)
            logger.debug('delte successed: %s:%s' % (key, ip))
        except:
            logger.error('delete failed: %s:%s' %(key, ip))

    def set_proxy_status(self,key,ip,stat):
        try:
            redis_cli.hset(key, ip, stat)
            logger.debug('update successed: %s:%s' % (key, ip))
        except Exception as e:
            logger.error('update failed: %s:%s' % (key, ip))
#singleton
#proxy = proxy()
proxy1 = proxy()
proxy2 = proxy()
proxy3 = proxy()
proxy = proxy()

if __name__ == '__main__':
    url = 'https://weibo.cn/pub/'
    #print(proxy.get_proxy(http_key))
    #print(proxy.get_proxy(https_key, url=url))

    t1 = threading.Thread(target=proxy1.get_proxy,args=(https_key,True,url))
    t2 = threading.Thread(target=proxy2.get_proxy, args=(https_key, True, url))
    t3 = threading.Thread(target=proxy3.get_proxy, args=(https_key, True, url))
    for t in [t1,t2,t3]:
        t.setDaemon(True)
        t.start()
    t.join()

    for ip in redis_cli.hkeys(https_key):
        try:
            if not proxy.check_proxy(ip.decode('utf-8')):
                proxy.delete_proxy(https_key, ip)
            else:
                #li = ip.decode('utf8').split(':')
                proxies = {'https':  ip.decode('utf8')}
               # httpproxy_handler = urllib.request.ProxyHandler({"https":  ip.decode('utf8')})
                requests.get(url, headers={'User-Agent':random.choice(agents)}, proxies=proxies)
                print('hhg')
        except:
            proxy.delete_proxy(https_key, ip)
