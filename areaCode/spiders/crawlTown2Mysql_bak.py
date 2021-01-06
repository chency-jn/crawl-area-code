# coding=utf-8
import requests
from bs4 import BeautifulSoup
import pymysql
import time


class CrawlTownCode(object):
    def __init__(self):
        self.db = pymysql.connect("127.0.0.1", "root", "123456", "demo", charset="utf8mb4")
        self.main()
        self.db.close()

    def main(self):
        base_url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/'
        trs = self.get_resp(base_url, 'provincetr')
        # 循环每一行
        for tr in trs:
            # 循环每个省
            for td in tr:

                print(td)
                if td.find('a') == None:
                    print('======没找到===')
                    continue
                province_name = td.a.get_text()
                province_code = td.a.get('href').replace('.html','')
                if province_code< '13':
                    continue
                province_url = base_url + td.a.get('href')
                trs = self.get_resp(province_url, None)
                for tr in trs[1:]:  # 循环每个市
                    city_code = tr.find_all('td')[0].string[0:4]
                    city_name = tr.find_all('td')[1].string
                    city_url = base_url + tr.find_all('td')[1].a.get('href')
                    trs = self.get_resp(city_url, None)
                    for tr in trs[1:]:  # 循环每个区
                        county_code = tr.find_all('td')[0].string[0:6]
                        county_name = tr.find_all('td')[1].string
                        if tr.find_all('td')[1].a != None:
                            town_url = base_url +province_code+'/'+ tr.find_all('td')[1].a.get('href')
                            trs = self.get_resp(town_url, None)
                            for tr in trs[1:]:  # 循环每个镇
                                datas = []
                                town_code = tr.find_all('td')[0].string[0:9]
                                town_name = tr.find_all('td')[1].string
                                data = [town_code, town_name,'4','']
                                print(town_name)
                                datas.append(data)
                                village_url = base_url + province_code + '/'+ city_code[2:4] + '/' + tr.find_all('td')[1].a.get('href')
                                trs = self.get_resp(village_url, None)
                                for tr in trs[1:]:  # 循环每个街道/村
                                    village_code = tr.find_all('td')[0].string[0:12]
                                    catagory = tr.find_all('td')[1].string
                                    village_name = tr.find_all('td')[2].string
                                    data = [village_code, village_name, '5', catagory]
                                    print(village_name)
                                    datas.append(data)
                            time.sleep(1)
                            sql = "INSERT INTO `travel`.`area_code_child`(`code`, `name`, `level`, `catagory`)  values (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE code = VALUES(code)"
                            self.connect_mysql(sql, datas)

    def get_resp(self, url, attr):
        resp = requests.get(url)
        resp.encoding = 'gb2312'  # 编码转换
        if(resp.status_code != 200):
            print('request fail,code=',resp.status_code)
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
    CrawlTownCode()
