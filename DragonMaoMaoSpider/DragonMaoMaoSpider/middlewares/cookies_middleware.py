import json
import os
import random

from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.response import response_status_message
from twisted.web._newclient import ResponseNeverReceived
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError
import logging
from DragonMaoMaoSpider.anticrawl.cookies import initCookie, updateCookie, removeCookie
from DragonMaoMaoSpider.dao.redisdb import redis_cli

logger = logging.getLogger(__name__)

class CookiesMiddleware(object):

    def __init__(self):
        pass

    #get spiderName:cookies key and random choose one to set cookie
    def process_request(self, request, spider):
        redisKeys = redis_cli.keys('%s:Cookies*' % spider.name)
        if len(redisKeys) > 0:
            elem = random.choice(redisKeys).decode('utf-8')
            cookie = json.loads(redis_cli.get(elem))
            request.cookies = cookie
            account = elem.split("Cookies:")[-1]
            request.meta["accountText"] = elem.split("Cookies:")[-1].encode()

    #this method should set redis_enable = false, and process redirect url when cookie invalid/acounts forbidden/or any strange urls
    def process_response(self, request, response, spider):
        if spider.name == 'SinaSpider':
            return self.sina_cookies_redirect(request, response, spider)

    def process_exception(self, request, exception, spider):
        pass

    def sina_cookies_redirect(self, request, response, spider):
        if response.status in [300, 301, 302, 303]:
            try:
                redirect_url = response.headers["location"]
                if "login.weibo" in redirect_url or "login.sina" in redirect_url:  #cookie invalid
                    logger.warning("Acount:%s Cookie need to be updating..." % request.meta['accountText'].split("--")[0])
                    updateCookie(request.meta['accountText'], redis_cli, spider.name)
                elif "weibo.cn/security" in redirect_url:  # acount forbidden
                    logger.warning("Account:%s is locked! Remove it!" % request.meta['accountText'].split("--")[0])
                    removeCookie(request.meta["accountText"], redis_cli, spider.name)
                elif "weibo.cn/pub" in redirect_url:
                    logger.warning(
                        "Redirect to 'http://weibo.cn/pub'!( Account:%s )" % request.meta["accountText"].split("--")[0])
                new_request = request.copy()
                new_request.dont_filter = True
                return new_request
            except Exception as e:
                raise IgnoreRequest
        elif response.status in [403, 414]:
            logger.error("%s! Stopping..." % response.status)
            os.system("pause")
        else:
            return response