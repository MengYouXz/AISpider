from scrapy import Request
import re
import scrapy
import requests
from common._date import get_all_month
from bs4 import BeautifulSoup
import random
import time
from datetime import date, datetime, timedelta
from common._date import get_all_month
from common.set_date import get_this_month

DATE_FORMATE = "%d/%m/%Y"
from AISpider.items.lithgow_items import LithgowItem

class LithgowSpider(scrapy.Spider):
    """
    lockyer valley

    """
    name = "lithgow"
    allowed_domains = ["lithgowcc-web.t1cloud.com"]
    start_urls = ["https://lithgowcc-web.t1cloud.com/T1PRDefault/WebApps/eProperty/P1/Home.aspx?r=P1.WEBGUEST&f=LC.EPR.HOME.VIW"]
    start_date = '01/08/2006'  # 网站最早的记录为 01/08/2006

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'LOG_STDOUT': True,
    }

    def __init__(self,days=None,*args, **kwargs):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Origin': 'https://sdrc-web.t1cloud.com'
        }
        self.cookies = {
            'Cookie':''
        }
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
            # 用session处理cookie
            url_home = 'https://lithgowcc-web.t1cloud.com/T1PRDefault/WebApps/eProperty/P1/Home.aspx?r=P1.WEBGUEST&f=LC.EPR.HOME.VIW'
            session = requests.session()
            url_search = 'https://lithgowcc-web.t1cloud.com/T1PRDefault/WebApps/eProperty/P1/eTrack/eTrackApplicationSearch.aspx?r=P1.WEBGUEST&f=%24P1.ETR.SEARCH.ENQ'
            session.get(url=url_home,headers=self.headers)
            resp = session.get(url = url_search,headers=self.headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            paylod_1 = soup.select_one('#__VIEWSTATE').get('value')
            paylod_2 = soup.select_one('#__EVENTVALIDATION').get('value')
            y_position = random.randint(150, 180)
            paylods = {
                'ctl00_Content_ajaxToolkitManager_HiddenField': '',
                '__EVENTTARGET': 'ctl00$Content$btnSearch',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': paylod_1,
                '__SCROLLPOSITIONX': 0,
                '__SCROLLPOSITIONY': y_position,
                '__EVENTVALIDATION': paylod_2,
                'ctl00$Content$txtApplicationID$txtText': '',
                'ctl00$Content$txtDateFrom$txtText': start_time,
                'ctl00$Content$txtDateTo$txtText': end_time,
                'ctl00$Content$txtDescription$txtText': '',
                'ctl00$Content$ddlApplicationType$elbList': 'all',
                'ctl00$Content$ddlStatus$elbList': 'C',
                'ctl00$Content$ddlDecision$elbList': 'all',
                'ctl00$Content$txtStreetNoFrom$txtText': '',
                'ctl00$Content$txtStreetNoTo$txtText': '',
                'ctl00$Content$txtStreet$txtText': '',
                'ctl00$Content$txtStreetType$txtText': '',
                'ctl00$Content$txtSuburb$txtText': '',
                'ctl00$Content$txtPlanNo$txtText': '',
                'ctl00$Content$txtPlanType$txtText': '',
                'ctl00$Content$txtLotNo$txtText': '',
                'ctl00$Content$txtParcelType$txtText': ''
            }
            for item in self.post_search(paylods,session):
                yield item
    def judge_date(self,start_time):
        if self.days.split('/')[2] == start_time.split('/')[2]:
            if self.days.split('/')[1] == start_time.split('/')[1]:
                return False
            else:return True
        else:
            return False
            
    def post_search(self,paylods,session):
        self.cookies = {
            "Cookie": str(session.cookies).split(" ")[1]
        }
        search_post = 'https://lithgowcc-web.t1cloud.com/T1PRDefault/WebApps/eProperty/P1/eTrack/eTrackApplicationSearch.aspx?r=P1.WEBGUEST&f=%24P1.ETR.SEARCH.ENQ'
        session.post(url=search_post, data=paylods, headers=self.headers)
        print(self.cookies)
        url_search_result= 'https://lithgowcc-web.t1cloud.com/T1PRDefault/WebApps/eProperty/P1/eTrack/eTrackApplicationSearchResults.aspx?r=P1.WEBGUEST&f=%24P1.ETR.RESULTS.VIW'
        resp = session.get(url_search_result,headers=self.headers)
        # print(resp.text)
        soup = BeautifulSoup(resp.text, 'html.parser')
        paylod_1 = soup.select_one('#__VIEWSTATE').get('value')
        paylod_2 = soup.select_one('#__EVENTVALIDATION').get('value')
        y_position = random.randint(450, 480)
        paylods = {
            '__EVENTTARGET':'ctl00$Content$cusResultsGrid$repWebGrid$ctl00$grdWebGridTabularView' ,
            '__EVENTARGUMENT': '',
            '__VIEWSTATE':paylod_1,
            '__VIEWSTATEGENERATOR': 'EA86C627',
            '__SCROLLPOSITIONX': 0,
            '__SCROLLPOSITIONY': y_position,
            '__EVENTVALIDATION': paylod_2,
        }
        obj = re.compile(r'<td><a href="javascript:.*?">(?P<app_number>.*?)</a>',re.S)
        result = obj.findall(resp.text)
        i = 0
        app_nums = []
        for num in result:
            if i % 2 == 0:
                app_nums.append(num)
            else:
                pass
            i += 1
        try:
            page_number = int(app_nums[-1])
            print(f"Search {page_number} pages")
            # print(app_nums)
            for page in range(page_number+2):
                if page == 0:
                        pass
                elif page==1:
                    print(app_nums)
                    for app_num in app_nums:
                        detail_url = f"https://lithgowcc-web.t1cloud.com/T1PRDefault/WebApps/eProperty/P1/eTrack/eTrackApplicationDetails.aspx?r=P1.WEBGUEST&f=%24P1.ETR.APPDET.VIW&ApplicationId={app_num}"
                        yield Request(url=detail_url,dont_filter=True, cookies=self.cookies, callback=self.parse)
                else:
                    try:
                        app_nums = self.deal_pagination(page,paylods,session)
                        print(app_nums)
                        for app_num in app_nums:
                            detail_url = f"https://lithgowcc-web.t1cloud.com/T1PRDefault/WebApps/eProperty/P1/eTrack/eTrackApplicationDetails.aspx?r=P1.WEBGUEST&f=%24P1.ETR.APPDET.VIW&ApplicationId={app_num}"
                            yield Request(url=detail_url, dont_filter=True, cookies=self.cookies, callback=self.parse)
                    except:
                        break
            for app_num in app_nums:
                detail_url = f"https://lithgowcc-web.t1cloud.com/T1PRDefault/WebApps/eProperty/P1/eTrack/eTrackApplicationDetails.aspx?r=P1.WEBGUEST&f=%24P1.ETR.APPDET.VIW&ApplicationId={app_num}"
                yield Request(url=detail_url, cookies=self.cookies, callback=self.parse)
        except:
            print("only one page")
            print(app_nums)
            for app_num in app_nums:
                detail_url = f"https://lithgowcc-web.t1cloud.com/T1PRDefault/WebApps/eProperty/P1/eTrack/eTrackApplicationDetails.aspx?r=P1.WEBGUEST&f=%24P1.ETR.APPDET.VIW&ApplicationId={app_num}"
                yield Request(url=detail_url, cookies=self.cookies, callback=self.parse)

    def deal_pagination(self,page,paylods,session):
        page_num = f'Page${page}'
        print(page_num)
        paylods['__EVENTARGUMENT'] = page_num
        url_search_result= 'https://lithgowcc-web.t1cloud.com/T1PRDefault/WebApps/eProperty/P1/eTrack/eTrackApplicationSearchResults.aspx?r=P1.WEBGUEST&f=%24P1.ETR.RESULTS.VIW'
        resp = session.post(url_search_result, headers=self.headers,data=paylods)
        obj = re.compile(r'<td><a href="javascript:.*?">(?P<app_number>.*?)</a>', re.S)
        try:
            result = obj.findall(resp.text)
            i = 0
            app_nums = []
            for num in result:
                if i % 2 == 0:
                    app_nums.append(num)
                else:
                    pass
                i += 1
            return app_nums
        except:
            return None


    def parse(self,response):
        item = LithgowItem()
        soup = BeautifulSoup(response.text, 'html.parser')
        judge = soup.select_one('.cssPageTitle')
        if judge == None:
            temp_dick = {}
            try:
                obj = re.compile(r'noScriptLinkButton.*?value="(?P<data>.*?)"', re.S)
                data = obj.findall(response.text)
                # print(data)
                temp_dick['Address'] = data[1].strip()
            except:
                pass
            app_id = soup.select('.grid td')
            i = 0
            for app in app_id:
                if i%2 == 0:
                    temp_str = app.text.strip().replace('\r','').replace('\t','')
                else:
                    try :
                        if temp_dick[temp_str]:
                            if temp_str == 'Land Description':
                                temp_dick[temp_str] = app.text.strip().replace('\r', '').replace('\t', '')
                            else:
                                i +=1
                                continue
                    except:
                        temp_dick[temp_str] = app.text.strip().replace('\r','').replace('\t','')
                i +=1

            print(temp_dick)
            try:
                name_details = 'Name'+':'+temp_dick['Name']+';'+'Association'+':'+temp_dick['Association']+';'
            except:
                name_details = None
                pass
            properties = 'Address'+':'+temp_dick['Address']+';'+'Land Description'+':'+temp_dick['Land Description']+';'
            item['application_id'] = temp_dick['Application ID']
            item['description'] = temp_dick['Description']
            item['application_group'] = temp_dick['Group']
            item['category'] = temp_dick['Category']
            item['sub_category'] = temp_dick['Sub Category']

            lodged_date = temp_dick['Lodgement Date'].strip()
            time_array = time.strptime(lodged_date, '%d/%m/%Y')
            temp_data = int(time.mktime(time_array))
            item['lodged_date'] = temp_data if lodged_date else None

            item['stage'] = temp_dick['Stage or Decision']
            try :
                lodged_date = temp_dick['Determined Date'].strip()
                time_array = time.strptime(lodged_date, '%d/%m/%Y')
                temp_data = int(time.mktime(time_array))
                item['determined_date'] = temp_data if lodged_date else None
            except:
                item['determined_date'] = None
            item['name_details'] = name_details
            item['properties'] = properties
            yield item
        else:
            return

