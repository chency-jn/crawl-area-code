# coding=utf-8
import codecs
import json
import time

import scrapy

#网上网友的另外一种方式 但是数据总是不全 容易出现意外 所以暂时放弃 有时间再看看
class CountrySpider(scrapy.Spider):
    name = 'country0'
    base_url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/'
    #base_url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/37/3714.html'

    def start_requests(self):
        urls = ['http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/index.html']
        #urls = ['http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/37/3714.html']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if (response.status != 200):
            print("=====request fail===status===",response.status)
        else:
            # l1
            #print('parse:'+str(response))
            for provincetr in response.css('tr.provincetr td'):
                if(len(provincetr.css('a::text').extract()) >= 1):
                    name = provincetr.css('a::text').extract()[0]
                    href = provincetr.css('a::attr(href)').extract()[0]
                    code = href.replace('.html', '')

                    data = {'level': 'l1', 'name': name, 'code': code}
                    self.write_item_to_file(data)
                    yield data
                    next_page = self.base_url + href
                    yield scrapy.Request(url=next_page, callback=self.parse)

            # l2
            citypr = response.css('tr.citytr td a::text').extract()
            print('citypr:' + str(citypr))
            for i in range(0, len(citypr), 2):
                code = citypr[i][0:4]
                name = citypr[i + 1]
                data = {'level': 'l2', 'name': name, 'code': code}
                self.write_item_to_file(data)
                yield data
                next_page = self.base_url + code[0:2] + "/" + code + ".html"
                time.sleep(0.3)
                yield scrapy.Request(url=next_page, callback=self.parse)

            # l3
            countytr1 = response.css('tr.countytr td a::text').extract()
            countytr2 = response.css('tr.countytr td::text').extract()
            print('countytr1:' + str(countytr1))
            print('countytr2:' + str(countytr2))
            for i in range(0, len(countytr1), 2):
                code = countytr1[i][0:6]
                name = countytr1[i + 1]
                data = {'level': 'l3', 'name': name, 'code': code}
                self.write_item_to_file(data)
                self.log(data)
                print("========:"+name)
                yield data
                next_page = self.base_url + code[0:2] + "/" + code[2:4] + "/" + code + ".html"
                time.sleep(0.5)
                yield scrapy.Request(url=next_page, callback=self.parse)
            for i in range(0, len(countytr2), 2):
                code = countytr2[i][0:6]
                name = countytr2[i + 1]
                data = {'level': 'l3', 'name': name, 'code': code}
                yield data

            # l4
            # towntr = response.css('tr.towntr td a::text').extract()
            # print('towntr:' + str(towntr))
            # for i in range(0, len(towntr), 2):
            #     code = towntr[i][0:9]
            #     name = towntr[i + 1]
            #     data = {'level': 'l4', 'name': name, 'code': code}
            #     self.write_item_to_file(data)
            #     self.log(data)
            #     yield data
            #     next_page = self.base_url + code[0:2] + "/" + code[2:4] + "/" + code[4:6] + "/" + code + ".html"
            #     time.sleep(0.5)
            #     yield scrapy.Request(url=next_page, callback=self.parse)


            # l5
            # villagetr = response.css('tr.villagetr td::text').extract()
            # print('villagetr:' + str(villagetr))
            # for i in range(0, len(villagetr), 3):
            #     code = villagetr[i]
            #     catagory = villagetr[i + 1]
            #     name = villagetr[i + 2]
            #     data = {'level': 'l5', 'name': name, 'code': code, 'catagory': catagory}
            #     print(data)
            #     self.write_item_to_file(data)
            #     yield data

    def write_item_to_file(self,item):
     with codecs.open('result.txt', 'ab','utf-8') as f:
         f.write(json.dumps(item))
         f.write('\n')

if __name__ == '__main__':
    t = CountrySpider()
    data = {'level': 'l5', 'name': '\u4e1c\u8857\u6751\u6c11\u59d4\u5458\u4f1a', 'code': '123', 'catagory': '\u9f50\u5e84\u6751\u6c11\u59d4\u5458\u4f1a'}
    t.write_item_to_file(data)