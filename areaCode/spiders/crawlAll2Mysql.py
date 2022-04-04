# coding=utf-8
import requests
from bs4 import BeautifulSoup
import pymysql
import time

cownTr = []
haveDealCity = []
class CrawlAllCode(object):

    def __init__(self):
        # self.db = pymysql.connect("127.0.0.1", "3307","root", "123456", "demo", charset="utf8mb4")
        self.db = pymysql.connect(host="localhost", port=3307, database="demo", user="root", password="123456",
                                  charset="utf8mb4")
        self.main()
        self.db.close()

    def main(self):
        base_url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2021/'
        # 山东省
        crawl_province_url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2021/46.html'
        # 德州市
        crawl_city_url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2021/46/4604.html'
        # 平原县
        # crawl_conuty_url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/37/14/371426.html'
        trs = self.get_resp(base_url, 'provincetr', 0)

        # 循环每一行
        for tr in trs:
            # 循环每个省
            for td in tr:


                if td.find('a') == None:
                    print('======没找到===')
                    continue
                province_name = td.a.get_text()
                province_code = td.a.get('href').replace('.html', '')
                province_url = base_url + td.a.get('href')
                print('province_name'+ province_name)
                if crawl_province_url != province_url:
                #if 1==2:
                    continue
                else:
                    trs = self.get_resp(province_url, None, 0)
                    values = [tr for tr in trs[1:]]
                    for tr in trs[1:]:  # 循环每个市
                        city_code = tr.find_all('td')[0].string[0:4]
                        city_name = tr.find_all('td')[1].get_text()
                        city_url = base_url + tr.find_all('td')[1].a.get('href')
                        if crawl_city_url != city_url:
                        #if 1 == 2:
                            continue
                        else:
                            trs = self.get_resp(city_url, None, 0)
                            datas = []
                            for tr in trs[1:]:  # 循环每个区
                                #county_code = tr.find_all('td')[0].string.rstrip('0')
                                county_code = tr.find_all('td')[0].string[0:6]
                                county_name = tr.find_all('td')[1].get_text()
                                classNameList = tr.attrs['class']

                                # 如果不是区 则放入
                                isCity = False
                                if ('towntr' in classNameList):
                                    if county_code in haveDealCity:
                                        print ('特殊数据已处理：' , county_code)
                                        continue

                                    isCity = True
                                    haveDealCity.append(county_code)
                                    print ("========市下面不是=======",county_code)
                                    nextUrl = city_url
                                    county_name = city_name

                                #print (county_name)
                                data = [province_code, province_name, city_code, city_name, county_code, county_name]
                                countSql = 'select count(id) from area_code_new where county_code=' + county_code
                                count = self.connect_mysql(countSql, None)

                                if (count[0][0] == 0):
                                    datas.append(data)
                                if tr.find('a') == None:
                                    print('======没找到===')
                                    continue
                                #country_url = base_url + province_code + '/' + tr.find_all('td')[1].a.get('href')
                                nextUrl = base_url + province_code + '/' + tr.find_all('td')[1].a.get('href')
                                if isCity :
                                    nextUrl = city_url


                                # if crawl_conuty_url != country_url:
                                #   continue
                                # else:
                                self.crawlTownDown(tr, base_url, nextUrl, isCity)


                            sql = "insert into area_code_new (id,province_code,province_name,city_code,city_name,county_code,county_name,del_flag,revision,created_time,created_by,`updated_by`,`updated_time`) values (REPLACE(UUID(), '-', ''),%s,%s,%s,%s,%s,%s,0,0,NOW(),'root','root',now()) ON DUPLICATE KEY UPDATE province_code = VALUES(province_code)"
                            # print('datas:',datas)
                            if datas:
                                self.connect_mysql(sql, datas)
                            else:
                                print ("省市区需要插入area_code为空")



                    print('============按理说执行完了==============')


    def crawlTownDown(self, tr, base_url, nextUrl, isCity):

        datas = []
        # http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/37/01/370102.html
        # 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/64/6401.html'
        if tr.find('a') == None:
            print('======没找到===')
            return

        # 非正常 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2021/44/19/441900005.html'
        # 正常  'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2021/44/18/441802.html'

        trs = self.get_resp(nextUrl, 'towntr', 0)
        if trs == []:
            # 插入社区/村
            self.getVillage(nextUrl)
        # values = [tr for tr in trs[1:]]
        # for o in cownTr:
        #     values.append(o)
        # 循环数据的每一行 镇/街道
        for tr in trs:
            if tr.find_all('td')[1].a != None:
                datas = []
                town_code = tr.find_all('td')[0].string[0:9]
                # if(town_code>1)
                town_name = tr.find_all('td')[1].string
                data = [town_code, town_name, town_code[0:6], '4', '']
                # print(town_name)
                datas.append(data)
                nextUrl = tr.find_all('td')[1].a.get('href')
                if isCity :
                    village_url = base_url + town_code[0:2] + '/' + '/' + nextUrl
                else :
                    village_url = base_url + town_code[0:2] + '/' + town_code[2:4] + '/' + nextUrl

                sql = "INSERT INTO `area_code_child_new`(`id`,`code`, `name`,`p_code`, `level`, `catagory`,`created_time`,`created_by`,`updated_by`,`updated_time`)  values (REPLACE(UUID(), '-', ''),%s,%s,%s,%s,%s,now(),'root','root',now()) ON DUPLICATE KEY UPDATE code = VALUES(code)"
                if datas:
                    self.connect_mysql(sql, datas)
                else:
                    print ("街镇需要插入area_code为空")
                # 插入社区/村
                self.getVillage(village_url)


    def getVillage(self, village_url):
        trs = self.get_resp(village_url, None, 0)
        if trs == None:
            print ('5级地址:'+village_url)
            return
        datas = []
        for tr in trs[1:]:  # 循环每个 社区/村
            village_code = tr.find_all('td')[0].string[0:12]
            catagory = tr.find_all('td')[1].string
            village_name = tr.find_all('td')[2].string
            data = [village_code, village_name, village_code[0:9], '5', catagory]
            # print(village_name)
            countSql = 'select count(id) from area_code_child_new where code=' + village_code
            count = self.connect_mysql(countSql, None)
            if (count[0][0] > 0):
                continue

            datas.append(data)
        sql = "INSERT INTO `area_code_child_new`(`id`,`code`, `name`,`p_code`, `level`, `catagory`,`created_time`,`created_by`,`updated_by`,`updated_time`)  values (REPLACE(UUID(), '-', ''),%s,%s,%s,%s,%s,now(),'root','root',now()) ON DUPLICATE KEY UPDATE code = VALUES(code)"
        if datas:
            self.connect_mysql(sql, datas)
        else:
            print ("社区/村需要插入area_code为空，village_url:",village_url)

    def get_resp(self, url, attr, retryTime):

        #time.sleep(1)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Cookie': 'x-version-extension=2.0.18; x-access-token=e2c5f45ffe5e3e12e94e8a7fa3145457a648639b4d059726bcf5c5b52a2de3aef5d4dfa2a50e0f5b5780220060f40cd1681dd1f64d8ffeeb43f92640381b240d'
        }
        resp = requests.get(url, headers=headers)
        #resp = requests.get(url)
        # print(resp.text)
        resp.encoding = 'utf-8'  # 编码转换
        if (resp.status_code != 200):
            print('request fail,code=', resp.status_code)
            while retryTime < 5:
                print('重试第', int(retryTime), '次')
                return self.get_resp(url, attr, retryTime + 1)
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
