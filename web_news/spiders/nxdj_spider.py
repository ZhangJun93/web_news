# -*- coding: utf-8 -*-
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.items import SpiderItem
from scrapy.spiders import CrawlSpider, Request
from web_news.misc.spiderredis import SpiderRedis
import time
import re


class NingXiaSpider(SpiderRedis):
    name = 'ningxiadj'
    website = u'宁夏党建网'
    allowed_domins = ['www.nxdjw.gov.cn']
    start_urls = ['http://www.nxdjw.gov.cn/']

    rules = (
        Rule(LinkExtractor(allow=(r'ywdt/gcsy0526/', r'/ywdt/djyw0526/', r'/jcdj', r'/dyjy', r'/gbgz', r'/gbjd', r'/lzjs', r'/xxjl', r'/djyj', r'/rcgz', r'/gsgg0526/',  r'/rqgs0526/', r'/rsrm0526/')), callback='parse_item', follow=True),
    )

    custom_settings = {
        'CLOSESPIDER_TIMEOUT': 3600,
    }

    # def find_urls(self, response):
    #     print "test ", response.url
    #     try:
    #         url_new = ""
    #         page_num = int(re.search(r'createPageHTML.(\d+), 0, "index", "html".', response.body).group(1))
    #         match = re.search(r'((http://www.nxdjw.gov.cn/([0-9a-zA-Z]{4})/)[a-zA-Z0-9/]*)', response.url)
    #         if match:
    #             if match.group(3) == 'ywdt':
    #                 # 如果是 /ywdt/djyw0526/* ,/ywdt/gcsy0526/* 这类url
    #                 for i in range(page_num -1):
    #                     url_new = match.group(1) + "index_" + str(i + 1) + ".html"
    #                     print '1, ', url_new
    #                     yield Request(url_new)
    #             else:
    #                 # 如果不是 /ywdt/djyw0526/* ,/ywdt/gcsy0526/* ， 使用另一种匹配方式
    #                 for i in range(page_num - 1):
    #                     url_new = match.group(2) + "index_" + str(i + 1) + ".html"
    #                     print '2, ', url_new
    #                     yield Request(url_new)
    #     except Exception as e:
    #         self.logger.error('can not find next page url, error url: %s, error msg: %s', (response.url, e))

    def parse_item(self, response):
        if response.body.find("function createPageHTML") != -1:
            try:
                url_new = ""
                page_num = int(re.search(r'createPageHTML.(\d+), 0, "index", "html".', response.body).group(1))
                match = re.search(r'((http://www.nxdjw.gov.cn/([0-9a-zA-Z]{4})/)[a-zA-Z0-9/]*)', response.url)
                if match:
                    if match.group(3) == 'ywdt':
                        # 如果是 /ywdt/djyw0526/* ,/ywdt/gcsy0526/* 这类url
                        for i in range(page_num - 1):
                            url_new = match.group(1) + "index_" + str(i + 1) + ".html"
                            yield Request(url_new)
                    else:
                        # 如果不是 /ywdt/djyw0526/* ,/ywdt/gcsy0526/* ， 使用另一种匹配方式
                        for i in range(page_num - 1):
                            url_new = match.group(2) + "index_" + str(i + 1) + ".html"
                            yield Request(url_new)
            except Exception as e:
                self.logger.error('can not find next page url, error url: %s, error msg: %s', (response.url, e))
        elif re.search(r'/[a-zA-Z0-9]+/t[0-9_]+.html', response.url):
            loader = ItemLoader(item=SpiderItem(), response=response)
            contents = ''
            title = ''
            try:
                title = response.xpath('/html/head/title/text()').extract_first()

                # 利用url提取日期
                match = re.search(r't(20[0-9]{6})', response.url)
                date = match.group(1)
                dateArray = time.strptime(date, "%Y%m%d")
                otherStyleDate = time.strftime("%Y-%m-%d", dateArray)

                content_list = response.xpath('//td[@class="hs14"]/descendant-or-self::p/text()').extract()
                for content in content_list:
                    contents += content

                ### print info
                # try:
                # print 'title, ', title.encode('GB18030')
                # print 'url, ', response.url
                # print "date, ", otherStyleDate
                # print "content, ", contents.encode('GB18030')
                # except Exception as e:
                #     print " error : ", e

                loader.add_value('title', title)
                loader.add_value('date', otherStyleDate)
            except Exception as e:
                self.logger.error('error url: %s error msg: %s' % (response.url, e))
                loader.add_value('title', '')
                loader.add_value('date', '1970-01-01')
            finally:
                # self.logger.info('crawling url: %s' % response.url)
                loader.add_value('website', self.website)
                loader.add_value('url', response.url)
                loader.add_value('collection_name', self.name)
                if contents == '':
                    self.logger.warning(' url: %s msg: %s' % (response.url, ' content is None'))
                loader.add_value('content', contents)
                yield loader.load_item()
