from bs4 import BeautifulSoup
import scrapy
from AISpider.items.armadale_items import ArmadaleItem

class ArmadalcSpider(scrapy.Spider):
    name = 'armadale'
    allowed_domains = ["engage.armadale.wa.gov.au", "www.armadale.wa.gov.au"]
    start_urls = [
        'https://www.armadale.wa.gov.au/community-consultation']
    custom_settings = {
        'LOG_STDOUT': True,
        # 'LOG_FILE': 'scrapy_armadalc.log',
    }

    def __init__(self):
        self.headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    # 'Cookie': '_ga=GA1.1.1733334968.1712482471; _ehq_uid=BAhsKwduPm9b--cfbe915acb7208fcb84c4f444bbdb5b70ca8236e; participant_fe=new; _ga_786DT6FKNH=GS1.1.1712540883.3.0.1712540883.60.0.0; _ehq_last_visit=1712540888; _ehq_session_id=BAhsKwdQpnVb--e4f794dacdc84b1293748e7f8eca6ee88c7fc8f1; _engagementhq_v3=BAh7DEkiD3Nlc3Npb25faWQGOgZFVEkiJTI4YjViNWJjYTJjZjkwNTc5MDUxMjkxMDViZGRjZDJlBjsAVEkiGXJlcG9ydGluZ19zZXNzaW9uX2lkBjsARmwrBxemdVtJIg5sYXN0X3NlZW4GOwBGVTogQWN0aXZlU3VwcG9ydDo6VGltZVdpdGhab25lWwhJdToJVGltZQ0BDR%2FA3cxAwAk6DW5hbm9fbnVtaXk6DW5hbm9fZGVuaQY6DXN1Ym1pY3JvIgcRYDoJem9uZUkiCFVUQwY7AEZJIgpQZXJ0aAY7AFRJdTsHDQkNH8DdzEDACTsIaXk7CWkGOwoiBxFgOwtADkkiHGxhc3RfdmlzaXRlZF9wcm9qZWN0X2lkBjsARmkDjGgBSSIMcHJvamVjdAY7AEZJIilsb3QtNi1uby0yNy1mYW5jb3RlLXN0cmVldC1rZWxtc2NvdHQGOwBUSSIQX2NzcmZfdG9rZW4GOwBGSSIxS3NhTkNrWHd4NHdsRXpDcmFGYXpzU3Y1YWNQVDRUaUtzaWVHaTFBS2VZOD0GOwBGSSIdbmV3X3JlcG9ydGluZ19zZXNzaW9uX2lkBjsARmwrB7s%2Bb1s%3D--45ba6019322a63b923b20cb7cd37cff118f7dc77',
                    'Pragma': 'no-cache',
                    'Referer': 'https://www.armadale.wa.gov.au/community-consultation',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'same-site',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                }

    def start_requests(self):
        yield scrapy.Request(
            url='https://www.armadale.wa.gov.au/community-consultation',
            headers=self.headers,
            callback=self.parse
        )

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        table_list = soup.find_all('table', class_='views-table cols-2')[6]
        a_tags = table_list.find_all('a')
        links = []
        for a_tag in a_tags:
            href = a_tag.get('href')
            if href and not href.startswith("https://engage.armadale.wa.gov.au"):
                new_href = "https://www.armadale.wa.gov.au" + href
                links.append(new_href)
            else:
                links.append(href)
        for link in links:
            yield scrapy.Request(
                url=link,
                headers=self.headers,
                callback=self.parse_detail
            )

    def parse_detail(self, response):
        # 第一种https://www.armadale.wa.gov.au/lot-15-no-651-nicholson-road-forrestdale
        soup = BeautifulSoup(response.text, 'lxml')
        if not 'Online Submission' in response.text:
            divs = soup.find('div', class_='column')
            title = divs.find('h2').text.strip()
            address = soup.find('nav', class_='breadcrumb').find('ol').find_all('li')[3].get_text()
            text_div = divs.find('div', class_='field-item even')
            if text_div:
                text = text_div.text.strip()
            else:
                text = None
            links = {}
            table = soup.find('table', class_='sticky-enabled')
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    link = row.find('a')
                    if link:
                        text = link.text.strip()
                        href = link['href']
                        links[text] = href
            item = ArmadaleItem()
            item['title'] = title
            item['address'] = address
            item['text'] = text
            item['documents'] = links
            print(item)
            yield item
        # 第二种  https://engage.armadale.wa.gov.au/lot-6-no-27-fancote-street-kelmscott
        else:
            address = soup.find('h1').text.strip()
            description_parent = soup.find('div', class_='description parent-description')
            feedback_closes = description_parent.find('p').get_text().replace('Feedback closes:', '').strip()
            title_tag = description_parent.find('h2') if description_parent else None
            title = title_tag.text.strip() if title_tag else None
            text_list = description_parent.find_all('p')[1:]
            text = []
            for txt in text_list:
                con = txt.get_text()
                text.append(con)
            documents = {}
            li_tags = soup.find_all('li', class_='documents_in_folder')
            for li_tag in li_tags:
                a_tag = li_tag.find('a')
                if a_tag:
                    link_text = a_tag.text.strip()
                    href = a_tag.get('href')
                    documents[link_text] = href
            item = ArmadaleItem()
            item['title'] = title
            item['feedback_closes'] = feedback_closes
            item['address'] = address
            item['text'] = text
            item['documents'] = documents
            print(item)
            yield item
# if soup.find('div', class_='view-content'):
            # links_div = divs.find('div', class_='view-content')
            # links = {}
            # for link in links_div.find_all('a', class_='fetchSize'):
            #     href = link['href']
            #     link_text = link.text.strip()
            #     links[link_text] = href

# ol = soup.find('div', class_='truncated-description').find('ol')
            # if ol:
            #     lis = ol.find_all('li', recursive=False)
            #     text = [li.get_text(strip=True) for li in lis]
            # else:
            #     text = None
# feedback_closes = soup.find(class_='closing-time').text.strip().replace('Feedback closes:', '').strip()
# address = title.split('-')[-1].strip()