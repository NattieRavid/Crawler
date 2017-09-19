import unittest

from .. import crawler


class SpiderTestCase(
    unittest.TestCase,
):
    def setUp(
        self,
    ):
        self.crawler = crawler.Crawler()

    def test_crawl(
        self,
    ):
        expected_visited_urls = (
            'bugmenot.com',
            'bugmenot.com/removal.php',
            'bugmenot.com/terms.php',
        )

        responses = self.crawler.crawl(
            domain='bugmenot.com',
        )
        responses = list(responses)

        self.assertEqual(
            len(responses),
            len(expected_visited_urls),
            msg='test crawl failed'
        )

        for response in responses:
            self.assertIn(
                response['url'],
                expected_visited_urls,
                msg='test crawl failed',
            )
            self.assertEqual(
                response['status_code'],
                200,
                msg='test crawl failed',
            )
