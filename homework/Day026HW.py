# -*- coding: utf-8 -*-
import scrapy


class Day026hwSpider(scrapy.Spider):
    name = 'Day026HW'
    allowed_domains = ['www.ptt.cc']
    start_urls = ['http://www.ptt.cc/']
    cookies = {'over18': '1'}


    def parse(self, response):
        pass
