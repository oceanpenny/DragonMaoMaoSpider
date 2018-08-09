import urllib.request

from scrapy_redis.spiders import RedisSpider
from bs4 import BeautifulSoup
from DragonMaoMaoSpider.items import BookItem
from scrapy.selector import Selector
from DragonMaoMaoSpider.urlgen.generators import DouBanUrlGenerator
from scrapy.http import Request


class Spider(RedisSpider):
    name = 'DouBanSpider'
    redis_key = 'DouBanSpider:start_urls'
    DouBanUrlGenerator('科技', redis_key).totalgen()

    def parse(self, response):
        bookItem = BookItem()
        booklist = response.xpath('//div[@class="mod book-list"]')
        #print(booklist)
        for book_info in booklist.xpath('.//dd'):
            bookItem['title'] = book_info.xpath('./a[@class="title"]/text()').extract()[0]
            desc = book_info.xpath('.//div[@class="desc"]/text()').extract()[0]
            print(desc)
            desc_list = desc.split('/')
            book_url = book_info.xpath('./a[@class="title"]/@href').extract()[0]
            #book_url = book_info.find('a', {'class': 'title'}).get('href')
            try:
                bookItem['author_info'] = '作者/译者： ' + '/'.join(desc_list[0:-3])
            except:
                bookItem['author_info'] ='作者/译者： 暂无'
            try:
                bookItem['pub_info'] = '出版信息： ' + '/'.join(desc_list[-3:])
            except:
                bookItem['pub_info'] = '出版信息： 暂无'
            try:
                bookItem['rating'] = book_info.find('span', {'class':'rating_nums'}).string.strip()
            except:
                bookItem['rating'] ='0.0'
            #print(bookItem['title'])
            #print(bookItem['author_info'])
            #print(bookItem['pub_info'])
            #print(bookItem['rating'])
            #print(bookItem.author_info)
            print("boourl: " + book_url)
            yield (Request(url=book_url, meta={"item": bookItem}, callback=self.parsbook_url, dont_filter=True))
        #yield bookItem

    def parsbook_url(self, response):
        item = response.meta['item']
        people_num = response.xpath('//div[@class="rating_sum"]//span').extract()[1]
        print('num: ' + people_num)
        #people_num = soup.find('div', {'class': 'rating_sum'}).findAll('span')[1].string.strip()