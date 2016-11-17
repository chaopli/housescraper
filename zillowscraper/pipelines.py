# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, streaming_bulk
import subprocess
import time
from subprocess import call


class ZillowscraperPipeline(object):
    def __init__(self):
        if not start_elastic_search():
            print 'Failed to start elasticsearch'
            return

        self.es = Elasticsearch(hosts=[{'host': 'localhost', 'port': 9200}])
        if not self.es.indices.exists('zillow'):
            self.es.indices.create(index='zillow', body={'settings': {'number_of_shards': 1, 'number_of_replicas': 0}})

    def process_item(self, item, spider):
        index_data(self.es, item)
        return item


def elastic_search_running():
    ps = subprocess.Popen('ps aux'.split(), stdout=subprocess.PIPE)
    output = subprocess.check_output('grep elastic'.split(), stdin=ps.stdout)
    return 'java' in output


def start_elastic_search():
    if elastic_search_running():
        print 'Elastic Search is already running!'
        return True
    # call('pkill -9 -f elasticsearch'.split())
    call('./elasticsearch/bin/elasticsearch -d'.split())
    es = Elasticsearch(hosts=[{'host': 'localhost', 'port': 9200}])
    counter = 0
    while not es.ping():
        time.sleep(1)
        if counter > 10:
            return False
    return True


def index_data(es, item):
    data = [{'_op_type': 'create', '_index': 'zillow', '_type': 'document', '_source': item}]
    res = bulk(es, data)
