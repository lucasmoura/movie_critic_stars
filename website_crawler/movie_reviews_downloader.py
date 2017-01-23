import requests
import re
import json

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
DATE_REGEX_PATTERN = '\d{2}\sde\s(Janeiro|Fevereiro|Março|Abril|Maio|Junho|Julho|Agosto|Setembro|Outubro|Novembro|Dezembro)\sde\s\d{4}' # noqa

date_regex = re.compile(DATE_REGEX_PATTERN)


def format_movie_title(movie_title):
    return movie_title.split('|')[0].strip()


def create_movie_review_url(review_id):
    return BASE_URL.format(review_id)


def get_movie_number_of_stars(movie_review_html):
    movie_stars_div = movie_review_html.find('div', {'class': 'rateit'})
    return movie_stars_div.attrs['data-rateit-value']


def get_date_index_from_movie_review(movie_review_div):
    """
        The movie reviews found on the website have the full text inside a
        single HTML div. All movie reviews possess a paragraph containing the
        date when that particular movie review was written. This will be used
        as way to know when the movie review has ended.
    """
    index = -1

    for number, text in enumerate(movie_review_div.contents):
        if text != '\n':
            if date_regex.match(text.get_text()):
                index = number

    return index


def check_for_critics_published_in_movie_festivals(movie_review_div,
                                                   movie_review_date_index):
    """
    When a movie review was produced during a movie festival, there is another
    paragraph inside the movie review, like the following example:

    'Texto originalmente publicado durante a cobertura do Festival de...'

    This method will be used to check if that is the case. If it is, the movie
    review should not include this paragraph as well.
    """
    last_paragraph = movie_review_div.contents[movie_review_date_index]

    if last_paragraph == '\n':
        return False

    last_paragraph = last_paragraph.get_text()
    return last_paragraph.startswith('Texto originalmente publicado')


def get_movie_review_text(movie_review_html):
    movie_review_div = movie_review_html.find(
        'div', {'class': 'critica-conteudo'})

    import ipdb; ipdb.set_trace()
    movie_review_date_index = get_date_index_from_movie_review(
        movie_review_div)
    value = check_for_critics_published_in_movie_festivals(
        movie_review_div, movie_review_date_index)

    movie_review_final_paragraph = movie_review_date_index
    if value:
        movie_review_final_paragraph = movie_review_final_paragraph - 1

    print(movie_review_final_paragraph)


def get_movie_review(review_id):
    movie_url = create_movie_review_url(review_id)

    response = requests.get(movie_url)
    movie_review_html = BeautifulSoup(response.content, 'html.parser')

    movie_title = movie_review_html.title.string
    movie_title = format_movie_title(movie_title)

    movie_stars = get_movie_number_of_stars(movie_review_html)

    movie_review_text = get_movie_review_text(movie_review_html)

    return (movie_title, movie_stars, movie_review_text)


def main():
    review_id = 8348
    get_movie_review(review_id)


if __name__ == '__main__':
    main()
