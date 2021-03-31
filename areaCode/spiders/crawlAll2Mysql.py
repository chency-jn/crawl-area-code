# coding=utf-8
import requests
from bs4 import BeautifulSoup
import pymysql
import time


class CrawlAllCode(object):
    def __init__(self):
        self.db = pymysql.connect("127.0.0.1", "root", "123456", "demo", charset="utf8mb4")
        self.main()
        self.db.close()

    def main(self):
        base_url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/'
        #山东省
        crawl_province_url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/37.html'
        #德州市
        crawl_city_url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/37/3714.html'
        #平原县
        crawl_conuty_url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/37/14/371426.html'
        trs = self.get_resp(base_url, 'provincetr')
        # 循环每一行
        for tr in trs:
            # 循环每个省
            for td in tr:
                datas = []
                print('province_td',td)
                if td.find('a') == None:
                    print('======没找到===')
                    continue
                province_name = td.a.get_text()
                province_code = td.a.get('href').replace('.html', '')
                province_url = base_url + td.a.get('href')
                print('province_name',province_name)
                if crawl_province_url != province_url:
                    continue
                else:
                    trs = self.get_resp(province_url, None)
                    for tr in trs[1:]:  # 循环每个市
                        city_code = tr.find_all('td')[0].string[0:4]
                        city_name = tr.find_all('td')[1].string
                        city_url = base_url + tr.find_all('td')[1].a.get('href')
                        if crawl_city_url != city_url:
                            continue
                        else:
                            trs = self.get_resp(city_url, None)
                            for tr in trs[1:]:  # 循环每个区
                                county_code = tr.find_all('td')[0].string[0:6]
                                county_name = tr.find_all('td')[1].string
                                data = [province_code, province_name, city_code, city_name, county_code, county_name]
                                print('county_data',data)
                                datas.append(data)
                                if tr.find('a') == None:
                                    print('======没找到===')
                                    continue
                                country_url = base_url + province_code + '/' + tr.find_all('td')[1].a.get('href')
                                if crawl_conuty_url != country_url:
                                    continue
                                else:
                                    self.crawlTownDown(tr, base_url, province_code)

                            time.sleep(2)
                    sql = "insert into area_code (province_code,province_name,city_code,city_name,county_code,county_name) values (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE province_code = VALUES(province_code)"
                    self.connect_mysql(sql, datas)

    def crawlTownDown(self, tr, base_url, province_code):
        datas = []
        # http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/37/01/370102.html
        # 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/64/6401.html'
        if tr.find('a') == None:
            print('======没找到===')
            return
        # county_url = base_url + tr.find_all('td')[1].a.get('href')
        country_url = base_url + province_code + '/' + tr.find_all('td')[1].a.get('href')
        trs = self.get_resp(country_url, 'towntr')
        # 循环数据的每一行 镇/街道
        for tr in trs:
            if tr.find_all('td')[1].a != None:
                datas = []
                town_code = tr.find_all('td')[0].string[0:9]
                town_name = tr.find_all('td')[1].string
                data = [town_code, town_name, town_code[0:6], '4', '']
                print(town_name)
                datas.append(data)
                village_url = base_url + town_code[0:2] + '/' + town_code[2:4] + '/' + \
                              tr.find_all('td')[1].a.get('href')
                trs = self.get_resp(village_url, None)
                for tr in trs[1:]:  # 循环每个 社区/村
                    village_code = tr.find_all('td')[0].string[0:12]
                    catagory = tr.find_all('td')[1].string
                    village_name = tr.find_all('td')[2].string
                    data = [village_code, village_name, village_code[0:9], '5', catagory]
                    print(village_name)
                    datas.append(data)
            time.sleep(2)
            sql = "INSERT INTO `area_code_child`(`code`, `name`,`p_code`, `level`, `catagory`)  values (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE code = VALUES(code)"
            self.connect_mysql(sql, datas)

    def get_resp(self, url, attr):
        resp = requests.get(url)
        resp.encoding = 'gb2312'  # 编码转换
        if (resp.status_code != 200):
            print('request fail,code=', resp.status_code)
        else:
            soup = BeautifulSoup(resp.text, 'lxml')
            table = soup.find_all('tbody')[1].tbody.tbody.table
            if attr:
                trs = table.find_all('tr', attrs={'class': attr})
            else:
                trs = table.find_all('tr')
            return trs

    # 连接数据库并插入数据
    def connect_mysql(self, sql, data):
        cursor = self.db.cursor()
        try:
            result = None
            if data:
                if isinstance(data[0], list):
                    cursor.executemany(sql, data)
                else:
                    cursor.execute(sql, data)
            else:
                cursor.execute(sql)
                result = cursor.fetchall()
        except Exception as e:
            print(e)
            self.db.rollback()
        finally:
            cursor.close()
            self.db.commit()  # 提交操作
            return result


if __name__ == '__main__':
    CrawlAllCode()
