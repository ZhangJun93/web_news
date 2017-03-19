# -*- coding: utf-8 -*-
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.items import SpiderItem
from scrapy.spiders import CrawlSpider, Request
from web_news.misc.spiderredis import SpiderRedis
import time
import re


class NmgSpider(SpiderRedis):
    name = 'nmgdj'
    website = u'内蒙古机关党建网'
    allowed_domains = ['nmgjgdj.gov.cn']
    start_urls = ['http://www.nmgjgdj.gov.cn/']

    rules = [
        Rule(LinkExtractor(allow=r'/t[0-9_]+.html'), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=('/gwdt', '/jgdjxx', '/djtt', '/dflzjs', '/zzjs', '/sxjs', '/ghgz', '/tqgz', '/bfgz', '/jypx', '/wjjh')), callback='find_urls', follow=True),
       # Rule(LinkExtractor(allow='/zt/'), follow=True)
    ]

    custom_settings = {
        'CLOSESPIDER_TIMEOUT': 3600,
    }

    def find_urls(self, response):
        if response.body.find('下一页') != -1:
            try:
                url_new = ""
                page_num = int(re.search(r'countPage = ([0-9]+)', response.body).group(1))
                for i in range(page_num - 1):
                    url_new = response.url + "index_" + str(i + 1) + ".html"
                    yield Request(url_new)
            except Exception as e:
                self.logger.error('can not find next page url, error url: %s, error msg: %s', (response.url, e))

    def parse_item(self, response):
        loader = ItemLoader(item=SpiderItem(), response=response)
        contents = ''
        try:
            title = response.xpath('//div[@class="bt font24_lan"]/text()').extract_first()

            # 1.利用正文信息匹配日期，但是复杂，可能并不是每个都匹配
            # text = response.xpath('//div[@class="lysj"]/ul/li[3]/text()').extract_first()
            # match = re.search(r'([0-9]{4})[^\x00-\xff]([0-9]{2})[^\x00-\xff]([0-9]{2})[^\x00-\xff]', text)
            # if match:
            #     date = match.group(1) + match.group(2) + match.group(3)
            #     dateArray = time.strptime(date, "%Y%m%d")
            #     otherStyleDate = time.strftime("%Y-%m-%d", dateArray)
            #     print "date, ", otherStyleDate

            # 2. 利用url提取日期，简洁快速
            match = re.search(r't(20[0-9]{6})', response.url)
            date = match.group(1)
            # 转换日期格式
            dateArray = time.strptime(date, "%Y%m%d")
            otherStyleDate = time.strftime("%Y-%m-%d", dateArray)

            # 这里//text() 等价于提取当前标签下所有含有文本的标签的文本信息,区别于/text()
            content_list = response.xpath(r'//div[@class="nr font14_lan"]/descendant-or-self::p//text()').extract()
            for content in content_list:
                contents = contents + content

            # ### print info
            # try:
            #     ### str.encode('GB18030') 解决cmd中打印中文报错问题
            #     print 'title, ', title.encode('GB18030')
            #     print 'url, ', response.url
            #     print "date, ", otherStyleDate
            #     print "content, ", contents.encode('GB18030')
            # except Exception as e:
            #     print " error : ", e

            loader.add_value('title', title)
            loader.add_value('date', otherStyleDate)
        except Exception as e:
            # self.logger.error('error url: %s error msg: %s' % (response.url, e))
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
