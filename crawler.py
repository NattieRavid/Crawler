import scrapy.crawler
import threading
import time

from . import spider


class Crawler:
    settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 8,
        'COOKIES_ENABLED': False,
        'DOWNLOAD_TIMEOUT': 5,
        'HTTPERROR_ALLOW_ALL': True,
        'LOG_ENABLED': False,
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    }

    visited_sites = {}

    def __init__(
        self,
    ):
        self.crawler_process = scrapy.crawler.CrawlerProcess(
            settings=self.settings,
        )

    def crawl(
        self,
        domain,
    ):
        url = 'http://{domain}'.format(
            domain=domain,
        )

        self.crawler_process.crawl(
            spider.Spider,
            allowed_domains=[
                domain,
            ],
            start_urls=[
                url,
            ],
        )

        self.crawler_thread = threading.Thread(
            target=self.crawler_process.start,
        )
        self.crawler_thread.daemon = True
        self.crawler_thread.start()

        while self.crawler_thread.is_alive() or not spider.Spider.responses.empty():
            if not spider.Spider.responses.empty():
                response = spider.Spider.responses.get()
                if response:
                    yield response
            else:
                time.sleep(1)
