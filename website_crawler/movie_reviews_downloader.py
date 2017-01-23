import requests

from bs4 import BeautifulSoup

"""
This script is responsible for downloading the movie reviews written by
Mr. Pablo Villaca. This script will store each movie review in unique file.
This file will possess two lines and the review itself. The first line will
present the movie title and the second line, the number of stars the movie
received. Afther these two lines, the rest of the file will be populated by the
movie review.
"""

BASE_URL = 'http://www.cinemaemcena.com.br/Critica/Filme/{}'


def format_movie_title(movie_title):
    return movie_title.split('|')[0].strip()


def create_movie_review_url(review_id):
    return BASE_URL.format(review_id)


def get_movie_number_of_stars(movie_review_html):
    movie_stars_div = movie_review_html.find('div', {'class': 'rateit'})
    return movie_stars_div.attrs['data-rateit-value']


def get_movie_review(review_id):
    movie_url = create_movie_review_url(review_id)

    response = requests.get(movie_url)
    movie_review_html = BeautifulSoup(response.content, 'html.parser')

    movie_title = movie_review_html.title.string
    movie_title = format_movie_title(movie_title)

    movie_stars = get_movie_number_of_stars(movie_review_html)


def main():
    review_id = 8326
    get_movie_review(review_id)


if __name__ == '__main__':
    main()
