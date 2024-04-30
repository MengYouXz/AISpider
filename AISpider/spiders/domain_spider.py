
import re
import scrapy
from scrapy.http import Response
from AISpider.items.domain_items import domainItem
from common._string import except_blank, data_wash_tag,data_wash_null



class domainSpider(scrapy.Spider):
    """
    gave up retrying
    """
    name = "domain"
    allowed_domains = ["www.domain.com.au"]
    start_urls = [
        'https://www.domain.com.au/sale/?excludeunderoffer=1&retirement=1@@Retirement Villagefor sale',
        'https://www.domain.com.au/sold-listings/?excludepricewithheld=1&keywords=retirement%20village@@Retirement Village sold'
        'https://www.domain.com.au/sold-listings/?ptype=development-site&excludepricewithheld=1@@land sold',
        'https://www.domain.com.au/sale/?ptype=development-site,new-land,vacant-land&excludeunderoffer=1@@land for sale'
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'menu_Sub': 'hide',

    }

    custom_settings = {
        # 'ITEM_PIPELINES': {
        #     "AISpider.pipelines.AispiderPipeline": None,
        # }
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'LOG_STDOUT': True,
        'LOG_FILE': 'scrapy_domain.log',
        'DOWNLOAD_TIMEOUT': 1200
    }

    index = 1

    def __init__(self, *args, **kwargs):
        super(domainSpider, self).__init__(*args, **kwargs)
        self.cookie = None

    def start_requests(self):
        """
        添加请求负载
        """

        for url in self.start_urls:
            url_list = url.split('@@', 1)[0]
            app_model = url.split('@@', 1)[1]
            yield scrapy.Request(url_list, method="GET", dont_filter=True, headers=self.headers,
                                 meta={'app_model': app_model, })

    def parse(self, response: Response, **kwargs: any):
        app_model = response.meta.get('app_model')

        no_other_message=response.xpath('//a[@class="address is-two-lines css-1y2bib4"]/@href').getall()
        if len(no_other_message)<20:
            have_other_message=re.findall('<a class="listing-result-viewmore-button css-\w+" href="(.+?)">',response.text)
            no_other_message=re.findall('</path></svg></button></div><a href="(https://www.domain.com.au/.+?)" class="address is-two-lines css-\w+" rel="noopener">?',response.text)
            print(len(have_other_message))
            print(len(no_other_message))
            for url in have_other_message:
                yield scrapy.Request(url, method="GET", headers=self.headers, callback=self.parse_detail1,
                                     meta={'app_model': app_model,})
            for url in no_other_message:
                app_id = ''.join(re.findall('-(\d+)\?', url))
                if app_id=='':
                    app_id = ''.join(re.findall('-(\d+)$', url))

                yield scrapy.Request(url, method="GET", headers=self.headers, callback=self.parse_detail,
                                     meta={'app_model': app_model,'app_id':app_id })
        else:
            for item in no_other_message:
                item=re.sub('https://www.domain.com.au','',item)
                item='https://www.domain.com.au'+item
                app_id = ''.join(re.findall('-(\d+)$',item))
                yield scrapy.Request(item, method="GET", headers=self.headers, callback=self.parse_detail,
                             meta={'app_model': app_model, 'app_id': app_id})

        page_number_now = ''.join(except_blank(response.xpath('//span[@class="css-1oil53x"]/text()').getall()))
        page_number_next = ''.join(except_blank(response.css('.css-1ytqxcs span+a::text').extract()))
        page_number_next_url = ''.join(except_blank(response.css('.css-1ytqxcs span+a::attr(href)').extract()))
        error_text = ''.join(except_blank(response.xpath('//div[@class="css-18axwrx"]/p/text()').getall()))
        if page_number_next!='':
            if int(page_number_now) <int(page_number_next) and error_text != "The requested URL was not found on the server.":
                url = 'https://www.domain.com.au'+page_number_next_url
                yield scrapy.Request(url, method="GET", headers=self.headers, callback=self.parse,
                                     meta={'app_model': app_model,})



    def parse_detail(self, response):
        app_title = ''.join(except_blank(response.xpath('//div[@class="css-1texeil"]/text()').getall()))#have
        app_status = ''.join(except_blank(response.xpath('//span[@class="css-h9g9i3"]/text()').getall()))#have
        location = ''.join(except_blank(response.xpath('//h1[@class="css-164r41r"]/text()').getall()))

        purpose_to = ''.join(
            except_blank(response.xpath('//div[@class="css-dvvls9"]/span/text()').getall()))
        property_features = ';'.join(
            except_blank(response.xpath('//ul[@class="css-4ewd2m"]/li/text()').getall()))
        key_information={}

        key_information_title = except_blank(
            response.xpath('//div[@class="css-ghc6s4"]/div/span/span/span/text()').getall())
        key_information_data = except_blank(
            response.xpath('//div[@class="css-ghc6s4"]/div/span/span/text()').getall())
        key_information = dict(zip(key_information_title, key_information_data))
        land_area=''
        for item in key_information_data:
            land_area=''.join(re.findall('.+m²',item))
            if land_area==[]:
                land_area=''.join(re.findall('.+ha]',item))

        description =re.findall('"__typename":"DateTime"},"description":"(.*)","displayableAddress"',  response.text)
        description= ''.join([data_wash_null(i) for i in description])
        domain_says = ''.join(data_wash_tag(
            except_blank(response.xpath('//p[@class="css-yt9dan"]/text()').getall())))

        people_name = ''.join(
            except_blank(response.xpath('//h3[@class="css-159ex32"]/text()').getall()))
        people_address = ''.join(
            except_blank(response.xpath('//p[@class="css-1vslaj8"]/text()').getall()))

        item = domainItem()
        item["app_model"] = response.meta.get('app_model') or None
        item["app_id"] = response.meta.get('app_id') or None
        item["location"] = location  or None
        item["app_status"] = app_status  or None
        item["app_title"] = app_title  or None
        item["purpose_to"] = purpose_to or None
        item["property_features"] = property_features or None


        item["count_beds"] = key_information["Beds"] if "Beds" in list(key_information.keys()) else None
        if "Baths" in list(key_information.keys()):
            item["count_baths"] = key_information["Baths"]
        elif "Bath" in list(key_information.keys()):
            item["count_baths"] = key_information["Bath"]
        else:
            item["count_baths"] =None
        item["parking_info"] = key_information["Parking"] if "Parking" in list(key_information.keys()) else None
        item["land_area"] = land_area or None


        item["description"] = description or None
        item["domain_says"] = domain_says or None
        item["people_name"] = people_name or None
        item["people_address"] = people_address or None


        yield item
        print(f"success-{response.meta.get('app_id')}-{response.meta.get('app_model')}")


    def parse_detail1(self, response):
        app_model=response.meta.get('app_model')
        total_title = ''.join(except_blank(response.xpath('//div[@class="css-1w4p1vw"]/text()').getall()))  # have
        total_location = ''.join(except_blank(response.xpath('//div[@class="css-kb31vo"]/text()').getall()))

        total_information = ';'.join(except_blank(response.xpath('//div[@class="css-1dp9j9k"]/div/span/text()').getall()))
        project_highlights = except_blank(response.xpath('//div[@class="css-nc66p8"]/span/text()').getall())
        project_highlights=''.join(sorted(list(set(project_highlights)),key=project_highlights.index))

        description = re.findall(',"headline":"(.*)","category":', response.text)
        description = ''.join([i.replace('","description":"', '\n') for i in description])
        description=data_wash_null(description)
        detail_list=except_blank(response.xpath('//div[@class="css-1wfe5ji"]/div/a/@href').getall())

        for url in detail_list:

            app_id = ''.join(except_blank(re.findall('-(\d+)$', url)))
            yield scrapy.Request(url, method="GET", headers=self.headers, callback=self.parse_detail2,
                                 meta={'app_model': app_model,'total_title':total_title,'total_location':total_location,
                                       'total_information':total_information,'project_highlights':project_highlights,
                                       'description':description,'app_id': app_id})


    def parse_detail2(self, response):
        app_status = ''.join(except_blank(response.xpath('//span[@class="css-h9g9i3"]/text()').getall()))#have
        app_title = ''.join(except_blank(response.xpath('//span[@class="css-1w4p1vw"]/text()').getall()))  # have
        location = ''.join(except_blank(response.xpath('//h1[@class="css-164r41r"]/text()').getall()))
        purpose_to = ';'.join(except_blank(response.xpath('//p[@class="css-vvp9rf"]/text()').getall()))
        property_features = ';'.join(except_blank(response.xpath('//ul[@class="css-4ewd2m"]/li/text()').getall()))

        key_information = {}

        key_information_title = except_blank(
            response.xpath('//div[@class="css-ghc6s4"]/div/span/span/span/text()').getall())
        key_information_data = except_blank(
            response.xpath('//div[@class="css-ghc6s4"]/div/span/span/text()').getall())
        land_area=''
        for item in key_information_data:
            land_area=''.join(re.findall('.+m²',item))
            if land_area==[]:
                land_area=''.join(re.findall('.+ha]',item))
        key_information = dict(zip(key_information_title, key_information_data))

        description =re.findall('"__typename":"DateTime"},"description":"(.*)","displayableAddress"',  response.text)

        description = ''.join([data_wash_null(i) for i in description])

        domain_says = ''.join(data_wash_tag(
            except_blank(response.xpath('//p[@class="css-yt9dan"]/text()').getall())))

        people_name = ';'.join(
            except_blank(response.xpath('//h3[@class="css-159ex32"]/text()').getall()))
        people_address = ';'.join(
            except_blank(response.xpath('//p[@class="css-1vslaj8"]/text()').getall()))


        item = domainItem()
        item["app_id"] = response.meta.get('app_id') or None
        item["app_model"] = response.meta.get('app_model') or None
        item["total_title"] = response.meta.get('total_title') or None
        item["total_location"] = response.meta.get('total_location') or None
        item["total_information"] = response.meta.get('total_information') or None
        item["project_highlights"] = response.meta.get('project_highlights') or None
        item["total_description"] = response.meta.get('description') or None

        item["location"] = location  or None
        item["app_title"] = app_title  or None
        item["app_status"] = app_status  or None
        item["purpose_to"] = purpose_to or None
        item["property_features"] = property_features or None


        item["count_beds"] = key_information["Beds"] if "Beds" in list(key_information.keys()) else None
        item["count_baths"] = key_information["Baths"] if "Baths" in list(key_information.keys()) else None
        item["parking_info"] = key_information["Parking"] if "Parking" in list(key_information.keys()) else None
        item["land_area"] =land_area or None


        item["description"] = description or None
        item["domain_says"] = domain_says or None
        item["people_name"] = people_name or None
        item["people_address"] = people_address or None
        yield item
        print(f"success-{response.meta.get('app_id')}-{response.meta.get('app_model')}")