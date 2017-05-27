#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by shimeng on 17-5-19l

BOT_NAME = 'sina'

SPIDER_MODULES = ['sina.spiders']
NEWSPIDER_MODULE = 'sina.spiders'


ROBOTSTXT_OBEY = False

DEFAULT_REQUEST_HEADERS = {
  'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
  'Host':'m.weibo.cn'
}

ITEM_PIPELINES = {
    'sina.pipelines.MongoPipeline': 301,
}

MONGO_URI = 'mongodb://localhost'

MONGO_DATABASE = 'sina_weibo'