# -*- coding:utf-8 -*-
from scrapy.spiders import Rule
from scrapy.spiders import CrawlSpider, Request
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.items import SpiderItem
from web_news.misc.spiderredis import SpiderRedis
import time
import re


class XiZangSpider(SpiderRedis):
    name = 'xizangdj'
    website = u'西藏机关党建网'
    allowed_domain = ['dj.zgxzqw.gov.cn']
    start_urls = ['http://dj.zgxzqw.gov.cn/']

    rules = [
        Rule(LinkExtractor(allow=r't[0-9_]+.html'), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=('/dsj', '/tzgg', '/dwyw', '/qzdt', '/dsdt', '/xf', '/sxjs', '/zzjs', '/zfjs', '/ffcl', '/zdjs',
                                  '/qtgz', '/zcfg', '/sy/xssc', '/jl', '/tzgg')), callback='find_urls', follow=True),
    ]

    custom_settings = {
        'CLOSESPIDER_TIMEOUT': 3600,
    }

    def find_urls(self, response):
        if response.body.find('下一页') != -1:
            try:
                url_new = ''
                page_num = int(re.search(r'createPageHTML.(\d+), 0,', response.body).group(1))
                for i in range(page_num - 1):
                    url_new = response.url + "index_" + str(i + 1) + ".html"
                    yield Request(url_new)
            except Exception as e:
                self.logger.error('can not find next page url, error url: %s, error msg: %s', (response.url, e))

    def parse_item(self, response):
        loader = ItemLoader(item=SpiderItem(), response=response)
        contents = ''
        try:
            # print "title, ", response.xpath(r'//div[@class="c-tit"]/text()').extract_first().encode('GB18030')
            title = response.xpath(r'//div[@class="c-tit"]/text()').extract_first()

            match = re.search(r't(20[0-9]{6})', response.url)
            date = match.group(1)
            dateArray = time.strptime(date, "%Y%m%d")
            otherStyleDate = time.strftime("%Y-%m-%d", dateArray)

            # 提取多种内容能出现的位置
            content_list = response.xpath(r'//div[@class="TRS_Editor"]//text() | //p[@class="TRS_PreAppend"]//text() | //p[@class="Custom_UnionStyle"]//text()').extract()

            for content in content_list:
                contents = contents + content

            ### print info
            # try:
            #     print 'title, ', title.encode('GB18030')
            #     print 'url, ', response.url
            #     print "date, ", otherStyleDate
            #     print "content, ", contents.encode('GB18030')
            # except Exception as e:
            #     print " error : ", e

            loader.add_value('title', title)
            loader.add_value('date', otherStyleDate)
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            loader.add_value('date', '1970-01-01')
            loader.add_value('title', '')
        finally:
            # self.logger.info('crawling url: %s' % response.url)
            loader.add_value('url', response.url)
            loader.add_value('collection_name', self.name)
            loader.add_value('website', self.website)
            if contents == '':
                self.logger.warning(' url: %s msg: %s' % (response.url, ' content is None'))
            loader.add_value('content', contents)
            return loader.load_item()
