# -*- coding:utf-8 -*-
import scrapy
import requests
import json
import bs4
from scrapy.selector import SelectorList
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from MTS_getdata import utiltools
from MTS_getdata.items import MTSGetdataItem
from MTS_getdata.utiltools import validate_attr
from MTS_getdata import selen

MAIN_PAGE = "main_page"
PRODUCT = "product"
IMG = 'image'

class MTSCrawler(scrapy.Spider):
    name = "MTSCrawler"
    start_urls = ["https://midi.world.tmall.com/i/asynSearch.htm?_ksTS=1466028179363_287&callback=jsonp288&mid=w-14494838665-0&wid=14494838665&path=/category.htm&search=y&scene=taobao_shop&pageNo=0", ]    
    def parse_TBD(self, response):
#        yield scrapy.Request("", self.parse_TBD)
#        bread_cum = response.xpath('//div[contains(@class,"httm")]/div[contains(@class,"httm2")]/div/a/@href').extract()
#        moveon_urls = []
#        for i in bread_cum:
#            if i.find('category.')>-1:
#                moveon_urls.append(i)
#        for i in moveon_urls:
#            tmp_url = "https:"+i
#            print tmp_url
#            yield scrapy.Request(tmp_url, self.parse_TBD)
        pass


    def parse(self, response):
        page_body = response.body
        page_new_body = page_body[page_body.find("\"")+1:page_body.rfind("\"")] 
        response = response.replace(body=page_new_body.decode("string_escape"))
        page = response.xpath('//b[contains(@class,"ui-page-s-len")]/text()').extract()[0]
        page = int(page.split(r'/')[1])
        for i in range(page):
            srs = response.url
            new_url = srs[0:srs.rfind('=')+1]+str(i+1)
            req = scrapy.Request(new_url, self.parse_for_product)
            yield req
            break

    def url_maker(self, base, p_id):
        return base+p_id+'.htm'

    def parse_for_product(self, response):

        base = 'https://world.tmall.com/item/'
        body_con = response.body
        new_body = body_con[body_con.find("\"")+1:body_con.rfind("\"")] 
        res = response.replace(body=new_body.decode("string_escape"))
        product_page = res.xpath('//div[contains(@class,"item5line1")]/dl')
        
        for link in product_page:
            price = link.xpath('dd[@class="detail"]/div[@class="attribute"]/div[@class="cprice-area"]/span[@class="c-price"]/text()').extract()
            url = link.xpath('@data-id').extract()
            name = link.xpath('dt/a/img/@alt').extract()[0]
            
            try:
                p_id = url[0]
            except:
                print "Id Not Caught Error"
            
            tmp_url = self.url_maker(base,p_id)
            # req = scrapy.Request(tmp_url, self.parse_product)
            req = scrapy.Request('https://world.tmall.com/item/526012665963.htm?', self.parse_product)
            req.meta["price"] = price[0]
            req.meta["product_url"] = tmp_url
            req.meta["title"] = name
            req.meta["item_id"] = p_id
            yield req
            break

    def resize_pic(self, s):
        new_str = s
        return new_str[2:new_str.rfind('_')]

    def python_getter(self, st):
        n = st.rfind(");")
        m = st[:n].rfind(");")
        st = st[:st[:m].rfind("}")+1]
        return json.loads(st)

    def concat_p(self, sa, sb):
        return ";"+sa+";"+sb+";"

    def get_pricing(self, Mp, s_Mp, color_iter, size_list, price):
        color = color_iter.xpath('a/span/text()').extract()[0]
        pricing_list = []
        
        if len(size_list) == 0:
            PRICING = {}
            for dex in Mp:
                v_Mp = Mp.get(dex)
                if v_Mp['stock']>0:
                    PRICING['size'] = ''
                    PRICING['in_stock'] = True
                    PRICING['inventory'] = v_Mp['stock']
                    PRICING['currency'] = 'CNY'
                    PRICING['original_price'] = float(v_Mp['price'])
                    PRICING['sale_price'] = float(price)
                    break
            if len(PRICING)>0:
                pricing_list.append(PRICING)
            else:
                print "List Zero Error!"

        for i in size_list.xpath('a/span/text()').extract():
            PRICING = {}
            tmp_str = self.concat_p(s_Mp[i], s_Mp[color])
            tmp_val = Mp.get(tmp_str)
            if tmp_val!=None:
                PRICING['size'] = i
                PRICING['in_stock'] = (tmp_val['stock']>0)
                PRICING['inventory'] = tmp_val['stock']
                PRICING['currency'] = 'CNY'
                PRICING['original_price'] = float(tmp_val['price'])
                PRICING['sale_price'] = float(price)
            else:
                tmp_str_ = self.concat_p(s_Mp[color], s_Mp[i])
                tmp_val_ = Mp.get(tmp_str_)
                if tmp_val_ != None:
                    PRICING['size'] = i
                    PRICING['in_stock'] = (tmp_val_['stock']>0)
                    PRICING['inventory'] = tmp_val_['stock']
                    PRICING['currency'] = 'CNY'
                    PRICING['original_price'] = float(tmp_val_['price'])
                    PRICING['sale_price'] = float(price)
                else:
                    PRICING = None
                    print "Still Might Be Empty!"
            if PRICING!=None:
                pricing_list.append(PRICING)
        
        return pricing_list


    def parse_product(self, response):
        pic = response.xpath('//ul[@id="J_UlThumb"]/li/a/img/@src').extract()
        detail = response.xpath('//div[@class="attributes" and @id="attributes"]').extract()
        color_pics = response.xpath('//dd/ul[contains(@class,"tm-clear J_TSaleProp tb-img")]/li')
        total_list = response.xpath('//dd/ul[contains(@class,"tm-clear J_TSaleProp")]/li')
        json_getter = response.xpath('//div[@class="tm-clear"]/script[3]').extract()
        extract_pic = 
                
        print len(extract_pic)

        size_list = SelectorList()
        
        for i in total_list:
            if i.xpath('a/span/text()').extract()[0] not in color_pics.xpath('a/span/text()').extract():
                size_list.append(i)
