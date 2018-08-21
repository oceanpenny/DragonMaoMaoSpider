
import urllib
from DragonMaoMaoSpider.dao.redisdb import redis_cli

#init_id, could be stars/politician/musician/criminal/anyone
init_seed = [
    '1797054534', '2509414473', '2611478681', '5861859392', '2011086863', '5127716917', '1259110474', '5850775634', '1886437464'
]

class SinaGenerator(object):
    def __init__(self, redis_key):
        self.page_num = 0
        self.redis_key = redis_key

    #default use list  settings:REDIS_START_URLS_AS_SET=False
    def gen(self,ids):
        for id in ids:
            url = 'https://weibo.cn/%s/info' % id
            redis_cli.sadd(self.redis_key, url)
