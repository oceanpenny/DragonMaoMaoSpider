# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class Sina_InfoItem(Item):
    ID = Field()  # sina_id
    NickName = Field()
    Gender = Field()
    Province = Field()
    City = Field()
    BriefIntroduction = Field()
    Birthday = Field()
    Num_Tweets = Field()
    Num_Follows = Field()
    Num_Fans = Field()
    SexOrientation = Field()
    Sentiment = Field()
    Authentication = Field()
    URL = Field()

class Sina_TweetsItem(Item):
    ID = Field()  #same as Info
    Tweets_ID = Field()
    Content = Field()
    PubTime = Field()
    PubTools = Field()
    Likes = Field()
    Comments = Field()
    Forwards = Field()

class Sina_RelationItem(Item):
    pass

class DouBan_BookItem(Item):
    title = Field()
    rating = Field()
    people_num = Field()
    author_info = Field()
    pub_info = Field()
