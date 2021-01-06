# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class AreacodePipeline(object):
    def open_spider(self, spider):
        # 创建my.txt文件，并将字符集设为utf-8
        self.file = open('result2.txt', 'w', encoding='utf-8')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        # 将爬取到的文本保存到my.txt中;当向txt中写入字典,list集合时,使用str()
        self.file.write(str(item) + '\n')
