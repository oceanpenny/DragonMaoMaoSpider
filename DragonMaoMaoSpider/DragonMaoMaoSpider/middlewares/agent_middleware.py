# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random
import logging
from DragonMaoMaoSpider.anticrawl.user_agents import agents

logger = logging.getLogger(__name__)

class UserAgentMiddleware(object):
    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent