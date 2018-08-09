# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import DragonMaoMaoSpider.dao.mongodb as mongodb
from DragonMaoMaoSpider.items import InformationItem, TweetsItem, RelationshipsItem, BookItem

class MongoDBPipeline(object):
    def __init__(self):
        self.clinet = mongodb.MongoDBClient()

    def process_item(self, item, spider):
        """ 判断item的类型，并作相应的处理，再入数据库 """
        if isinstance(item, RelationshipsItem):
            try:
                self.clinet.insert('Relationships', dict(item))
            except Exception:
                pass
        elif isinstance(item, TweetsItem):
            try:
                self.clinet.insert('Tweets', dict(item))
            except Exception:
                pass
        elif isinstance(item, InformationItem):
            try:
                self.clinet.insert('Information', dict(item))
            except Exception:
                pass
        elif isinstance(item, BookItem):
            try:
                self.clinet.insert('Book', dict(item))
            except Exception:
                pass
        return item
