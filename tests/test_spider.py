import os
import unittest
import unittest.mock

import pytest
import scrapy

from .. import spider


def get_test_resource_file_content(
    filename,
):
    current_working_directory = os.path.dirname(
        os.path.realpath(__file__)
    )

    file_fullpath = os.path.join(
        current_working_directory,
        'resources',
        filename,
    )
    with open(file_fullpath, 'r') as fp:
        content = fp.read()

    return content


class SpiderTestCase(
    unittest.TestCase,
):
    bugmenot_com_html_content = get_test_resource_file_content(
        filename='bugmenot_com.html',
    )
    domain = 'bugmenot.com'
    url = f'http://{domain}'
    scrapy_response = scrapy.http.HtmlResponse(
        url=url,
        body=bugmenot_com_html_content,
        encoding='utf-8',
    )

    def setUp(
        self,
    ):
        self.spider = spider.Spider()
        self.spider.allowed_domains = [
            self.domain,
        ]

    def test_url_cleaner_regex(
        self,
    ):
        urls = (
            'www.bugmenot.com',
            'http://www.bugmenot.com',
            'https://www.bugmenot.com',
            'www.bugmenot.com/',
            'http://www.bugmenot.com/',
            'https://www.bugmenot.com/',
        )

        for url in urls:
            result = self.spider.http_cleaner_regex.sub(
                repl='',
                string=url,
            )
            self.assertEqual(
                result,
                'www.bugmenot.com',
                msg='test url cleaner regex failed',
            )

    def test_handle_http_response(
        self,
    ):
        expected_visited_urls = {
            'bugmenot.com',
        }
        expected_urls_to_visit = (
            'http://bugmenot.com/terms.php',
            'http://bugmenot.com/removal.php',
        )
        self.spider.visited_urls.clear()
        scrapy.Request = unittest.mock.MagicMock()

        spider_handle_http_response = self.spider.handle_http_response(
            response=self.scrapy_response,
        )
        list(spider_handle_http_response)

        self.assertEqual(
            self.spider.visited_urls,
            expected_visited_urls,
            msg=f'test handle http response failed',
        )

        self.assertEqual(
            len(scrapy.Request.call_args_list),
            len(expected_urls_to_visit),
            msg=f'test handle http response failed',
        )

        for url in expected_urls_to_visit:
            self.assertIn(
                (
                    {
                        'url': url,
                        'callback': self.spider.handle_http_response,
                    },
                ),
                scrapy.Request.call_args_list,
                msg=f'test handle http response failed',
            )

    def test_process_response(
        self,
    ):
        response = {
            'url': 'bugmenot.com',
            'status_code': 200,
            'content': self.bugmenot_com_html_content,
        }

        self.spider.responses = unittest.mock.MagicMock()

        self.spider.process_response(
            response=response,
        )

        self.spider.responses.put.assert_called_once_with(
            response,
        )

    def test_get_urls_from_webpage(
        self,
    ):
        expected_results = [
            'http://bugmenot.com/terms.php',
            'http://bugmenot.com/removal.php',
            'http://bugmenot.com/',
        ]

        results = self.spider.get_urls_from_webpage(
            response=self.scrapy_response,
            allowed_domains=[
                self.domain
            ],
        )
        self.assertEqual(
            len(results),
            len(expected_results),
            msg=f'{results} is not equal to {expected_results}',
        )

        for url in results:
            self.assertIn(
                url,
                expected_results,
                msg=f'{url} is not exist in {expected_results}',
            )

    def test_spider_normalize_url(
        self,
    ):
        urls = (
            'google.com',
            'http://google.com',
            'https://google.com',
            'google.com/',
            'http://google.com/',
            'https://google.com/',
        )

        expected_result = 'google.com'

        for url in urls:
            normalized_url = self.spider.normalize_url(url)
            self.assertEqual(
                normalized_url,
                expected_result,
                msg=f'{url} is not equal to {expected_result}',
            )