#        cnt = 0
#        sku_type = 0
#        for i in total_list:
#            cnt = cnt + 1
#            if i.xpath('a/span/text()').extract()[0] not in color_pics.xpath('a/span/text()').extract():
#                size_list.append(i)
#                sku_type = cnt
#        if sku_type > len(total_list)-len(color_pics):
#            sku_type = 0
#        else:
#            sku_type = 1
#
#        if len(size_list)==0:
#            sku_type = 3
#
        # cut_line = len(total_list)-len(color_pics)

        str_val_map = {}

        for i in range(len(total_list)):
            v = total_list[i].xpath('@data-value').extract()
            n = total_list[i].xpath('a/span/text()').extract()
            if len(n)>0 and len(v)>0:
                str_val_map[n[0]] = v[0]
            else:
                print "Value Error"
        #size_list = total_list[:cut_line]
        st = json_getter[0].split('TShop.Setup(')[1]
        info_dict = self.python_getter(st)
        skuMap = info_dict["valItemInfo"]["skuMap"]

        product_img = []
        for i in pic:
            tmp = self.resize_pic(i)
            product_img.append(tmp)
    
        # color_set = selen.single_page(response.url)
        color_set = []
        for i in color_pics:
            color = {}
            color['color'] = i.xpath('@title').extract()[0]
            try:
                tmp_str = i.xpath('a/@style').extract()[0]
                tmp_str = tmp_str[tmp_str.find('(')+3:tmp_str.rfind(')')]
                tmp_str = tmp_str[0:tmp_str.rfind('_')]
                color['image_url'] = tmp_str
            except:
                color['image_url'] = product_img[0]

            color['alternative_image_urls'] = product_img
            color['pricing_list'] = self.get_pricing(skuMap, str_val_map, i, size_list, response.meta['price'])
            if len(color['pricing_list'])>0:
                color_set.append(color)
        
        item = MTSGetdataItem()
        item['product_url'] = response.meta['product_url']
        item['item_id'] = response.meta['item_id']
        item['title'] = response.meta['title']
        item['brand'] = 'Midi'
        item['merchant'] = 'Tmall'
        item['product_description'] = ''
        item['product_detail'] = detail[0]
        item['colors'] = color_set
        item['categories'] = info_dict['itemDO']['categoryId']
        if len(item['colors'])>0:
            yield item


