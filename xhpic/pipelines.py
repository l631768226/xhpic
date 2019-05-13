# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import urllib
import urllib.request
import os
import random
from xhpic.settings import USER_AGENTS

class XhpicPipeline(object):
    def process_item(self, item, spider):
        headers = {
            'User-Agent': random.choice(USER_AGENTS)
        }
        req = urllib.request.Request(url=item['addr'],headers=headers)
        res = urllib.request.urlopen(req)
        file_name = os.path.join(r'E:\tmp\xh',item['name']+'.jpg')
        with open(file_name,'wb') as fp:
            fp.write(res.read())
        return item
