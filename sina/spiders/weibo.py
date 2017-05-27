#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by shimeng on 17-5-19


import scrapy
import json
from scrapy import Request
import re
import time
from sina.items import CommentItem, WeiboItem
from urlparse import parse_qs


class WeiboSpider(scrapy.Spider):
    name = "weibo"
    allowed_domains = ["m.weibo.cn"]
    # root id
    first_id = '1713926427'
    init_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={}'
    followers_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&uid={uid}&page={page}'
    def start_requests(self):

        url = self.init_url.format(self.first_id)
        yield scrapy.Request(url=url, callback=self.get_containerid)

    def get_containerid(self, response):
        content = json.loads(response.body)
        if content.get('userInfo'):
            user_info = content.get('userInfo')
            # 关注url
            print 'user id is %s' % user_info.get('id')
            yield Request(self.followers_url.format(uid=user_info.get('id'), page=1), callback=self.parse_followers_to_get_more_ids)

        containerid = None
        for data in content.get('tabsInfo').get('tabs'):
            if data.get('tab_type') == 'weibo':
                containerid = data.get('containerid')
                print 'weibo request url containerid is %s' % containerid

        # construct the wei bo request url
        if containerid:
            weibo_url = response.url + '&containerid=%s' % containerid
            yield scrapy.Request(url=weibo_url, callback=self.get_weibo_id)
        else:
            print 'sorry, do not get containerid'

    def parse_followers_to_get_more_ids(self, response):
        content = json.loads(response.body)
        if content.get('ok'):
            followers = content.get('cards')[0].get('card_group')
            for follower in followers:
                user_id = follower.get('user').get('id')
                yield Request(self.init_url.format(user_id), callback=self.get_containerid)

            params = parse_qs(response.url)
            page = str(int(params.get('page')[0]) + 1) if params.get('page') else '2'

            yield Request(self.followers_url.format(uid=params.get('uid')[0], page=page), callback=self.parse_followers_to_get_more_ids)

    def get_weibo_id(self, response):
        content = json.loads(response.body)
        # get weibo id ,you can also save some other data if you need
        for data in content.get('cards'):
            if data.get('card_type') == 9:
                single_weibo_id = data.get('mblog').get('id')
                print single_weibo_id

                post_create_time = data.get('mblog').get('created_at')
                post_comment_url = 'https://m.weibo.cn/api/comments/show?id=%s&page=1' % single_weibo_id
                yield Request(url=post_comment_url, callback=self.get_comment_content)

                post_content_url = 'https://m.weibo.cn/statuses/extend?id=%s' % single_weibo_id
                yield Request(url=post_content_url, callback=self.get_post_content,
                              meta={"post_create_time": post_create_time})

    def get_post_content(self, response):
        post_id = re.findall('(\d+)', response.url)[0]
        post_url = 'https://m.weibo.cn/status/%s' % (str(post_id))
        post_create_time = response.meta.get("post_create_time")
        content = json.loads(response.body)
        item = WeiboItem()
        post_content = re.sub(r'<.*?>', '', content.get('longTextContent'))
        item['_id'] = post_id
        item['content'] = post_content
        item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        item['url'] = post_url
        item['post_create_time'] = post_create_time

        yield item

    def get_comment_content(self, response):
        content = json.loads(response.body)
        # get comment text
        for data in content.get('data'):
            post_id = re.findall('(\d+)', response.url)[0]
            _id = data.get('id')
            text = re.sub('<.*?>', '', data.get('text'))
            text_2 = re.sub(r'.*?@.*?:', '', text)
            reply_text = re.sub('.*?@.*?:', '', re.sub('<.*?>', '', data.get('reply_text', '')))

            item = CommentItem()
            item['_id'] = _id
            item['comment'] = text_2
            item['refer'] = reply_text
            item['post_id'] = post_id
            yield item

        max_page = content.get('max')
        page_num_pattern = r'(\d+)'
        page_num = re.findall(page_num_pattern, response.url)[1]
        if int(max_page) > 1 and int(max_page) > int(page_num):
            post_id_pattern = r'.*?id=(\d+)&page=.*?'
            post_id = re.findall(post_id_pattern, response.url)[0]
            url = 'https://m.weibo.cn/api/comments/show?id=%s&page=%s' % (post_id, str(int(page_num) + 1))
            yield Request(url=url, callback=self.get_comment_content)
