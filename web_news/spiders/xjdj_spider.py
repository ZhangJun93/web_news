# -*- coding:utf-8 -*-
from scrapy.spiders import Rule
from scrapy.spiders import CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.items import SpiderItem
from web_news.misc.spiderredis import SpiderRedis
import re


class XjSpider(SpiderRedis):
    name = 'xinjiangdj'
    website = u'新疆党建网'
    download_delay = 0.1
    allowed_domains = ['www.xjkunlun.cn']
    start_urls = ['http://www.xjkunlun.cn/']

    rules = [
        # 只抓取2015以后的新闻, 太久远新闻存在内容抓取匹配问题
        Rule(LinkExtractor(allow=r'/201[5-9]/[0-9]+.htm',
                           deny=('/iptv', '/wlsp', '/mobile', '/kxj', '/xzzx', '/sy.xjkunlun', '/ycjy', '/djkw', '/index')),
             callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=('/xinwen', '/gzgz', '/dswx', '/ldjh', '/dkyj', '/lgbgz', '/wnfw'),
                           deny=('/iptv', '/wlsp', '/mobile', '/kxj', '/xzzx', '/sy.xjkunlun', '/ycjy', '/djkw')), follow=True),
    ]

    def parse_item(self, response):
	loader = ItemLoader(item=SpiderItem(), response=response)
        contents = ''
        try:
            title = response.xpath(r'//td[@class="STYLE1"]/div//text()').extract_first()

            content_list = response.xpath(r'//div[@class="container"]/div[2]/table/tbody/tr/td/p/text()').extract()
            if len(content_list) == 0:
                # 定义另一种匹配形式
                content_list = response.xpath(r'//*[@id="00010"]/table[2]/tbody/tr[2]/td/p/text()').extract()
            for content in content_list:
                contents = contents + content

            # 定义日期的两种匹配规则
            date_text = response.xpath(r'//*[@id="00010"]/table[2]/tbody/tr[1]/td/p/text() | //*[@id="00010"]/table[1]/tbody/tr[3]/td/text()').extract_first()
            match = re.search(r'(20[0-9]{2}-[0-9]{2}-[0-9]{2})', date_text)
            date = match.group(1)

            ### print info
            # try:
            # print 'title, ', title.encode('GB18030')
            # print 'url, ', response.url
            # print "date, ", date
            # print "content, ", contents.encode('GB18030')
            # except Exception as e:
            #     print " error : ", e

            loader.add_value('title', title)
            loader.add_value('date', date)
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
