# -*- coding:utf-8 -*-
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.items import SpiderItem
from web_news.misc.spiderredis import SpiderRedis
import time
import re


class GuangXiSpider(SpiderRedis):
    name = 'guangxidj'
    website = u'广西机关党建网'
    allowed_domins = ['www.gxjgdj.com/']
    start_urls = ['http://www.gxjgdj.com/']

    rules = (
        Rule(LinkExtractor(allow=r'/Item/[0-9]+.aspx'), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=r'/Category_[0-9]+/Index.aspx', deny=r'/Category_34'), follow=True),
    )

    custom_settings = {
        'CLOSESPIDER_TIMEOUT': 3600,
    }

    def parse_item(self, response):
        loader = ItemLoader(item=SpiderItem(), response=response)
        contents = ''
        try:
            title = response.xpath(r'//div[@class="article_content"]/h1/span/font/text()').extract_first()
            date_text = response.xpath(r'/html/body/div/div[2]/div[2]/div[3]/div[2]/div[1]/text()[3]').extract_first()
            match = re.search(r'(20\d{2})[^\x00-\xff](\d{2})[^\x00-\xff](\d{2})[^\x00-\xff]', date_text)
            date = match.group(1) + match.group(2) + match.group(3)
            dateArray = time.strptime(date, "%Y%m%d")
            otherStyleDate = time.strftime("%Y-%m-%d", dateArray)

            content_list = response.xpath(r'//div[@class="articlecontent"]//text()').extract()
            for content in content_list:
                contents = contents + content

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
            loader.add_value('date', '1970-01-01')
            loader.add_value('title', '')
        finally:
            #self.logger.info('crawling url: %s' % response.url)
            loader.add_value('url', response.url)
            loader.add_value('collection_name', self.name)
            loader.add_value('website', self.website)
            if contents == '':
                self.logger.warning(' url: %s msg: %s' % (response.url, ' content is None'))
            loader.add_value('content', contents)
            return loader.load_item()
