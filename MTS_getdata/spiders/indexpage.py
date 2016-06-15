# -*- coding:utf-8 -*-
import scrapy
import json
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
    start_urls = ["https://fila.world.tmall.com/view_shop.htm?spm=a312a.7700824.w4011-11586646327.431.OEIgzP&type=p&search=y&newHeader_b=s_from&searcy_type=item&from=.shop.pc_2_searchbutton&scene=taobao_shop&keyword=%C5%AE&pageNo=1&tsearch=y#anchor", ]
    
    # default callback function ,used when Request has been created on start_url 
    def parse(self, response):
        #driver = webdriver.PhantomJS(service_args=['--load-images=no'])
        #driver.get(response.url)
        #ele = driver.find_elements_by_xpath('//div[@class="pagination"]/a[@class="J_SearchAsync"]')
        for i in range(4):
            srs = response.url
            n = srs.find('pageNo')
            new_url = srs[0:n+7]+str(i+1)+srs[n+8::]
            req = scrapy.Request(new_url, self.parse_for_product)
            yield req

    def url_maker(self, base, p_id):
        return base+p_id+'.htm'

    def parse_for_product(self, response):
        product_page = response.xpath('//div[@class="item5line1"]/dl')

        base = 'https://world.tmall.com/item/'
        for link in product_page:
            price = link.xpath('dd[@class="detail"]/div[@class="attribute"]/div[@class="cprice-area"]/span[@class="c-price"]/text()').extract()
            url = link.xpath('@data-id').extract()
            name = link.xpath('dt/a/img/@alt').extract()
            if len(name)>0:
                name_1 = name[0]
                name_ = name_1[0:name_1.find('<')]+name_1[name_1.rfind('>')+1::]
            else:
                name_ = ''
            if len(url)>0:
                p_id = url[0]

            tmp_url = self.url_maker(base,p_id)
            req = scrapy.Request(tmp_url, self.parse_product)
            # req = scrapy.Request('https://world.tmall.com/item/532999026696.htm?', self.parse_product)
            req.meta["price"] = price[0]
            req.meta["product_url"] = tmp_url
            req.meta["title"] = name_
            req.meta["item_id"] = p_id
            yield req


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

    def get_pricing(self, info_dict, Mp, s_Mp, color_iter, size_list, price):
        color = color_iter.xpath('a/span/text()').extract()[0]
        pricing_list = []
    
        for i in size_list.xpath('a/span/text()').extract():
            PRICING = {}
            tmp_str = self.concat_p(s_Mp[i],s_Mp[color])
            tmp_val = Mp.get(tmp_str)
            if tmp_val!=None:
                PRICING['size'] = i
                PRICING['in_stock'] = (tmp_val['stock']>0)
                PRICING['inventory'] = tmp_val['stock']
                PRICING['currency'] = 'CNY'
                PRICING['original_price'] = float(tmp_val['price'])
                PRICING['sale_price'] = float(price)
            else:
                PRICING = None
                print "PRICING Might Be Empty!"
            if PRICING!=None:
                pricing_list.append(PRICING)
        return pricing_list


    def parse_product(self, response):
        pic = response.xpath('//ul[@id="J_UlThumb"]/li/a/img/@src').extract()
        detail = response.xpath('//div[@class="attributes" and @id="attributes"]').extract()
        color_pics = response.xpath('//dd/ul[contains(@class,"tm-clear J_TSaleProp tb-img")]/li')
        total_list = response.xpath('//dd/ul[contains(@class,"tm-clear J_TSaleProp")]/li')
        # size_list = response.xpath('//dd/ul[contains(@class,"tm-clear J_TSaleProp")]/li')
        json_getter = response.xpath('//div[@class="tm-clear"]/script[3]').extract()
        
        size_list = SelectorList()

        for i in total_list:
            if i.xpath('a/span/text()').extract()[0] not in color_pics.xpath('a/span/text()').extract():
                size_list.append(i)
        
        cut_line = len(total_list)-len(color_pics)

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
            tmp_str = i.xpath('a/@style').extract()[0]
            tmp_str = tmp_str[tmp_str.find('(')+3:tmp_str.rfind(')')]
            tmp_str = tmp_str[0:tmp_str.rfind('_')]
            color['image_url'] = tmp_str    
            color['alternative_image_urls'] = product_img
            color['pricing_list'] = self.get_pricing(info_dict, skuMap, str_val_map, i, size_list, response.meta['price'])
            if len(color['pricing_list'])>0:
                color_set.append(color)
        
        item = MTSGetdataItem()
        item['product_url'] = response.meta['product_url']
        item['item_id'] = response.meta['item_id']
        item['title'] = response.meta['title']
        item['brand'] = 'Fila'
        item['merchant'] = 'Tmall'
        item['product_description'] = ''
        item['product_detail'] = detail[0] 
        item['colors'] = color_set
        item['categories'] = info_dict['itemDO']['categoryId']
        if len(item['colors'])>0:
            yield item




