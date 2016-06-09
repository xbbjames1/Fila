# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MTSGetdataItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    item_id = scrapy.Field()
    product_url = scrapy.Field()
    categories = scrapy.Field()
    title = scrapy.Field()
    product_detail = scrapy.Field()
    product_description = scrapy.Field()
    brand = scrapy.Field()
    merchant = scrapy.Field()
    colors = scrapy.Field()
 

