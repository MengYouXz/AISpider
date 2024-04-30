from bs4 import BeautifulSoup
import scrapy
from AISpider.items.kwinana_items import KwinanaItem
import re

class KwinanaSpider(scrapy.Spider):
    name = 'kwinana'
    allowed_domains = ["www.lovemykwinana.com"]
    start_urls = [
        'https://www.lovemykwinana.com/development-applications-2']
    # custom_settings = {
    #     'LOG_STDOUT': True,
    #     'LOG_FILE': 'scrapy_kwinana.log',
    # }

    def __init__(self):
        self.cookies = {
                    '_ehq_uid': 'BAhsKwcqNXhb--d3cbc135fe44db79a84687a06e681b9b7a132720',
                    'participant_fe': 'new',
                    '_ehq_session_id': 'BAhsKweONXhb--9dbb24acb58706ad73b886a6b3f65b6879d52cf3',
                    '_gid': 'GA1.2.1400291786.1712557778',
                    'unexpected_visit': '1712558144',
                    'next-i18next': 'en',
                    'current_language': 'en',
                    '_ga_S4TS49X5LL': 'GS1.1.1712558151.1.0.1712558175.36.0.0',
                    '_ga': 'GA1.2.1825399406.1712557778',
                    '_engagementhq_v3': 'BAh7DEkiD3Nlc3Npb25faWQGOgZFVEkiJTdkNjEwZmYxNjAwZjI5N2VmNzdmMDg4NWNmMmQ0ZDc1BjsAVEkiHW5ld19yZXBvcnRpbmdfc2Vzc2lvbl9pZAY7AEZsKweONXhbSSIZcmVwb3J0aW5nX3Nlc3Npb25faWQGOwBGbCsHwUR4W0kiDmxhc3Rfc2VlbgY7AEZVOiBBY3RpdmVTdXBwb3J0OjpUaW1lV2l0aFpvbmVbCEl1OglUaW1lDQYNH8DpqNuWCToNbmFub19udW1pEzoNbmFub19kZW5pBjoNc3VibWljcm8iBwFAOgl6b25lSSIIVVRDBjsARkkiClBlcnRoBjsAVEl1OwcNDg0fwOmo25YJOwhpEzsJaQY7CiIHAUA7C0AQSSIcbGFzdF92aXNpdGVkX3Byb2plY3RfaWQGOwBGaQO2KwFJIgxwcm9qZWN0BjsARkkiH2RldmVsb3BtZW50LWFwcGxpY2F0aW9ucy0yBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMXFudmp1R1NlTXhReVVXdFNkMEdIZkJhLy9JbHRCSUJSbE84Tk5BWWNpWEk9BjsARg%3D%3D--531624ac7efc328865988e7a9deb951837914128',
                    '_gat': '1',
                    '_gat_ehq_public': '1',
                    '_ehq_last_visit': '1712558274',
                    '_ga_R71DRH1YGZ': 'GS1.2.1712557781.1.1.1712558275.60.0.0',
                    '_ga_93EXG27Q34': 'GS1.2.1712557781.1.1.1712558275.60.0.0',
                }
        self.headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    # 'Cookie': '_ehq_uid=BAhsKwcqNXhb--d3cbc135fe44db79a84687a06e681b9b7a132720; participant_fe=new; _ehq_session_id=BAhsKweONXhb--9dbb24acb58706ad73b886a6b3f65b6879d52cf3; _gid=GA1.2.1400291786.1712557778; unexpected_visit=1712558144; next-i18next=en; current_language=en; _ga_S4TS49X5LL=GS1.1.1712558151.1.0.1712558175.36.0.0; _ga=GA1.2.1825399406.1712557778; _engagementhq_v3=BAh7DEkiD3Nlc3Npb25faWQGOgZFVEkiJTdkNjEwZmYxNjAwZjI5N2VmNzdmMDg4NWNmMmQ0ZDc1BjsAVEkiHW5ld19yZXBvcnRpbmdfc2Vzc2lvbl9pZAY7AEZsKweONXhbSSIZcmVwb3J0aW5nX3Nlc3Npb25faWQGOwBGbCsHwUR4W0kiDmxhc3Rfc2VlbgY7AEZVOiBBY3RpdmVTdXBwb3J0OjpUaW1lV2l0aFpvbmVbCEl1OglUaW1lDQYNH8DpqNuWCToNbmFub19udW1pEzoNbmFub19kZW5pBjoNc3VibWljcm8iBwFAOgl6b25lSSIIVVRDBjsARkkiClBlcnRoBjsAVEl1OwcNDg0fwOmo25YJOwhpEzsJaQY7CiIHAUA7C0AQSSIcbGFzdF92aXNpdGVkX3Byb2plY3RfaWQGOwBGaQO2KwFJIgxwcm9qZWN0BjsARkkiH2RldmVsb3BtZW50LWFwcGxpY2F0aW9ucy0yBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMXFudmp1R1NlTXhReVVXdFNkMEdIZkJhLy9JbHRCSUJSbE84Tk5BWWNpWEk9BjsARg%3D%3D--531624ac7efc328865988e7a9deb951837914128; _gat=1; _gat_ehq_public=1; _ehq_last_visit=1712558274; _ga_R71DRH1YGZ=GS1.2.1712557781.1.1.1712558275.60.0.0; _ga_93EXG27Q34=GS1.2.1712557781.1.1.1712558275.60.0.0',
                    'Pragma': 'no-cache',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                 }

    def start_requests(self):
        yield scrapy.Request(
            url='https://www.lovemykwinana.com/development-applications-2',
            cookies=self.cookies,
            headers=self.headers,
            callback=self.parse
        )

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        links = []
        ul = soup.find('ul', class_='blog-listing')
        lis = ul.find_all('li', class_='shared-content-block')
        for li in lis:
            link = li.find('a')
            href = link.get('href')
            links.append(href)
        for link in links:
            yield scrapy.Request(
                url=link,
                cookies=self.cookies,
                headers=self.headers,
                callback=self.parse_detail
            )

    def parse_detail(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        divs = soup.find('div', id='project_description_text')
        address = None
        id_number = None
        if divs:
            address_tag = divs.find('h1')
            if address_tag:
                address = address_tag.get_text()
                pattern = r"DA(\d+)"
                match = re.search(pattern, address)
                if match:
                    id_number = 'DA' + match.group(1)
        else:
            h2s = soup.find('h2', class_="title")
            if h2s:
                h2s_text = h2s.text
                pattern = r"DA(\d+)"
                match = re.search(pattern, h2s_text)
                if match:
                    id_number = 'DA' + match.group(1)
        if id_number == None: return
        text_tags = soup.find('div', class_='truncated-description')
        text = []
        if text_tags:
            lis = text_tags.find_all('li')
            for li in lis:
                tex = li.get_text()
                text.append(tex)

        key_dates = None
        h2_tag = soup.find('h2', class_='ehqthemed widget-header')
        if h2_tag is None:
            key_dates_tag = soup.find('div', class_='key-date-date')
            if key_dates_tag:
                key_dates = key_dates_tag.get_text().strip()
        else:
            key_dates = h2_tag.get_text().strip()

        documents = {}
        uls = soup.find('ul', class_='widget-list accordion-group')
        if uls:
            lis = uls.find_all('a', target='_blank')
            for li in lis:
                href = li.get('href')
                href_text = li.text.strip()
                documents[href_text] = href
        item = KwinanaItem()
        item['application_id'] = id_number
        item['application_id'] = id_number
        item['address'] = address
        item['text'] = text
        item['key_dates'] = key_dates
        item['documents'] = documents
        print(item)
        yield item