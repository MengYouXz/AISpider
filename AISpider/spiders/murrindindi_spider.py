import scrapy
from bs4 import BeautifulSoup
from AISpider.items.murrindindi_items import MurrindindiItem
from datetime import datetime
import time
# 每天更新10条数据
# 抽空优化
# 暂时可以跑

class MurrindindiSpider(scrapy.Spider):
    name = "murrindindi"
    allowed_domains = ["www.murrindindi.vic.gov.au"]
    start_urls = ["https://www.murrindindi.vic.gov.au/Your-Property/Planning-and-Building/Planning-and-Development/Planning-applications-on-public-notice"]


    title_list = ['doucuments','description','address','date']

# https://www.murrindindi.vic.gov.au/ files/assets/public/v/1/documents/planning-and-building/planning/planning-applications/25-murchison-street-marysville-3779.pdf
    def parse(self, response):
        item = MurrindindiItem()
        soup = BeautifulSoup(response.text, 'html.parser')
        datas = soup.select('tbody tr td')
        url_list = soup.select('tbody td a')
        temp_list = []
        for url in url_list:
            temp_list.append(url.get('href'))
        # print(temp_list)
        temp = 0
        url_temp = 0
        item_dick = {}
        for data in datas:
            if temp %4 == 0:
                item_dick['app_number'] = data.get_text().strip().split('(')[0].strip()
                url = "https://www.murrindindi.vic.gov.au" + temp_list[url_temp] + ';'
                item_dick['documents'] = url
                url_temp += 1
            elif temp %4 == 1:
                item_dick['description'] = data.get_text().strip()
            elif temp % 4 == 2:
                item_dick['address'] = data.get_text().strip()
            elif temp % 4 == 3:
                lodged_date = data.get_text().strip()
                time_array = time.strptime(lodged_date, '%d/%m/%Y')
                temp_data = int(time.mktime(time_array))
                item_dick['date'] = temp_data if lodged_date else None
                time.sleep(1)
            else:
                print('error')

            if temp %4 == 3 and temp != 0:
                try:
                    item['app_number']=item_dick['app_number']
                except:
                    item['app_number']=None
                try:
                    item['documents'] = item_dick['documents']
                except:
                    item['documents'] = None
                try:
                    item['description'] = item_dick['description']
                except:
                    item['description']=None
                try:
                    item['address'] = item_dick['address']
                except:
                    item['address']=None
                try:
                    item['date'] = item_dick['date']
                except:
                    item['date'] = None
                temp = -1
                time.sleep(1)
                yield item

            temp+=1

        
    


