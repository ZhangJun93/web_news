#!/usr/bin/python
# -*- coding:utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.items import SpiderItem
from web_news.misc.filter import Filter
from web_news.misc.spiderredis import SpiderRedis
import time

class YgwangSpider(CrawlSpider):
    name = 'ygw'
    webname = '央广网'
    download_delay = 0.2
    allowed_domains = ['www.cnr.cn',
		       'news.cnr.cn',
		       'tech.cnr.cn']
    start_urls = ['http://www.cnr.cn/']

    rules = [
	Rule(LinkExtractor(allow=("index"),deny=("qqq")),follow=True),
        Rule(LinkExtractor(allow=r't(\d+)_(\d+)',deny=("tjch","zhuanti","pic")), callback='get_news',follow=True),
    ]

    def get_news(self,response):
	try:
	    l = ItemLoader(item=SpiderItem(),response=response)
            l.add_value('title', response.xpath('//div[@class="wh645 left"]/p[1]/text()').extract())
	    l.add_value('title', response.xpath('//p[@class="f22 lh30 yahei"]/a/text()').extract())
	    l.add_value('title', response.xpath('//p[@class="f22 lh40 fb"]/text()').extract())

            l.add_value('date',response.xpath('//p[@class="lh30 left f14 yahei"]/text()').extract())
	    l.add_value('date',response.xpath('//span[@id="pubtime_baidu"]/text()').extract())
	    l.add_value('title', response.xpath('//div[@class="top"]/p/text()').extract())

            date = ''.join(l.get_collected_values('date'))
            #date = time.strptime(date.split()[0], '%Y-%m-%d')
            #l.replace_value('date', time.strftime('%Y-%m-%d %H:%M:%S', date))

            l.add_value('content',response.xpath('//div[@class="TRS_Editor"]/p/text()').extract())
            l.add_value('content',response.xpath('//div[@class="TRS_Editor"]/div/p/text()').extract())
	    l.add_value('content',response.xpath('//div[@class="sanji_left"]/p/text()').extract())
	    l.add_value('content',response.xpath('//div[@class="news-con"]/div/p/text()').extract())
	    l.add_value('content',response.xpath('//div[@class="news-con"]/div/div/div/font/text()').extract())
	    l.add_value('content',response.xpath('//div[@id="news-con"]/div/p/text()').extract())
	    l.add_value('content',response.xpath('//div[@id="news-con"]/div/font/font/p/text()').extract())

            l.add_value('url', response.url)
            l.add_value('collection_name', self.name)
	    url = response.url

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
