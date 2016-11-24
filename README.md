Zillow Scraper
===============

This is a demo of scraper for zillow written in python using **Scrapy**. Now it
could just scrape a few information but it is very easy to extend based on the
requirements. After the information got scraped from the website, it will be
stored in to elasticsearch, but I didn't define any mappings yet since this is
just a toy project.

Requirements
-------------

* Tools
	* Elasticsearch

* Python packages
	* scrapy
	* elasticsearch
	* elasticsearch-dsl

Usage
-----

To use the scraper, one can simply run `scrapy crawl zillow_spider`.
