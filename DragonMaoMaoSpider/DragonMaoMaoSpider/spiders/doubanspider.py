
from scrapy_redis.spiders import RedisSpider
from DragonMaoMaoSpider.items import DouBan_BookItem
from DragonMaoMaoSpider.urlgen.generators import DouBanUrlGenerator
from scrapy.http import Request


class Spider(RedisSpider):
    name = 'DouBanSpider'
    redis_key = 'DouBanSpider:start_urls'
    allowed_status_list = []

    #no need to login, no cookies, disable redirect
    custom_settings = {
        'COOKIES_ENABLED': False,
        'SCHEDULER_DUPEFILTER_KEY':'DouBanSpider:dupefilter',
    }
    def __init__(self):
        for tag in {'爱情', '传记', '汽车', '旅游', '历史', '武侠', '哲学', '物理', '心理学'}:
            DouBanUrlGenerator(tag, self.redis_key).totalgen()

    def parse(self, response):
        return
        bookItem = DouBan_BookItem()
        booklist = response.xpath('//div[@class="mod book-list"]')
        for book_info in booklist.xpath('.//dd'):
            bookItem['title'] = book_info.xpath('./a[@class="title"]/text()').extract()[0]
            desc = book_info.xpath('.//div[@class="desc"]/text()').extract()[0]
            desc_list = desc.split('/')
            book_url = book_info.xpath('./a[@class="title"]/@href').extract()[0]
            try:
                bookItem['author_info'] = '作者/译者： ' + '/'.join(desc_list[0:-3])
            except:
                bookItem['author_info'] ='作者/译者： 暂无'
            try:
                bookItem['pub_info'] = '出版信息： ' + '/'.join(desc_list[-3:])
            except:
                bookItem['pub_info'] = '出版信息： 暂无'
            try:
                bookItem['rating'] = book_info.xpath('.//span[@class="rating_nums"]').extract()[0]
            except:
                bookItem['rating'] ='0.0'
            yield (Request(url=book_url, meta={"item": bookItem}, callback=self.parsbook_url))

    def parsbook_url(self, response):
        item = response.meta['item']
        try:
            item['people_num'] = response.xpath('//div[@class="rating_sum"]//span')[1].xpath('./text()').extract()[0]
        except:
            item['people_num'] = '0'
        yield(item)