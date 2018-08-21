from scrapy import cmdline

cmdline.execute("scrapy crawl SinaSpider -s LOG_FILE=SinaSpider.log ".split())