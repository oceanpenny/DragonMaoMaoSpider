# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from DragonMaoMaoSpider.dao.mongodb import mongodb_cli
from DragonMaoMaoSpider.items import Sina_InfoItem, Sina_TweetsItem, Sina_RelationItem, DouBan_BookItem

class MongoDBPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, Sina_RelationItem):
            try:
                mongodb_cli.insert('Relationships', dict(item))
            except Exception:
                pass
        elif isinstance(item, Sina_TweetsItem):
            try:
                mongodb_cli.insert('Tweets', dict(item))
            except Exception:
                pass
        elif isinstance(item, Sina_InfoItem):
            try:
                mongodb_cli.insert('Information', dict(item))
            except Exception:
                pass
        elif isinstance(item, DouBan_BookItem):
            try:
                mongodb_cli.insert('Book', dict(item))
            except Exception:
                pass
        return item
