import unittest

from website_crawler import movie_reviews_downloader as mrd


class CineclickCrawlerTest(unittest.TestCase):

    def setUp(self):
        self.cineclick = mrd.CineclickCrawler(None, None, None)

    def test_format_date(self):
        expected = '20/11/2011'
        test_string = '20/11/2011 16h02'

        self.assertEqual(
            self.cineclick.format_date(test_string), expected)
