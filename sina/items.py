# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class WeiboItem(Item):
    table_name = 'weibos'

    _id = Field()
    content = Field()
    crawl_time = Field()
    url = Field()
    post_create_time = Field()


class CommentItem(Item):
    table_name = 'comments'
    _id = Field()
    post_id = Field()
    comment = Field()
    refer = Field()
