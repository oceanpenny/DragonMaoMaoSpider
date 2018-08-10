# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
from datetime import datetime, timedelta
import random
from twisted.web._newclient import ResponseNeverReceived
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError
import logging
from DragonMaoMaoSpider.anticrawl.user_agents import agents
from DragonMaoMaoSpider.anticrawl.proxy import proxy, http_key, https_key

logger = logging.getLogger(__name__)

class UserAgentMiddleware(object):
    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent

class ProxyMiddleware(object):
    DONT_RETRY_ERRORS = (TimeoutError, ConnectionRefusedError, ResponseNeverReceived, ConnectError, ValueError)
    def __init__(self):
        self.last_proxy_time = datetime.now()
        self.recover_interval = 20

    #defaut change proxy after 20 minutes or request.meta['change_proxy']=true which may cause by except or response.
    def process_request(self, request, spider):
        if datetime.now() > (self.last_proxy_time + timedelta(minutes=self.recover_interval)):
            request.meta['change_proxy'] = True
            self.last_no_proxy_time = datetime.now()
            logger.debug('try change proxy')

        if "change_proxy" in request.meta.keys() and request.meta["change_proxy"]:
            if request.url.startswith('https://'):
                request.meta['proxy'] = proxy.get_proxy(https_key)
            elif request.url.startswith('http://'):
                request.meta['proxy'] = proxy.get_proxy(http_key)
            request.meta['change_proxy'] = False
            logger.debug('url:%s, proxyy:%s' % (request.url, request.meta['proxy']))

    #when response code is not 200 or not in allowed status_list change_proxy and try again, set dont_filter=True
    #you should init your spider.allowed_status_list attribute.
    def process_response(self, request, response, spider):
        if response.status != 200 \
                and (not hasattr(spider, "allowed_status_list") \
                     or response.status not in spider.allowed_status_list):
            logger.debug('response status not in spider.allowed_status_list')
            new_request = request.copy()
            new_request.meta['change_proxy'] = True
            new_request.dont_filter = True
            return new_request
        else:
            return response

    #sample retry and change proxy
    def process_exception(self, request, exception, spider):
        logger.debug('request exception: ', request.url)
        new_request = request.copy()
        new_request.meta['change_proxy'] = True
        new_request.dont_filter = True
        return new_request