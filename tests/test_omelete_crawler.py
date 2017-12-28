import unittest

from website_crawler import movie_reviews_downloader as mrd


class OmeleteCrawlerTest(unittest.TestCase):

    def setUp(self):
        self.omelete = mrd.OmeleteCrawler(None, None, None)

    def test_format_date(self):
        expected = '26/10/2006'
        test_string = '26/10/2006 - 0:00'

        self.assertEqual(
            self.omelete.format_date(test_string), expected)
