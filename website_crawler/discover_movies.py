import requests

from bs4 import BeautifulSoup

from website_crawler.movie_reviews_downloader import CinemaEmCenaCrawler


def search_for_valid_movie_codes(base_url, start_code, final_code):
    valid_movie_codes = []
    cec = CinemaEmCenaCrawler(base_url, None, None)

    for code in range(start_code, final_code+1):
        print('Testing code {} ...'.format(code))
        response = requests.get(base_url + str(code))

        movie_review_html = BeautifulSoup(response.content, 'html.parser')
        movie_stars = cec.get_movie_number_of_stars(movie_review_html)

        if movie_stars:
            valid_movie_codes.append(code)

    return valid_movie_codes


class MovieUrlFinder:

    def __init__(self, base_url, reviews_page_url, start_index, end_index):
        self.base_url = base_url
        self.reviews_page_url = reviews_page_url
        self.start_index = start_index
        self.end_index = end_index

    def search_for_urls(self):
        self.reviews_page_url += self.get_reviews_page_indexer()
        review_urls = []

        for index in range(self.start_index, self.end_index + 1):
            reviews_page = self.reviews_page_url.format(index)
            review_urls.extend(self.get_urls_from_page(reviews_page))

        return review_urls

    def get_urls_from_page(self, reviews_page):
        review_urls = []

        review_html = self.parse_review_page(reviews_page)
        reviews_div = self.get_reviews_div(review_html)

        for review in reviews_div:
            review_url = review.find('a', href=True)['href']
            review_url = self.create_review_url(review_url)
            review_urls.append(review_url)

            print('Found url: {}'.format(review_url))

        return review_urls

    def parse_review_page(self, reviews_page):
        response = requests.get(reviews_page)
        return BeautifulSoup(response.content, 'html.parser')

    def get_reviews_page_indexer(self):
        raise NotImplementedError

    def get_reviews_div(self):
        raise NotImplementedError

    def create_review_url(self, review_url):
        raise NotImplementedError


class OmeleteUrlFinder(MovieUrlFinder):

    def get_reviews_div(self, review_html):
        return review_html.findAll('div', {'class': 'call'})

    def get_reviews_page_indexer(self):
        return '?pagina={}#filters'

    def create_review_url(self, review_url):
        return self.base_url + review_url


class CineclickUrlFinder(MovieUrlFinder):

    def get_reviews_page_indexer(self):
        return '?page={}'

    def get_reviews_div(self, review_html):
        return review_html.findAll('div', {'class': 'item'})

    def create_review_url(self, review_url):
        return self.base_url + review_url
