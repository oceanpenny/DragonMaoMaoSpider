# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
from datetime import datetime, timedelta
import random
from twisted.web._newclient import ResponseNeverReceived
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError

from DragonMaoMaoSpider.anticrawl.user_agents import agents
from DragonMaoMaoSpider.anticrawl.proxy import proxy, http_key, https_key

class UserAgentMiddleware(object):
    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent

class ProxyMiddleware(object):
    DONT_RETRY_ERRORS = (TimeoutError, ConnectionRefusedError, ResponseNeverReceived, ConnectError, ValueError)
    def __init__(self):
        self.last_proxy_time = datetime.now()
        self.recover_interval = 20

    def process_request(self, request, spider):
        if datetime.now() > (self.last_proxy_time + timedelta(minutes=self.recover_interval)):
            request.meta['change_proxy'] = True
            self.last_no_proxy_time = datetime.now()

        #request.meta['dont_redirect'] = True
        if "change_proxy" in request.meta.keys() and request.meta["change_proxy"]:
            print(request.url)
            if request.url.startswith('https://'):
                request.meta['proxy'] = proxy.get_proxy(https_key)
            elif request.url.startswith('http://'):
                request.meta['proxy'] = proxy.get_proxy(http_key)
            request.meta['change_proxy'] = False
            print('proxy: ',request.meta['proxy'])

    def process_response(self, request, response, spider):
        if response.status != 200 \
                and (not hasattr(spider, "website_possible_httpstatus_list") \
                     or response.status not in spider.website_possible_httpstatus_list):
            print("response status not in spider.website_possible_httpstatus_list")
            new_request = request.copy()
            new_request.meta['change_proxy'] = True
            new_request.dont_filter = True
            return new_request
        else:
            return response

    def process_exception(self, request, exception, spider):
        print('request exception: ', request.url)