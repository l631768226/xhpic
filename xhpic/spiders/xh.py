# -*- coding: utf-8 -*-
import scrapy
import os

from xhpic.items import XhpicItem

class XhSpider(scrapy.Spider):
    name = 'xh'
    allowed_domains = ['xiaohuar.com']
    start_urls = ['http://www.xiaohuar.com/list-1-1.html']

    url_set = set()

    def parse(self, response):
        if response.url.startswith("http://www.xiaohuar.com/list-"):
            allPics =  response.xpath('//div[@class="img"]/a')
            for pic in allPics:
#               分别处理每个图片，取出名称及地址
                item = XhpicItem()
                name = pic.xpath('./img/@alt').extract()[0]
                addr = pic.xpath('./img/@src').extract()[0]
                addr = 'http://www.xiaohuar.com' + addr
                item['name'] = name
                item['addr'] = addr

                yield item

        urls = response.xpath("//a/@href").extract()

        for url in urls:
            if url.startswith('http://www.xiaohuar.com/list-'):
                if url in XhSpider.url_set:
                    pass
                else:
                    XhSpider.url_set.add(url)

                    yield self.make_requests_from_url(url)

            else:
                pass