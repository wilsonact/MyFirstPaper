# -*- coding: utf-8 -*-
import scrapy


class ahItem(scrapy.Item):
    # 帖子表，包含帖子的信息：帖子ID、帖子名称、楼主、所属论坛、发帖时间、点击数、回复数
    # 内容表：用户id、用户当前帮助值、精华帖数、帖数、回复数、注册时间、来自地区、、帖子id、评论时间、内容、图片数、字数

    # content

    # YYY
    post_name = scrapy.Field()  # 帖子名
    post_id = scrapy.Field()  # pid
    host_id = scrapy.Field()  # 楼主ID
    host_name = scrapy.Field()  # host name
    post_forum = scrapy.Field()  # 所属论坛
    if_lord = scrapy.Field()  # 是否是楼主
    if_main_post = scrapy.Field()  # 是否是主贴（是否是回复） 主贴1 回复0
    post_time = scrapy.Field()  # 发布时间
    reply_cnt = scrapy.Field()  # 回复数，如果不是主贴，则定义为-1
    view_cnt = scrapy.Field()  # 点击数 如果不是主贴，则定义为-1
    post_content = scrapy.Field()  # 正文内容
    picture_desc = scrapy.Field()
    picture_cnt = scrapy.Field()  # 包含图片数

    # # user infomation
    user_id = scrapy.Field()  # 用户名称
    user_ess_cnt = scrapy.Field()  # 用户精华帖数
    user_post_cnt = scrapy.Field()  # 用户发帖数
    user_reply_cnt = scrapy.Field()  # 用户回复数
    user_reg_time = scrapy.Field()  # 用户注册时间
    user_area = scrapy.Field()  # 用户地区
