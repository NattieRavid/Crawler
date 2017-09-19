import queue
import re
import scrapy
import scrapy.linkextractors


class Spider(
    scrapy.Spider,
):
    name = 'generic_spider'

    http_cleaner_regex = re.compile(
        pattern=r'(^https?://|/$)',
    )

    start_urls = set()
    visited_urls = set()
    responses = queue.Queue(
        maxsize=100,
    )

    def start_requests(
        self,
    ):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.handle_http_response,
            )

    def handle_http_response(
        self,
        response,
    ):
        normalized_url = self.normalize_url(
            url=response.url,
        )
        if normalized_url in self.visited_urls:
            return

        self.visited_urls.add(normalized_url)

        response_dict = {
            'url': normalized_url,
            'status_code': response.status,
            'content': response.text,
        }
        self.responses.put(
            response_dict,
        )

        webpage_urls = self.get_urls_from_webpage(
            response=response,
            allowed_domains=self.allowed_domains,
        )
        urls_to_visit = {
            url
            for url in webpage_urls
            if self.normalize_url(
                url=url,
            ) not in self.visited_urls
        }

        for url in urls_to_visit:
            yield scrapy.Request(
                url=url,
                callback=self.handle_http_response,
            )

    def process_response(
        self,
        response,
    ):
        self.responses.put(
            response,
        )

    def get_urls_from_webpage(
        self,
        response,
        allowed_domains,
    ):
        links_items = scrapy.linkextractors.LinkExtractor(
            allow_domains=allowed_domains,
        ).extract_links(
            response=response,
        )

        urls = [
            item.url
            for item in links_items
        ]

        return urls

    def normalize_url(
        self,
        url,
    ):
        normalized_url = self.http_cleaner_regex.sub(
            repl='',
            string=url,
        )

        return normalized_url
