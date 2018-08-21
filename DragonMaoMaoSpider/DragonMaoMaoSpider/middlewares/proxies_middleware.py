
from datetime import datetime, timedelta
from twisted.web._newclient import ResponseNeverReceived
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError
import logging
from DragonMaoMaoSpider.anticrawl.proxy import proxy, http_key, https_key

logger = logging.getLogger(__name__)

class ProxyMiddleware(object):
    def __init__(self):
        self.last_proxy_time = datetime.now()
        self.interval = 20
        self.last_proxy = None

    #defaut change proxy after 20 minutes or request.meta['change_proxy']=true which may cause by except or response.
    def process_request(self, request, spider):
        request.meta['proxy'] = self.last_proxy

        if datetime.now() > (self.last_proxy_time + timedelta(minutes=self.interval)):
            if self.last_proxy is None:
                request.meta['change_proxy'] = True
            else:
                request.meta['change_proxy'] = False
                request.meta['proxy'] = None
            self.last_proxy_time = datetime.now()
            logger.debug('change proxy per %s minutes' % self.interval)

        if 'change_proxy' in request.meta.keys() and request.meta['change_proxy']:
            if request.url.startswith('https://'):
                self.last_proxy = proxy.get_proxy(https_key)
                request.meta['proxy'] = self.last_proxy
            elif request.url.startswith('http://'):
                self.last_proxy = proxy.get_proxy(http_key)
                request.meta['proxy'] = self.last_proxy
            request.meta['change_proxy'] = False
            logger.debug('url:%s, proxy:%s' % (request.url, request.meta['proxy']))

    #when response code is not 200 or not in allowed status_list change_proxy and try again, set dont_filter=True
    #you should init your spider.allowed_status_list attribute.
    def process_response(self, request, response, spider):
        if response.status != 200 \
                and (not hasattr(spider, "allowed_status_list") \
                     or response.status not in spider.allowed_status_list):
            logger.debug('response status:%s, which is not in spider.allowed_status_list, url:%s' % (response.status, request.url))
            new_request = request.copy()
            new_request.meta['change_proxy'] = True
            new_request.dont_filter = True
            return new_request
        else:
            return response

    #sample retry and change proxy
    def process_exception(self, request, exception, spider):
        pass