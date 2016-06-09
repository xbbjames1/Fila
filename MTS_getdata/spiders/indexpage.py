# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import scrapy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from MTS_getdata import utiltools
from MTS_getdata.items import MTSGetdataItem
from MTS_getdata.utiltools import validate_attr

MAIN_PAGE = "main_page"
PRODUCT = "product"
IMG = 'image'

class MTSCrawler(scrapy.Spider):
    name = "MTSCrawler"
    start_urls = ["https://meidian.play.m.jaeapp.com/?iid=44792&cpp=0&wp_m=userDefineItem_7691833258&wp_pk=shop%2Fmall_index_134363478_4290029&from=inshop&wp_app=weapp", ]
    
    # default callback function ,used when Request has been created on start_url 
    def parse(self, response):
        res_tmp = response.xpath('//section[starts-with(@class,"app-module app-poster")]/a[starts-with(@class,"spot none")]/@href').extract()
        for i in range(len(res_tmp)):
            # To Be Cancel For more!!!!!!!!!!!!!!
            if utiltools.enhanced_catch(res_tmp[i]):
                temp_n = res_tmp[i].find('=')
                temp_m = res_tmp[i].find('&')
                iid = res_tmp[i][temp_n+1:temp_m]
                req = scrapy.Request(res_tmp[i], self.parse_for_product)
                req.meta['categories_id'] = iid
                yield req

    def url_maker(self, base, p_id):
        return base+p_id+'.htm'

    def parse_for_product(self, response):
        product_page = response.xpath('//ul[@class="ul"]/li[contains(@class,"column-box")]/a')
        base = 'https://world.tmall.com/item/'
        print "Length is:", len(product_page) 
        for link in product_page:
            price = link.xpath('span[starts-with(@class,"cur pro")]/text()').extract()
            url = link.xpath('@href').extract()
            name = link.xpath('figcaption/text()').extract()
            if len(url)>0:
                p_id = url[0].rsplit('=')
            tmp_url = self.url_maker(base,p_id[-1]) 
            req = scrapy.Request(tmp_url, self.parse_product)
            req.meta["price"] = price[0]
            req.meta["product_url"] = tmp_url
            req.meta["title"] = name[0]
            req.meta["categories_id"] = response.meta["categories_id"]
            yield req
            break

    SIZE_NUM = 430
    def resize_pic(self, s, org_size, new_size):
        p = str(org_size)
        l = len(p)
        n = s.rfind(p)
        st = s[0:n]
        m = st.rfind(p)
        new_str = s[0:m]+str(new_size)+s[m+l]+str(new_size)+s[n+l::]
        return new_str

    def parse_product(self, response):
        pic = response.xpath('//ul[@id="J_UlThumb"]/li/a/img/@src').extract()
        detail = response.xpath('//div[@class="attributes" and @id="attributes"]').extract()
        product_img = []
        for i in pic:
            tmp = self.resize_pic(i, 60, self.SIZE_NUM)
            product_img.append(tmp[2::])
        color_set = []
#        for i in :
#            colors = {}
#            colors['color'] = i+1 
#            colors['image_url'] = product_img[0]
#            colors['alternative_image_urls'] = product_img
##            colors['price'] = response.meta['price']
#            color_set.append(colors)
#        print color_set
        item = MTSGetdataItem()
        item['title']=response.meta['title'])
        item['brand'] = 'Meters Bonwe'
        item['merchant'] = 'Tmall'
        item['product_description'] = None
        item['product_detail'] = detail[0]
        
        drive = webdriver.PhantomJS()
        drive.get(response.url)
        
        yield item
