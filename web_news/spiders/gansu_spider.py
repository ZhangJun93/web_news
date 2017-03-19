#!/usr/bin/python
# -*- coding:utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.items import SpiderItem
from web_news.misc.filter import Filter
from web_news.misc.spiderredis import SpiderRedis
import time
import re
class GansuSpider(CrawlSpider):
    name = 'gansu'
    webname = ''
    download_delay = 0.2
    allowed_domains = ['www.szgw.gansu.gov.cn']

    start_urls = ['http://www.szgw.gansu.gov.cn/']

    rules = [
	Rule(LinkExtractor(allow=("channels","admin")),follow=True),
        Rule(LinkExtractor(allow=("contents")), callback='get_news',follow=True),
    ]

    def get_news(self,response):
        l = ItemLoader(item=SpiderItem(),response=response)
        l.add_value('title', response.xpath('//h3/text()').extract())

        l.add_value('date',response.xpath('//table[3]/tr[2]/td/table/tr/td/div/text()').extract())

        #r1 = r"\d{4}\-\d{1,2}\-\d{1,2}"
	#date0 = re.compile(r1)
	#date = ''.join(l.get_collected_values('date'))
	#date1 = date0.findall(date)
       # l.replace_value('date', date1[0]+" "+"00:00:00")

        l.add_value('content',response.xpath('//table[3]/tr[2]/td/table/tr[3]/td/div/p/text()').extract())
        l.add_value('content',response.xpath('//table[3]/tr[2]/td/table/tr[3]/td/div/div/p/text()').extract())


 
        l.add_value('url', response.url)
        l.add_value('collection_name', self.name)

        return l.load_item()

