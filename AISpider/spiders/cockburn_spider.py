import requests
import scrapy
from datetime import date, datetime, timedelta
from scrapy.http import Request
from bs4 import BeautifulSoup
from requests import Session
import json
from AISpider.items.cockburn_items import CockburnTtem
from common._date import get_all_month
import time
from common.set_date import get_this_month
class CockburnSpider(scrapy.Spider):
    name = "cockburn"
    allowed_domains = ["ecouncil.cockburn.wa.gov.au"]
    start_urls = ["https://ecouncil.cockburn.wa.gov.au/eProperty/P1/eTrack/eTrackApplicationSearch.aspx?r=P1.WEBGUEST&f=P1.ETR.SEARCH.ENQ"]
    custom_settings = {
        'LOG_STDOUT': True,
        # 'LOG_FILE': 'scrapy_cockburn2.log',
        'DOWNLOAD_TIMEOUT': 1200
    }


    def __init__(self,category=None,days=None,):
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        self.result_url = 'https://ecouncil.cockburn.wa.gov.au/eProperty/P1/eTrack/eTrackApplicationSearchResults.aspx?r=P1.WEBGUEST&f=%24P1.ETR.RESULTS.VIW'
        self.cookie = {
        }
        self.category = category
        if days == None:
            self.days = get_this_month()
        else:
            now = datetime.now()
            days = int(days)
            date_from = (now - timedelta(days)).date().strftime('%d/%m/%Y')
            self.days = date_from
    def start_requests(self):
        if self.category == 'current':
            for item in self.get_current_data():
                yield item
        elif self.category == 'past':
            all_month = get_all_month(self.days, "%d/%m/%Y")
            for index, y_date in enumerate(all_month):
                if y_date == all_month[-1]:
                    break
                start_time = y_date
                end_time = all_month[index + 1]
                judge_result = self.judge_date(start_time)
                if datetime.strptime(self.days, '%d/%m/%Y').timestamp() > datetime.strptime(start_time, '%d/%m/%Y').timestamp() and judge_result==True:continue
                if self.days.split('/')[1] == start_time.split('/')[1] and self.days.split('/')[2] == start_time.split('/')[2]:
                    start_time = self.days
                print(start_time + "-----" + end_time)
                if start_time == '01/05/2024':
                    for item in self.get_past_data(start_date=start_time,end_date=end_time):
                        yield item
    def judge_date(self,start_time):
        if self.days.split('/')[2] == start_time.split('/')[2]:
            if self.days.split('/')[1] == start_time.split('/')[1]:
                return False
            else:return True
        else:
            return False

    def get_current_data(self):
        session = Session()
        proxy = {'https': 'http://127.0.0.1:8888'}
        resp = session.get(url=self.start_urls[0],headers=self.headers,)
        cookies = session.cookies.get_dict()
        self.cookie = cookies
        from_data = CockburnSpider.deal_form_data(resp)
        session.post(url=self.start_urls[0],headers=self.headers,data=from_data,)
        resp = session.get(url=self.result_url,headers=self.headers,)
        for item in self.get_details(resp):
            yield item
        
        page_num = 2
        #获取下一页
        while True:
            from_data = CockburnSpider.deal_form_data2(resp,num=page_num)
            next_resp = session.post(url=self.result_url,headers=self.headers,data=from_data,cookies=self.cookie)
            for item in self.get_details(next_resp):
                if item ==None:break
                yield item
            resp = next_resp
            page_num+=1

    def get_past_data(self,start_date,end_date):
        session = Session()
        proxy = {'https': 'http://127.0.0.1:8888'}
        resp = session.get(url=self.start_urls[0],headers=self.headers,)
        cookies = session.cookies.get_dict()
        self.cookie = cookies
        from_data = CockburnSpider.deal_form_data4(resp,start_date,end_date)
        status_ = session.post(url=self.start_urls[0],headers=self.headers,data=from_data,)
        resp = session.get(url=self.result_url,headers=self.headers,)
        judge = self.judge(resp)
        if judge == True:
            for item in self.get_details(resp):
                yield item
        else:
            return None
        page_num = 2
        #获取下一页
        while True:
            from_data = CockburnSpider.deal_form_data2(resp,num=page_num)
            next_resp = session.post(url=self.result_url,headers=self.headers,data=from_data,cookies=self.cookie)
            judge = self.judge(next_resp)
            if judge == True:
                for item in self.get_details(resp):
                    yield item
            else:
                break

            for item in self.get_details(next_resp):
                if item ==None:break
                yield item
            resp = next_resp
            page_num+=1

    def judge(self,response):
        soup = soup = BeautifulSoup(response.text, "html.parser")
        error = soup.select_one("title").get_text()
        if 'Object moved' in error: return None
        if 'Error' in error: return None
        if 'Application Tracking' in error: return None
        return True

    def deal_url_list(self,response):
        soup = BeautifulSoup(response.text, "html.parser")
        error = soup.select_one('title').get_text()
        if 'Object moved' in error: return None
        if 'Error' in error: return None
        if 'Application Tracking' in error: return None
        app_id_list = soup.select('.noScriptLinkButton')
        temp_list = []
        for app_id in app_id_list:
            temp = str(app_id)
            temp = temp.split('value=')[1].split('"')[1]
            try:
                int(app_id)
                break
            except:
                if '/' in temp:
                    temp_list.append(f"https://ecouncil.cockburn.wa.gov.au/eProperty/P1/eTrack/eTrackApplicationDetails.aspx?r=P1.WEBGUEST&f=%24P1.ETR.APPDET.VIW&ApplicationId={temp}")
        # 
        return temp_list

    def get_details(self,request):
        url_list = self.deal_url_list(request)
        if url_list is None: return None
        temp_num = 2
        for url in url_list:
            from_data = CockburnSpider.deal_form_data3(request,temp_num)
            temp_num+=1
            yield Request(url,callback=self.parse,body=json.dumps(from_data))

    @staticmethod
    def deal_form_data(response):
        soup = BeautifulSoup(response.text, "html.parser")
        __VIEWSTATE = soup.select_one("#__VIEWSTATE").get('value')
        __EVENTVALIDATION = soup.select_one("#__EVENTVALIDATION").get('value')
        from_data ={
            'ctl00_Content_ajaxToolkitManager_HiddenField': '',
            '__EVENTTARGET': 'ctl00$Content$btnSearch',
            '__EVENTARGUMENT':'' ,
            '__VIEWSTATE': __VIEWSTATE,
            '__VIEWSTATEGENERATOR': 'CA8B432D',
            '__SCROLLPOSITIONX': 0,
            '__SCROLLPOSITIONY': 1212,
            '__EVENTVALIDATION': __EVENTVALIDATION,
            'ctl00$Content$txtApplicationID$txtText': '',
            'ctl00$Content$txtDateFrom$txtText': '01/01/2012',
            'ctl00$Content$txtDateTo$txtText': '10/04/2024',
            'ctl00$Content$txtDescription$txtText': '',
            'ctl00$Content$ddlApplicationType$elbList': 'all',
            'ctl00$Content$ddlStatus$elbList': 'C',
            'ctl00$Content$txtStreetNoFrom$txtText': '',
            'ctl00$Content$txtStreetNoTo$txtText': '',
            'ctl00$Content$txtStreet$txtText': '',
            'ctl00$Content$txtStreetType$txtText':'' ,
            'ctl00$Content$txtSuburb$txtText': '',
            'ctl00$Content$txtPlanNo$txtText': '',
            'ctl00$Content$txtPlanType$txtText': '',
            'ctl00$Content$txtLotNo$txtText': '',
            'ctl00$Content$txtParcelType$txtText': ''
        }
        return from_data

    @staticmethod
    def deal_form_data2(response,num):
        soup = BeautifulSoup(response.text, "html.parser")
        __VIEWSTATE = soup.select_one("#__VIEWSTATE").get('value')
        __EVENTVALIDATION = soup.select_one("#__EVENTVALIDATION").get('value')
        __VIEWSTATEGENERATOR = soup.select_one("#__VIEWSTATEGENERATOR").get('value')
        from_data ={
            '__EVENTTARGET': 'ctl00$Content$cusResultsGrid$repWebGrid$ctl00$grdWebGridTabularView',
            '__EVENTARGUMENT': f'Page${num}',
            '__VIEWSTATE': __VIEWSTATE,
            '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
            '__SCROLLPOSITIONX': 0,
            '__SCROLLPOSITIONY': 843,
            '__EVENTVALIDATION': __EVENTVALIDATION,
        }
        return from_data

    @staticmethod
    def deal_form_data3(response,temp_num):
        soup = BeautifulSoup(response.text, "html.parser")
        __VIEWSTATE = soup.select_one("#__VIEWSTATE").get('value')
        __EVENTVALIDATION = soup.select_one("#__EVENTVALIDATION").get('value')
        __VIEWSTATEGENERATOR = soup.select_one("#__VIEWSTATEGENERATOR").get('value')
        from_data ={
            '__EVENTTARGET': f'ctl00$Content$cusResultsGrid$repWebGrid$ctl00$grdWebGridTabularView$ctl0{temp_num}$ctl01',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': __VIEWSTATE,
            '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
            '__SCROLLPOSITIONX': '0',
            '__SCROLLPOSITIONY': '100',
            '__EVENTVALIDATION': __EVENTVALIDATION,
        }
        return from_data

    @staticmethod
    def deal_form_data4(response,start_date,end_date):
        soup = BeautifulSoup(response.text, "html.parser")
        __VIEWSTATE = soup.select_one("#__VIEWSTATE").get('value')
        __EVENTVALIDATION = soup.select_one("#__EVENTVALIDATION").get('value')
        __VIEWSTATEGENERATOR = soup.select_one("#__VIEWSTATEGENERATOR").get('value')
        from_data ={
            'ctl00_Content_ajaxToolkitManager_HiddenField': '',
            '__EVENTTARGET': 'ctl00$Content$btnSearch',
            '__EVENTARGUMENT':'' ,
            '__VIEWSTATE': __VIEWSTATE,
            '__VIEWSTATEGENERATOR': 'CA8B432D',
            '__SCROLLPOSITIONX': 0,
            '__SCROLLPOSITIONY': 1212,
            '__EVENTVALIDATION': __EVENTVALIDATION,
            'ctl00$Content$txtApplicationID$txtText': '',
            'ctl00$Content$txtDateFrom$txtText': start_date,
            'ctl00$Content$txtDateTo$txtText': end_date,
            'ctl00$Content$txtDescription$txtText': '',
            'ctl00$Content$ddlApplicationType$elbList': 'all',
            'ctl00$Content$ddlStatus$elbList': 'P',
            'ctl00$Content$txtStreetNoFrom$txtText': '',
            'ctl00$Content$txtStreetNoTo$txtText': '',
            'ctl00$Content$txtStreet$txtText': '',
            'ctl00$Content$txtStreetType$txtText':'' ,
            'ctl00$Content$txtSuburb$txtText': '',
            'ctl00$Content$txtPlanNo$txtText': '',
            'ctl00$Content$txtPlanType$txtText': '',
            'ctl00$Content$txtLotNo$txtText': '',
            'ctl00$Content$txtParcelType$txtText': ''
        }
        return from_data


    def parse(self, response):
        item = CockburnTtem()
        soup = BeautifulSoup(response.text, "html.parser")
        data = soup.select('#ctl00_Content_cusPageComponents_repPageComponents_ctl00_pnlComponent td')
        temp_dict = {}
        temp_num = 0
        temp = ''
        for i in data:
            if temp_num%2 == 0:
                temp = i.get_text().replace('\t', '').replace('\n', '').replace('\r', '')
            else:
                temp_dict[temp] = i.get_text().replace('\t', '').replace('\n', '').replace('\r', '')
            temp_num+=1
        temp_list = list(temp_dict.keys())
        temp_dict['Sub Category'] = temp_dict['Sub Category'].replace('\xa0','')
        item['app_number'] = temp_dict['Application ID']
        item['description'] = temp_dict['Description'] if 'Description' in temp_list else None
        item['group_'] = temp_dict['Group'] if 'Group' in temp_list else None
        item['category'] = temp_dict['Category'] if 'Category' in temp_list else None
        item['sub_category'] = temp_dict['Sub Category'] if 'Sub Category' in temp_list else None
        item['status_'] = temp_dict['Status'] if 'Status' in temp_list else None

        lodged_date = temp_dict['Lodgement Date']
        time_array = time.strptime(lodged_date, '%d/%m/%Y')
        temp_data = int(time.mktime(time_array))
        item['lodgement_date'] = temp_data if lodged_date else None   
        
        item['stage'] = temp_dict['Stage/Decision'] if 'Stage/Decision' in temp_list else None
        
        try:
            address = soup.select('#ctl00_Content_cusPageComponents_repPageComponents_ctl01_cusPageComponentGrid_pnlCustomisationGrid .normalRow td')
            temp_str = ''
            for i in address:
                temp_str += i.get_text().replace('\t', '').replace('\n', '').replace('\r', '')
            item['address']=temp_str
        except:
            pass

        try:
            document = soup.select_one('#ctl00_Content_cusPageComponents_repPageComponents_ctl04_cusPageComponentGrid_lblNoRecords').get_text().replace('\t', '').replace('\n', '').replace('\r', '')
            item['document']=document
        except:
            pass

        yield item