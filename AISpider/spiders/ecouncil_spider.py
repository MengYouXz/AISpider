
import scrapy
import requests
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
from datetime import date, datetime, timedelta
from common._date import get_all_month
from common.set_date import get_this_month
from common._date import get_all_month
from AISpider.items.ecouncil_items import EcouncilItem



# 最早数据01/01/2003
# 第一个时间选择 2003-2024.04.01 161条
#   第二个时间选择 2002 -2024.04.01 160条
class EcouncilSpider(scrapy.Spider):
    name = "bayside"
    allowed_domains = ["ecouncil.bayside.vic.gov.au"]
    start_urls = [
        "https://ecouncil.bayside.vic.gov.au/eservice/daEnquiryInit.do?docType=5&nodeNum=480394"]
    custom_settings = {
        'LOG_STDOUT': True,
        #"'LOG_FILE': 'scrapy_ecouncil.log',
        # 'DOWNLOAD_TIMEOUT': 1200
    }

    def __init__(self,run_type=None,days=None,*args, **kwargs):
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
        }
        self.run_type = run_type
        if days == None:
        # 如果没有传days默认为这个月的数据
            self.days = get_this_month()
        else:
            now = datetime.now()
            days = int(days)
            date_from = (now - timedelta(days)).date().strftime('%d/%m/%Y')
            # 这里计算出开始时间 设置到self.days
            self.days = date_from


    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, dont_filter=True,method='GET',headers=self.headers)


    def parse(self, response):
        #搜索第一个时间表，第二个置空
        #'dateFrom': '01/01/2003',
        #'dateTo': '01/04/2024',
        #第二个
        #'detDateFromString': '',
        # 'detDateToString': '',
        if self.run_type == 'all':self.days = '01/01/2003'
        end_time = datetime.now().date().strftime('%d/%m/%Y')
        paylods1 = {
            "number": '',
            'dateFrom': self.days,
            'dateTo': end_time,
            'detDateFromString': '',
            'detDateToString': '',
            'streetName': '',
            'suburb': '0',
            'unitNum': '',
            'houseNum': '0',
            'searchMode': 'A',
            'submitButton': 'Search'
        }
        # paylods请求一次 paylods2请求一次
        paylods2 = {
            "number": '',
            'dateFrom': '',
            'dateTo': '',
            'detDateFromString': self.days,
            'detDateToString': end_time,
            'streetName': '',
            'suburb': '0',
            'unitNum': '',
            'houseNum': '0',
            'searchMode': 'A',
            'submitButton': 'Search'
        }
        if self.run_type == 'first' or self.run_type =='all':
            search_response_url = 'https://ecouncil.bayside.vic.gov.au/eservice/daEnquiry.do?'
            data= ''
            for d in paylods1:
                data += (d + "=")
                data += (paylods1[d] + "&")
            data = data.strip("&")
            search_response_url = search_response_url +data
            yield Request(url=search_response_url,callback=self.parse_search,method='GET',headers=self.headers,dont_filter=False)
        if self.run_type == 'second'or self.run_type =='all':
            search_response_url = 'https://ecouncil.bayside.vic.gov.au/eservice/daEnquiry.do?'
            data = ''
            for d in paylods2:
                data += (d + "=")
                data += (paylods2[d] + "&")
            data = data.strip("&")
            search_response_url = search_response_url + data
            yield Request(url=search_response_url, callback=self.parse_search, method='GET', headers=self.headers,dont_filter=False)



    def parse_search(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')

        number = soup.select_one('label')
        number = int(number.get_text().replace(" ",'').replace("RecordsFound",'').strip())
        if number == 0:
            print('搜索到0条结果')
            pass
        else:
            print(f'搜索到{number}条结果')
            for i in range(number):
                url = f'https://ecouncil.bayside.vic.gov.au/eservice/daEnquiryDetails.do?index={i}'
                yield Request(url,headers=self.headers,callback=self.parse_detail,dont_filter=False)

    def parse_detail(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(response.text)
        item = EcouncilItem()
        # Application Information
        key_list = soup.select('.rowDataOnly .key')
        inputfields = soup.select('.rowDataOnly .inputField')
        data_dick = {}
        key_lists = []
        inputfield_lists = []
        for key in key_list:
            key_lists.append(key.text)
        for inputfield in inputfields:
            inputfield_lists.append(inputfield.text)

        data_dick['Property Details'] = ''
        if len(key_lists) == len(inputfield_lists):
            for x, y in zip(key_lists, inputfield_lists):
                data_dick[x] = y
        else:
            key_lists.reverse()
            inputfield_lists.reverse()
            for x, y in zip(key_lists, inputfield_lists):
                data_dick[x] = y
            temp_num = 1+len(inputfield_lists)-len(key_lists)
            inputfield_lists.reverse()
            temp_str = ''
            for i in range(temp_num):
                temp_str += (inputfield_lists[i]+';')
            data_dick['Property Details'] = temp_str
        temp_list = list(data_dick.keys())
        item['app_number'] = data_dick['Application No.']if 'Application No.' in temp_list else None
        item['description'] = data_dick['Property Details']if 'Property Details' in temp_list else None
        item['type_of_work'] = data_dick['Type of Work']if 'Type of Work' in temp_list else None
        try:
            lodged_date = data_dick['Date Lodged'].strip()
            time_array = time.strptime(lodged_date, '%d/%m/%Y')
            temp_data = int(time.mktime(time_array))
            item['date_lodged'] = temp_data if lodged_date else None
        except:
            item['date_lodged'] = None
        item['cost'] = data_dick['Cost of Work']if 'Cost of Work' in temp_list else None
        item['determination_details'] = data_dick['Determination Details']if 'Determination Details' in temp_list else None

        try:
            lodged_date = data_dick['Determination Date'].strip()
            time_array = time.strptime(lodged_date, '%d/%m/%Y')
            temp_data = int(time.mktime(time_array))
            item['determination_date'] = temp_data if lodged_date else None
        except:
            item['determination_date'] = None

        # Application Stages And Status
        # th = soup.select('.table-responsive .sub-heading th')
        td = soup.select('.table-responsive .datatable_alternate td')
        add_str = ''
        add_list = ['Milestone','Stage Description','Opened','Target Date','Completed Date','Status']
        tmp = 0
        for d in td:
            add_str += add_list[tmp]+':'+d.text+';'
            tmp +=1
            if tmp == 6:
                tmp = 0
        # print(add_str)
        item['application_stages_and_status'] = add_str
        # Application Documents
        document = soup.select('.table-responsive a')
        document_url_list = ''
        for d in document:
            document_url_list += "https://ecouncil.bayside.vic.gov.au/"+d.get('href')+';'
        # print(document_url_list)
        item['document'] = document_url_list

        print(item)
        yield item

