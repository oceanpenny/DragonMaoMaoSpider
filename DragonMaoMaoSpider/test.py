from scrapy import cmdline

cmdline.execute("scrapy crawl DouBanSpider -s LOG_FILE=DouBanSpider.log".split())