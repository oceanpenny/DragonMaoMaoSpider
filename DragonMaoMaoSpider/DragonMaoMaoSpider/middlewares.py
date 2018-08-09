# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import random
from scrapy import signals
from DragonMaoMaoSpider.anticrawl.user_agents import agents
from DragonMaoMaoSpider.anticrawl.proxy import proxy, http_key, https_key

class UserAgentMiddleware(object):
    """ 换User-Agent """
    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent

class ProxyMiddleware(object):

    def process_request(self, request, spider):
        request.meta['dont_redirect'] = True
        request.meta['proxy'] = proxy.get_proxy(http_key)
        print('proxy: ',request.meta['proxy'])