from scrapy.cmdline import execute
from pyquery import PyQuery as pq
import scrapy
import json
import re
import sys
import time


class ZillowSpider(scrapy.Spider):
    name = "zillow_spider"
    start_urls = [
        '''http://www.zillow.com/search/GetResults.htm?spt=homes&status=100000&lt=111101&ht=011010&pr=,&mp=,&bd=1%2C&ba=0%2C&sf=,&lot=0%2C&yr=,&singlestory=0&hoa=0%2C&pho=0&pets=0&parking=0&laundry=0&income-restricted=0&pnd=0&red=0&zso=0&days=any&ds=all&pmf=0&pf=0&sch=100111&zoom=9&rect=-122956924,37128571,-121480637,38089175&p=1&sort=pricea&search=maplist&listright=true&isMapSearch=1&zoom=9'''
    ]
    hdprefix = 'http://www.zillow.com/homedetails/'
    zillowhome = 'http://www.zillow.com/'
    cur_page = 1
    handle_httpstatus_list = [400, 401, 403, 404, 405, 413, 500]

    def parse(self, response):
        if response.status == 500:
            self.logger.error('Server Error')
            return
        json_resp = json.loads(response.text)
        numpages, zpids = json_resp['list']['numPages'], json_resp['list']['zpids']
        while self.cur_page < numpages:
            for zpid in zpids:
                yield scrapy.Request(self.hdprefix+str(zpid)+'_zpid/', callback=self.parse_home_detail)
                time.sleep(1)

            self.cur_page += 1
            yield scrapy.Request(self.get_page_url(self.cur_page), callback=self.parse)

    def parse_home_detail(self, response):
        if response.status == 301:
            yield scrapy.Request(self.zillowhome+str(response.headers['location']), callback=self.parse)
        price = response.xpath('//div[@class="main-row  home-summary-row"]/span/text()').extract_first()
        address = response.xpath('//span[@class="zsg-h2 addr_city"]/parent::h1/text()').extract_first()
        city = response.xpath('//h1[@class="notranslate"]/span[@class="zsg-h2 addr_city"]/text()').extract_first()
        description = response.xpath('//div[@class="notranslate zsg-content-item"]/text()').extract_first()
        facts = response.xpath('//h3[text()="Facts"]/parent::*/ul/li/text()').extract()
        features = response.xpath('//h3[text()="Features"]/parent::*/ul/li/text()').extract()
        photos = response.xpath('//img[@class="hip-photo"]/@href').extract()
        # self.logger.debug('\nGet Home Detail:\n'
        #                   'Address: %s\n'
        #                   'City: %s\n'
        #                   'Price: %s\n'
        #                   'Description: %s\n'
        #                   'Facts: %s\n'
        #                   'Features: %s\n'
        #                   'Photos: %s', address, city, price, description, facts, features, photos)
        yield {'address': address,
               'city': city,
               'price': price,
               'description': description,
               'facts': facts,
               'features': features,
               'photos': photos
               }

    def get_page_url(self, page):
        return '''http://www.zillow.com/search/GetResults.htm?spt=homes&status=100000&lt=111101&ht=011010&pr=,&mp=,&bd=1%2C&ba=0%2C&sf=,&lot=0%2C&yr=,&singlestory=0&hoa=0%2C&pho=0&pets=0&parking=0&laundry=0&income-restricted=0&pnd=0&red=0&zso=0&days=any&ds=all&pmf=0&pf=0&sch=100111&zoom=9&rect=-122956924,37128571,-121480637,38089175&p={}&sort=pricea&search=maplist&listright=true&isMapSearch=1&zoom=9'''.format(page)
