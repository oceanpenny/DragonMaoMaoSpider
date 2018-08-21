import re
import logging
import datetime

from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from DragonMaoMaoSpider.dao.redisdb import redis_cli
from DragonMaoMaoSpider.urlgen.sina_generator import init_seed, SinaGenerator
from DragonMaoMaoSpider.items import Sina_RelationItem, Sina_TweetsItem, Sina_InfoItem
from DragonMaoMaoSpider.anticrawl.cookies import initCookie, get_sina_cookie_from_cn, sina_acounts

#only crwal the pointed ids /infomation/tweets/follows-info/follows-tweets/fans-info/fans-tweets
SINGLE_RELATIONS = 0
#net datas, almost while(1)
WHOLE_NET = 1

logger = logging.getLogger(__name__)

class Spider(RedisSpider):
    name = 'SinaSpider'
    redis_key = "SinaSpider:start_urls"
    host = "https://weibo.cn"

    model = SINGLE_RELATIONS
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES':  {
            'DragonMaoMaoSpider.middlewares.proxies_middleware.ProxyMiddleware': 100,
            'DragonMaoMaoSpider.middlewares.agent_middleware.UserAgentMiddleware': 400,
            'DragonMaoMaoSpider.middlewares.cookies_middleware.CookiesMiddleware': 500,
        },
        'REDIS_START_URLS_AS_SET':True,
        'DOWNLOAD_TIMEOUT':100,
    }

    def __init__(self):
        generator = SinaGenerator(self.redis_key)
        generator.gen(init_seed)
        initCookie(self.name, sina_acounts, get_sina_cookie_from_cn)

    def parse(self, response):
        info_item = Sina_InfoItem()
        ID = re.findall('(\d+)/info', response.url)[0]
        try:
            text1 = ";".join(response.xpath('body/div[@class="c"]//text()').extract())  # 获取标签里的所有text()
            nickname = re.findall('昵称[：:]?(.*?);', text1)
            gender = re.findall('性别[：:]?(.*?);', text1)
            place = re.findall('地区[：:]?(.*?);', text1)
            briefIntroduction = re.findall('简介[：:]?(.*?);', text1)
            birthday = re.findall('生日[：:]?(.*?);', text1)
            sexOrientation = re.findall('性取向[：:]?(.*?);', text1)
            sentiment = re.findall('感情状况[：:]?(.*?);', text1)
            authentication = re.findall('认证[：:]?(.*?);', text1)
            url = re.findall('互联网[：:]?(.*?);', text1)

            info_item['ID'] = ID
            if nickname and nickname[0]:
                info_item["NickName"] = nickname[0].replace(u"\xa0", "")
            if gender and gender[0]:
                info_item["Gender"] = gender[0].replace(u"\xa0", "")
            if place and place[0]:
                place = place[0].replace(u"\xa0", "").split(" ")
                info_item["Province"] = place[0]
                if len(place) > 1:
                    info_item["City"] = place[1]
            if briefIntroduction and briefIntroduction[0]:
                info_item["BriefIntroduction"] = briefIntroduction[0].replace(u"\xa0", "")
            if birthday and birthday[0]:
                try:
                    birthday = datetime.datetime.strptime(birthday[0], "%Y-%m-%d")
                    info_item["Birthday"] = birthday - datetime.timedelta(hours=8)
                except Exception:
                    info_item["Birthday"] = birthday[0]
            if sexOrientation and sexOrientation[0]:
                if sexOrientation[0].replace(u"\xa0", "") == gender[0]:
                    info_item["SexOrientation"] = "同性恋"
                else:
                    info_item["SexOrientation"] = "异性恋"
            if sentiment and sentiment[0]:
                info_item["Sentiment"] = sentiment[0].replace(u"\xa0", "")
            if authentication and authentication[0]:
                info_item["Authentication"] = authentication[0].replace(u"\xa0", "")
            if url:
                info_item["URL"] = url[0]

            #crwal other info ex.Num_Tweets/Num_Follows/Num_Fans
            urlothers = 'https://weibo.cn/attgroup/opening?uid=%s' % ID
            yield Request(url=urlothers, meta={'item': info_item}, callback=self.parse_others)
        except Exception as e:
            logger.error('crawl ID:%s info failed, exception:%s' % (ID, e))

    def parse_others(self, response):
        info_item = response.meta['item']
        texts = ":".join(response.xpath('//div[@class="tip2"]/a//text()').extract())
        if texts:
            num_tweets = re.findall('微博\[(\d+)\]', texts)
            num_follows = re.findall('关注\[(\d+)\]', texts)
            num_fans = re.findall('粉丝\[(\d+)\]', texts)
            if num_tweets:
                info_item["Num_Tweets"] = int(num_tweets[0])
            if num_follows:
                info_item["Num_Follows"] = int(num_follows[0])
            if num_fans:
                info_item["Num_Fans"] = int(num_fans[0])
        yield info_item
        ID = info_item['ID']
        # infinite Loop, crawal new info via follow and fans
        if info_item["Num_Follows"] and info_item["Num_Follows"] < 500:
            yield Request(url="https://weibo.cn/%s/follow" % ID, callback=self.parse_info)
        if info_item["Num_Fans"] and info_item["Num_Fans"] < 500:
            yield Request(url="https://weibo.cn/%s/fans" % ID, callback=self.parse_info)

    def parse_info(self,response):
        urls = response.xpath('//a[text()="关注他" or text()="关注她"]/@href').extract()
        uids = re.findall('uid=(\d+)', ";".join(urls), re.S)
        for uid in uids:
            url = "https://weibo.cn/%s/info" % uid
            redis_cli.sadd(self.redis_key, url)

        next_url = response.xpath('//a[text()="下页"]/@href').extract()
        if next_url:
            yield Request(url=self.host+next_url[0], callback=self.parse_info)