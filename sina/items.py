#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by shimeng on 17-5-19

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
