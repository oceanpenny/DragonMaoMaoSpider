# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from DragonMaoMaoSpider.dao.mongodb import mongodb_cli
from DragonMaoMaoSpider.items import InformationItem, TweetsItem, RelationshipsItem, BookItem

class MongoDBPipeline(object):

    def process_item(self, item, spider):
        """ 判断item的类型，并作相应的处理，再入数据库 """
        if isinstance(item, RelationshipsItem):
            try:
                mongodb_cli.insert('Relationships', dict(item))
            except Exception:
                pass
        elif isinstance(item, TweetsItem):
            try:
                mongodb_cli.insert('Tweets', dict(item))
            except Exception:
                pass
        elif isinstance(item, InformationItem):
            try:
                mongodb_cli.insert('Information', dict(item))
            except Exception:
                pass
        elif isinstance(item, BookItem):
            try:
                mongodb_cli.insert('Book', dict(item))
            except Exception:
                pass
        return item
