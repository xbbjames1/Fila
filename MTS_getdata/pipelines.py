# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from MTS_getdata import selen
import json

JsonFile = []
class MTSGetdataPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri = crawler.settings.get("MONGO_URI"),
            mongo_db = crawler.settings.get("MONGO_DATABASE")
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        # collection_name = self.__class__.__name__
        # tmp = dict(item)
        # print "***************************", tmp, "!!!!!!!!!!!!!!!!!!!!!!!"
        # self.db[collection_name].insert(tmp)
        JsonFile.append(dict(item))
        return item
        # return None


    def close_spider(self, spider):
        print len(JsonFile)
        fp = open("MeterBonwe1.json","wb")
        fp.write(json.dumps(JsonFile))
        self.client.close()


