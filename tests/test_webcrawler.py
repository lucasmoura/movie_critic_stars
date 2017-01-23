import unittest

from bs4 import BeautifulSoup
from website_crawler import movie_reviews_downloader as mrd


class WebCrawlerTest(unittest.TestCase):

    def test_date_index(self):
        with open('tests/files/movie_review_1.txt', 'r') as movie_text:
            movie_review = BeautifulSoup(movie_text, 'html.parser')

        movie_review = movie_review.find(
            'div', {'class': 'critica-conteudo'})

        expected = 25
        self.assertEqual(mrd.get_date_index_from_movie_review(movie_review),
                         expected)

        with open('tests/files/movie_review_2.txt', 'r') as movie_text:
            movie_review = BeautifulSoup(movie_text, 'html.parser')

        movie_review = movie_review.find(
            'div', {'class': 'critica-conteudo'})

        expected = 15
        self.assertEqual(mrd.get_date_index_from_movie_review(movie_review),
                         expected)
