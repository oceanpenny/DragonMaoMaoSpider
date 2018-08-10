import urllib
from DragonMaoMaoSpider.dao.redisdb import redis_cli

class DouBanUrlGenerator(object):
    def __init__(self, tag, redis_key):
        self.page_num = 0
        self.tag = tag
        self.redis_key = redis_key

    #default use list  settings:REDIS_START_URLS_AS_SET=False
    def gen(self):
        url = 'http://www.douban.com/tag/' + urllib.parse.quote(self.tag) + '/book?start=' + str(self.page_num * 15)
        redis_cli.lpush(self.redis_key,url)
        self.page_num += 1

    def totalgen(self):
        for i in range(15):
            self.gen()

if __name__ == '__main__':
    testGenerator = DouBanUrlGenerator('物理','DouBanSpider:start_urls')
    testGenerator.totalgen()