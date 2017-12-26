import requests

from bs4 import BeautifulSoup

from website_crawler.movie_reviews_downloader import get_movie_number_of_stars

"""
    This script will be used to search for on the cinema em cena website
    for the valid code associated with movie reviews. This script will try
    by default the codes between 5000 and 9000.

    Basically, it will compose an url with a code and try to request the page
    to see if it actually exists.

    All the valid codes are going to be stored inside a txt file.
"""


def search_for_valid_movie_codes(base_url, start_code, final_code):
    valid_movie_codes = []

    for code in range(start_code, final_code+1):
        print('Testing code {} ...'.format(code))
        response = requests.get(base_url + str(code))

        movie_review_html = BeautifulSoup(response.content, 'html.parser')
        movie_stars = get_movie_number_of_stars(movie_review_html)

        if movie_stars:
            valid_movie_codes.append(code)

    return valid_movie_codes


def search_for_omelete_urls(base_url, reviews_page_url, start_index, end_index):
    reviews_page_url += '?pagina={}#filters'
    review_urls = []

    for index in range(start_index, end_index + 1):
        reviews_page = reviews_page_url.format(index)
        review_urls.extend(get_omelete_urls_from_page(reviews_page, base_url))

    return review_urls


def get_omelete_urls_from_page(review_page_url, base_url):
    review_urls = []

    response = requests.get(review_page_url)
    review_html = BeautifulSoup(response.content, 'html.parser')
    reviews_div = review_html.findAll('div', {'class': 'call'})

    for review in reviews_div:
        review_url = review.find('a', href=True)['href']
        review_url = base_url + review_url
        review_urls.append(review_url)

        print('Found url: {}'.format(review_url))

    return review_urls
