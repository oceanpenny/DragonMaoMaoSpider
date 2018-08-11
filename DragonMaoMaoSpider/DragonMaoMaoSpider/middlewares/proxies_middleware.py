
from datetime import datetime, timedelta
from twisted.web._newclient import ResponseNeverReceived
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError
import logging
from DragonMaoMaoSpider.anticrawl.proxy import proxy, http_key, https_key

logger = logging.getLogger(__name__)

class ProxyMiddleware(object):
    DONT_RETRY_ERRORS = (TimeoutError, ConnectionRefusedError, ResponseNeverReceived, ConnectError, ValueError)
    def __init__(self):
        self.last_proxy_time = datetime.now()
        self.recover_interval = 20
        self.last_proxy = None

    #defaut change proxy after 20 minutes or request.meta['change_proxy']=true which may cause by except or response.
    def process_request(self, request, spider):
        if datetime.now() > (self.last_proxy_time + timedelta(minutes=self.recover_interval)):
            request.meta['change_proxy'] = True
            self.last_no_proxy_time = datetime.now()
            logger.debug('try change proxy')

        if 'change_proxy' in request.meta.keys() and request.meta['change_proxy']:
            if self.last_proxy:
                del_ip = self.last_proxy.split('//')[1]
            if request.url.startswith('https://'):
                self.last_proxy = proxy.get_proxy(https_key)
                request.meta['proxy'] = self.last_proxy
                proxy.delete_proxy(https_key, del_ip)
            elif request.url.startswith('http://'):
                self.last_proxy = proxy.get_proxy(http_key)
                request.meta['proxy'] = self.last_proxy
                proxy.delete_proxy(http_key, del_ip)
            request.meta['change_proxy'] = False
            logger.debug('url:%s, proxyy:%s' % (request.url, request.meta['proxy']))

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
        logger.debug('request exception: %s' % request.url)
        new_request = request.copy()
        new_request.meta['change_proxy'] = True
        new_request.dont_filter = True
        return new_request