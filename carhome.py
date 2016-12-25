# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from urlparse import urljoin
from scrapy import Selector
from ahItem import ahItem


class MySpider(scrapy.Spider):
    name = "ah"
    allowed_domains = ["com.cn"]
    start_urls = [
        "http://club.autohome.com.cn/bbs/forum-c-3788-1.html"]
    custom_settings ={ 'DOWNLOAD_DELAY': 1 }
    # ,
    # "http://club.autohome.com.cn/bbs/thread-c-3788-57953292-1.html",
    # "http://club.autohome.com.cn/bbs/thread-c-3788-57984842-1.html"

    def parse(self,response):
        sel = Selector(response)
        try:
            post_list1 = sel.xpath('//div[@class="content"]/\
                div[@class="area"]/dl[@class="list_dl"]/\
                dt/a[@class="a_topic"]/@href').extract()
        except:
            post_list1=[]

        post_list2 = sel.xpath('//div[@class="content"]/\
            div[@class="carea"]/div[@id="subcontent"]/\
            dl[@class="list_dl"]/\
            dt/a[@class="a_topic"]/@href').extract()

        post_list = post_list1 + post_list2
        for post in post_list:
            post_page = urljoin("http://club.autohome.com.cn/bbs/", post)
            print post_page
            yield scrapy.Request(post_page, callback=self.parse_post, body='unicode')

        # ## 是否还有下一页，如果有的话，则继续

        try :
            next_page = sel.xpath('//div[@class="content"]/\
            div[@class="carea"]/div[@id="subcontent"]/\
            div[@class="pagearea"]/div[@class="pages"]/\
            a[@class="afpage"]/@href').extract()[0]
            has_next = True
        except:
            has_next = False

        if has_next:
            next_page = urljoin("http://club.autohome.com.cn/bbs", next_page)
        #     self.log('page_url: %s' % next_page)
        #     ## 将 「下一页」的链接传递给自身，并重新分析
            yield scrapy.Request(next_page, callback=self.parse, body='unicode')


    def parse_post(self, response):
        # 拿到页面上的链接，给内容解析页使用，如果有下一页，则调用本身 parse() '''
        # self.log("===========================| %s |" % response.url)
        sel = Selector(response)
    #     获取主帖内容
    #     song_list = response.css('div.sons').xpath('p[1]/a')
    #     total_page获取该帖子一共有多少页
        total_page = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
            div[@class="pagearea"]/div[@id="x-pages1"]/@maxindex').extract()[0]
        total_page = int(total_page)
        cur_page = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
            div[@class="pagearea"]/div[@id="x-pages1"]/span[@class="cur"]/\
            text()').extract()[0]
        cur_page = int(cur_page)
        # print cur_page
    #     div[@class="pagearea"]/div[@id="x-pages1"]/\
    #     @maxindex').extract()[0]

        # print response.url

        yield scrapy.Request(url=response.url, callback=self.parse_content, body='unicode')
    #     获取回复内容，一共有total_page 页，在每一页：
        next_page = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
            div[@class="pagearea"]/div[@id="x-pages1"]/a[@class="afpage"]/@href\
            ').extract()[0]
        next_page = urljoin("http://club.autohome.com.cn/bbs/", next_page)
        print 'next_page:' +next_page
        
        n = 1
        if (cur_page < total_page):
            yield scrapy.Request(url=next_page, callback=self.parse_content, body='unicode')
            n += 1

        # print response
        # url = reponse

    #         self.log('gushi_url: %s' % url)
    #         # 将得到的页面地址传送给单个页面处理函数进行处理 -> parse_content()

    #     # 是否还有下一页，如果有的话，则继续
    #     next_pages = response.css('div.pages').xpath(
    #         './a[@style="width:60px;"]/@href')

    #     if next_pages:
    #         next_page = urljoin(SITE_URL, next_pages[0].extract())
    #         self.log('page_url: %s' % next_page)
    #         # 将 「下一页」的链接传递给自身，并重新分析
    #         yield scrapy.Request(next_page, callback=self.parse,
    #                              headers=headers)

    def parse_content(self, response):

        item = ahItem()
        sel = Selector(response)

        cur_page = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
            div[@class="pagearea"]/div[@id="x-pages1"]/span[@class="cur"]/\
            text()').extract()[0]
        print "cur_page:"
        print cur_page

        if (int(cur_page) == 1):

            # common info
            try:
                post_name = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-maintopic"]/\
                div[@id="consnav"]/span[4]/text()').extract()[0]
                item['post_name'] = post_name
            except:
                item['post_name'] = 'fail'

            try:
                post_id = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-maintopic"]/\
                div[@id="F0"]/@pk').extract()[0]
                item['post_id'] = post_id
            except:
                item['post_id'] = 'fail'

            try:
                host_id = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-maintopic"]/\
                div[@id="F0"]/@uid').extract()[0]
                item['host_id'] = host_id
            except:
                item['host_id'] = 'fail'

            try:
                host_name = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-maintopic"]/\
                div[@id="F0"]/div[@class="conleft fl"]/ul[@class="maxw"]/\
                li[@class="txtcenter fw"]/a[@xname="uname"]/text()'
                                      ).extract()[0]
                item['host_name'] = host_name
            except:
                item['host_name'] = 'fail'

            try:
                post_forum = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-maintopic"]/\
                div[@id="consnav"]/span[2]/a/text()'
                                       ).extract()[0]
                item['post_forum'] = post_forum
            except:
                item['post_forum'] = 'fail'

            item['if_lord'] = '1'
            item['if_main_post'] = '1'

            try:
                view_cnt = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-maintopic"]/\
                div[@id="consnav"]/span[@class="fr fon12"]/font[@id="x-views"]/text()'
                                     ).extract()[0]
                item['view_cnt'] = view_cnt
            except:
                item['view_cnt'] = 'fail'

            try:
                item['post_time'] = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-maintopic"]/\
                div[@id="F0"]/@data-time').extract()[0]
            except:
                item['post_time'] = 'fail'

            try:
                reply_cnt = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-maintopic"]/\
                div[@id="consnav"]/span[@class="fr fon12"]/font[@id="x-replys"]/text()'
                                      ).extract()[0]
                item['reply_cnt'] = reply_cnt
            except:
                item['reply_cnt'] = 'fail'

            try:
                item['post_content'] = ''.join(sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-maintopic"]/\
                div[@id="F0"]/div[@class="conright fr"]/div[@class="rconten"]/\
                div[@class="conttxt"]/div[@class="w740"]/div[@class="tz-paragraph"]/text()'
                                                         ).extract())
            except:
                item['post_content'] = 'fail'

            try:
                picture_desc = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-maintopic"]/\
                div[@id="F0"]/div[@class="conright fr"]/div[@class="rconten"]/\
                div[@class="conttxt"]/div[@class="w740"]/div[@class="tz-figure"]/\
                div[@class="description"]/text()').extract()
                item['picture_desc'] = ' | '.join(picture_desc)
                item['picture_cnt'] = len(picture_desc)
            except:
                item['picture_desc'] = '-'
                item['picture_cnt'] = '0'

            try:
                item['user_id'] = host_id
            except:
                item['user_id'] = 'fail'
            # item['user_help_score'] =
            try:
                item['user_ess_cnt'] = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-maintopic"]/\
                div[@id="F0"]/div[@class="conleft fl"]/ul[@class="leftlist"]/\
                li[3]/a/text()').extract()[0]
            except:
                item['user_ess_cnt'] = '0帖'

            try:
                item['user_post_cnt'] = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-maintopic"]/\
                div[@id="F0"]/div[@class="conleft fl"]/ul[@class="leftlist"]/\
                li[4]/a[1]/text()').extract()[0]
            except:
                item['user_post_cnt'] = '0帖'

            try:
                item['user_reply_cnt'] = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-maintopic"]/\
                div[@id="F0"]/div[@class="conleft fl"]/ul[@class="leftlist"]/\
                li[4]/a[2]/text()').extract()[0]
            except:
                item['user_reply_cnt'] = '0回'

            try:
                item['user_reg_time'] = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-maintopic"]/\
                div[@id="F0"]/div[@class="conleft fl"]/ul[@class="leftlist"]/\
                li[5]/text()').extract()[0]
            except:
                item['user_reg_time'] = 'fail'

            try:
                item['user_area'] = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-maintopic"]/\
                div[@id="F0"]/div[@class="conleft fl"]/ul[@class="leftlist"]/\
                li[6]/a/text()').extract()[0]
            except:
                item['user_area'] = 'fail'

            print "\ntest print:"
            for i in item:
                print i, "  ", item[i]
            yield item

        # print the reply of single page
        reply_cnt_perpage = len(sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
            div[@id="cont_main"]/div[@id="maxwrap-reply"]/\
            div[@class="clearfix contstxt outer-section"]').extract())
        reply_cnt_perpage = int(reply_cnt_perpage)
        print "reply cnt perpage:"
        print reply_cnt_perpage

        for i in xrange(reply_cnt_perpage):
            print '\nfloor:' + str(i)
            item = ahItem()
            # path = '//div[@id="topic_detail_main"]/div[@id="content"]/\
            # div[@id="cont_main"]/div[@id="maxwrap-reply"]/\
            # div[@class="clearfix contstxt outer-section"][%s]'%i
            # print path
            i = str(i + 1)
            try:
                post_name = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-maintopic"]/\
                div[@id="consnav"]/span[4]/text()').extract()[0]
                item['post_name'] = post_name
            except:
                item['post_name'] = 'fail'

            try:

                post_id = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@class="pagearea"]/div[@id="x-pages1"]/a[1]/@href\
                ').extract()[0]
                print post_id
                post_id = post_id.split('-')[3]
                item['post_id'] = post_id
            except:
                item['post_id'] = 'fail'

            item['host_id'] = '-'

            item['host_name'] = '-'
            try:
                item['post_forum'] = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                    div[@id="cont_main"]/div[@id="maxwrap-maintopic"]/\
                    div[@id="consnav"]/span[2]/a/text()'
                                           ).extract()[0]
            except:
                item['post_forum'] = 'fail'

            item['if_lord'] = '0'
            item['if_main_post'] = '0'
            item['view_cnt'] = '-'
            item['reply_cnt'] = '-'

            try:
                item['post_content'] =  '\n'.join(sel.xpath('//div[@id="topic_detail_main"]/\
                    div[@id="content"]/\
                    div[@id="cont_main"]/div[@id="maxwrap-reply"]/\
                    div[@class="clearfix contstxt outer-section"][' + i + ']/\
                    div[@class="conright fl"]/div[@class="rconten"]/\
                    div[@xname="content"]/div/text()').extract())
                if item['post_content'] == '':
                    item['post_content'] =  '\n'.join(sel.xpath('//div[@id="topic_detail_main"]/\
                    div[@id="content"]/\
                    div[@id="cont_main"]/div[@id="maxwrap-reply"]/\
                    div[@class="clearfix contstxt outer-section"][' + i + ']/\
                    div[@class="conright fl"]/div[@class="rconten"]/\
                    div[@xname="content"]/div/div[2]/text()').extract())
                if item['post_content'] == '':
                    item['post_content'] =  '\n'.join(sel.xpath('//div[@id="topic_detail_main"]/\
                    div[@id="content"]/\
                    div[@id="cont_main"]/div[@id="maxwrap-reply"]/\
                    div[@class="clearfix contstxt outer-section"][' + i + ']/\
                    div[@class="conright fl"]/div[@class="rconten"]/\
                    div[@xname="content"]/div/p/text()').extract())
            except:
                item['post_content'] = 'fail'

            item['picture_desc'] = '-'
            item['picture_cnt'] = '-'

            try:
                item['post_time'] = sel.xpath('//div[@id="topic_detail_main"]/\
                        div[@id="content"]/\
                        div[@id="cont_main"]/div[@id="maxwrap-reply"]/\
                        div[@class="clearfix contstxt outer-section"][' + i + ']/\
                        @data-time').extract()[0]
            except:
                item['post_time'] = 'fail'

            try:
                item['user_id'] = sel.xpath('//div[@id="topic_detail_main"]/\
                        div[@id="content"]/\
                        div[@id="cont_main"]/div[@id="maxwrap-reply"]/\
                        div[@class="clearfix contstxt outer-section"][' + i + ']/\
                        @uid').extract()[0]
            except:
                item['user_id'] = 'fail'

            try:
                item['user_ess_cnt'] = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                    div[@id="cont_main"]/div[@id="maxwrap-reply"]/\
                    div[@class="clearfix contstxt outer-section"][' + i + ']/\
                    div[@class="conleft fl"]/ul[@class="leftlist"]/\
                    li[3]/a/text()').extract()[0]
            except:
                item['user_ess_cnt'] = '0帖'

            try:
                item['user_post_cnt'] = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-reply"]/\
                div[@class="clearfix contstxt outer-section"][' + i + ']/\
                div[@class="conleft fl"]/ul[@class="leftlist"]/\
                li[4]/a[1]/text()').extract()[0]
            except:
                item['user_post_cnt'] = '0帖'

            try:
                item['user_reply_cnt'] = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-reply"]/\
                div[@class="clearfix contstxt outer-section"][' + i + ']/\
                div[@class="conleft fl"]/ul[@class="leftlist"]/\
                li[4]/a[2]/text()').extract()[0]
            except:
                item['user_reply_cnt'] = '0回'

            try:
                item['user_reg_time'] = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-reply"]/\
                div[@class="clearfix contstxt outer-section"][' + i + ']/\
                div[@class="conleft fl"]/ul[@class="leftlist"]/\
                li[5]/text()').extract()[0]
            except:
                item['user_reg_time'] = 'fail'

            try:
                item['user_area'] = sel.xpath('//div[@id="topic_detail_main"]/div[@id="content"]/\
                div[@id="cont_main"]/div[@id="maxwrap-reply"]/\
                div[@class="clearfix contstxt outer-section"][' + i + ']/\
                div[@class="conleft fl"]/ul[@class="leftlist"]/\
                li[6]/a/text()').extract()[0]
            except:
                item['user_area'] = 'fail'

            yield item
            for i in item:
                print i, "  ", item[i]

    # def parese_reply(self,response)
    #     item = ahItem()
    #     sel = Selector(response)

        # for i in  xrange(20):
        #      item['post_name'] = post_name
        #      item['post_id'] = post_id
        #      item['host_id'] = host_id
        #      item['host_name'] = host_name
        #      item['post_forum'] = post_forum
        #      item['view_cnt'] = view_cnt
        #      item['reply_cnt'] = reply_cn

        # print "\ntest print:"
        # for i in item:
        #     print i, "  ", item[i]
        # print item['post_name'],"\n", item['post_host']


# configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
runner = CrawlerRunner()

d = runner.crawl(MySpider)
d.addBoth(lambda _: reactor.stop())
reactor.run()
