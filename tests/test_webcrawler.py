import unittest

from bs4 import BeautifulSoup
from website_crawler import movie_reviews_downloader as mrd


class WebCrawlerTest(unittest.TestCase):

    def setUp(self):
        self.cec = mrd.CinemaEmCenaCrawler(None, None, None)

    def test_date_index(self):
        with open('tests/files/movie_review_1.txt', 'r') as movie_text:
            movie_review = BeautifulSoup(movie_text, 'html.parser')

        movie_review = movie_review.find(
            'div', {'class': 'critica-conteudo'})

        expected = 25
        self.assertEqual(self.cec.get_date_index_from_movie_review(movie_review),
                         expected)

        with open('tests/files/movie_review_2.txt', 'r') as movie_text:
            movie_review = BeautifulSoup(movie_text, 'html.parser')

        movie_review = movie_review.find(
            'div', {'class': 'critica-conteudo'})

        expected = 15
        self.assertEqual(self.cec.get_date_index_from_movie_review(movie_review),
                         expected)

        with open('tests/files/movie_review_5.txt', 'r') as movie_text:
            movie_review = BeautifulSoup(movie_text, 'html.parser')

        movie_review = movie_review.find(
            'div', {'class': 'critica-conteudo'})

        expected = 11
        self.assertEqual(self.cec.get_date_index_from_movie_review(movie_review),
                         expected)

    def test_movie_festival_paragraph(self):
        with open('tests/files/movie_review_2.txt', 'r') as movie_text:
            movie_review = BeautifulSoup(movie_text, 'html.parser')

        movie_review = movie_review.find(
            'div', {'class': 'critica-conteudo'})

        expected = True
        date_index = self.cec.get_date_index_from_movie_review(movie_review)
        self.assertEqual(self.cec.check_for_critics_published_in_movie_festivals(
            movie_review, date_index - 2), expected)

        with open('tests/files/movie_review_1.txt', 'r') as movie_text:
            movie_review = BeautifulSoup(movie_text, 'html.parser')

        movie_review = movie_review.find(
            'div', {'class': 'critica-conteudo'})

        expected = False
        date_index = self.cec.get_date_index_from_movie_review(movie_review)
        self.assertEqual(self.cec.check_for_critics_published_in_movie_festivals(
            movie_review, date_index - 2), expected)

    def test_movie_additional_info(self):
        with open('tests/files/movie_review_2.txt', 'r') as movie_text:
            movie_review = BeautifulSoup(movie_text, 'html.parser')

        movie_review = movie_review.find(
            'div', {'class': 'critica-conteudo'})

        expected = False
        date_index = self.cec.get_date_index_from_movie_review(movie_review)
        self.assertEqual(self.cec.check_for_observation_in_movie_review(
            movie_review, date_index - 2), expected)

        with open('tests/files/movie_review_3.txt', 'r') as movie_text:
            movie_review = BeautifulSoup(movie_text, 'html.parser')

        movie_review = movie_review.find(
            'div', {'class': 'critica-conteudo'})

        expected = True
        date_index = self.cec.get_date_index_from_movie_review(movie_review)
        self.assertEqual(self.cec.check_for_observation_in_movie_review(
            movie_review, date_index - 1), expected)

        with open('tests/files/movie_review_4.txt', 'r') as movie_text:
            movie_review = BeautifulSoup(movie_text, 'html.parser')

        movie_review = movie_review.find(
            'div', {'class': 'critica-conteudo'})

        expected = True
        date_index = self.cec.get_date_index_from_movie_review(movie_review)
        self.assertEqual(self.cec.check_for_observation_in_movie_review(
            movie_review, date_index - 1), expected)
