
from datetime import datetime, timedelta
from twisted.web._newclient import ResponseNeverReceived
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError
import logging
from DragonMaoMaoSpider.anticrawl.proxy import proxy, http_key, https_key

logger = logging.getLogger(__name__)

class ProxyMiddleware(object):
    def __init__(self):
        self.url = None

    #random use proxy, and update ip state = true
    def process_request(self, request, spider):
        key = https_key if request.url.startswith('https://') else http_key
        if spider.name == 'SinaSpider':
            self.url = 'https://weibo.cn/pub/'
        proxies = proxy.get_proxy(key, url=self.url)
        ip = proxies.split('//')[1]
        request.meta['proxy'] = proxies
        proxy.set_proxy_status(key, ip, True)
        request.meta["ip"] = ip
        logger.debug('url:%s, proxy:%s' % (request.url, request.meta['proxy']))

    #when response code is not 200 or not in allowed status_list change_proxy and try again, set dont_filter=True
    #you should init your spider.allowed_status_list attribute.
    def process_response(self, request, response, spider):
        key = https_key if request.url.startswith('https://') else http_key
        ip =  request.meta["ip"]
        proxy.set_proxy_status(key, ip, False)

        if response.status != 200 \
                and (not hasattr(spider, "allowed_status_list") \
                     or response.status not in spider.allowed_status_list):
            logger.debug('response status:%s, which is not in spider.allowed_status_list, url:%s' % (response.status, request.url))
            new_request = request.copy()
            new_request.dont_filter = True
            return new_request
        else:
            return response

    #sample retry and change proxy
    def process_exception(self, request, exception, spider):
        pass