#!/usr/bin/python
# -*- coding:utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.items import SpiderItem
from web_news.misc.filter import Filter
from web_news.misc.spiderredis import SpiderRedis
import time
class FjjgSpider(CrawlSpider):
    name = 'fjjg'
    webname = ''
    download_delay = 0.2
    allowed_domains = ['fjdj.fjsen.com']
    start_urls = ['http://fjdj.fjsen.com/']

    rules = [
	Rule(LinkExtractor(allow=("node",)),follow=True),
        Rule(LinkExtractor(allow=("content")), callback='get_news',follow=True),
    ]

    def get_news(self,response):
	try:
            l = ItemLoader(item=SpiderItem(),response=response)
            l.add_value('title', response.xpath('//div[@class="left"]/h1/strong/text()').extract())
            l.add_value('title', response.xpath('//div[@id="new_subject_id"]/font/text()').extract())

            l.add_value('date',response.xpath('//span[@id="pubtime_baidu"]/text()').extract())
            l.add_value('date',response.xpath('//div[@class="cc"]/text()').extract())

            date = ''.join(l.get_collected_values('date'))
            #date = time.strptime(date.split()[0], u'%Y-%m-%d')
            #l.replace_value('date', time.strftime('%Y-%m-%d %H:%M:%S', date))

            l.add_value('content',response.xpath('//td[@id="new_message_id"]/p/text()').extract())
            l.add_value('content',response.xpath('//div[@id="new_message_id"]/p/text()').extract())
            l.add_value('content',response.xpath('//div[@id="zoom"]/b/font/a/text()').extract())

 
            l.add_value('url', response.url)
            l.add_value('collection_name', self.name)
            return l.load_item()
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            l = ItemLoader(item=SpiderItem(), response=response)
            l.add_value('title', '')
            l.add_value('date', '1970-01-01 00:00:00')
            l.add_value('source', '')
            l.add_value('content', '')
            l.add_value('url', response.url)
            l.add_value('collection_name', self.name)
            l.add_value('website', self.website)
            return l.load_item()
