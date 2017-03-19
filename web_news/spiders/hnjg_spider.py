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
class HnjgSpider(CrawlSpider):
    name = 'hnjg'
    webname = ''
    download_delay = 0.2
    allowed_domains = ['www.hnjgdj.gov.cn',
    ]

    start_urls = ['http://www.hnjgdj.gov.cn/']

    rules = [
	Rule(LinkExtractor(allow=("hnxw","gnyw","gjzx","jscj","kjjy")),follow=True),
        Rule(LinkExtractor(allow=("info")), callback='get_news',follow=True),
    ]

    def get_news(self,response):
        l = ItemLoader(item=SpiderItem(),response=response)
        l.add_value('title', response.xpath('//h2[@id="tti"]/text()').extract())
	l.add_value('title', response.xpath('//h2[@id="tti"]/font/text()').extract())
	l.add_value('title', response.xpath('//h2[@class="info_message"]/h2/font/text()').extract())

        l.add_value('date',response.xpath('//div[@class="info_message"]/h5/text()').extract())

        r1 = r"\d{4}\-\d{1,2}\-\d{1,2}"
	date0 = re.compile(r1)
	date = ''.join(l.get_collected_values('date'))
	date1 = date0.findall(date)
        l.replace_value('date', date1[0]+" "+"00:00:00")

        l.add_value('content',response.xpath('//div[@class="info_message"]/div/p/text()').extract())
        l.add_value('content',response.xpath('//div[@class="info_message"]/div/p/span/text()').extract())
        l.add_value('content',response.xpath('//div[@class="info_message"]/div/p/span/span/text()').extract())
 
        l.add_value('url', response.url)
        l.add_value('collection_name', self.name)

        return l.load_item()

