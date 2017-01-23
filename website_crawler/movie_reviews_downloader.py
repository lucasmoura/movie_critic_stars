import requests
import re
import os

from bs4 import BeautifulSoup
from unicodedata import normalize

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
MOVIES_FOLDER = 'movies'

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


def get_last_paragraph(movie_review_div, movie_review_final_index):
    last_paragraph = movie_review_div.contents[movie_review_final_index]

    if last_paragraph == '\n':
        return False

    return last_paragraph.get_text()


def check_for_critics_published_in_movie_festivals(movie_review_div,
                                                   movie_review_date_index):
    """
    When a movie review was produced during a movie festival, there is another
    paragraph inside the movie review, like the following example:

    'Texto originalmente publicado durante a cobertura do Festival de...'

    This method will be used to check if that is the case. If it is, the movie
    review should not include this paragraph as well.
    """
    last_paragraph = get_last_paragraph(
        movie_review_div, movie_review_date_index)

    if not last_paragraph:
        return False

    return last_paragraph.startswith('Texto originalmente publicado')


def check_for_observation_in_movie_review(movie_review_div,
                                          movie_review_final_index):
    """
    Some movie review possess some additional observation at the end of the
    text, information readers about after credit scenes and any other
    information that the movie critic think it is relevant. However,
    this additional info should not be considered on the review itself and
    should be removed. An example of such paragraph can be seen on the
    following movie review:

    http://www.cinemaemcena.com.br/Critica/Filme/6049

    This method will be used to check if additional information can be found
    on the text.
    """
    last_paragraph = get_last_paragraph(
        movie_review_div, movie_review_final_index)

    if not last_paragraph:
        return False

    b = normalize('NFC', last_paragraph).startswith(
        normalize('NFC', 'Observa\xe7\xe3o:'))

    return b


def create_movie_review_array(movie_review_div, movie_review_final_paragraph):
    """
    The first three paragraphs of any movie review are not relevant, since they
    only possess some break line characters and the name of the movie director
    and the actors which were on the movie. Therefore, the count starts at at
    the fourth paragraph.
    """
    movie_review = []
    for paragraph_number in range(2, movie_review_final_paragraph):
        paragraph = movie_review_div.contents[paragraph_number]
        if paragraph != '\n':
            movie_review.append(paragraph.get_text())

    return movie_review


def get_movie_review_text(movie_review_html):
    movie_review_div = movie_review_html.find(
        'div', {'class': 'critica-conteudo'})

    movie_review_date_index = get_date_index_from_movie_review(
        movie_review_div)
    value = check_for_critics_published_in_movie_festivals(
        movie_review_div, movie_review_date_index - 2)

    movie_review_final_paragraph = movie_review_date_index
    if value:
        movie_review_final_paragraph = movie_review_final_paragraph - 3

    value = check_for_observation_in_movie_review(
        movie_review_div, movie_review_final_paragraph - 1)

    if value:
        movie_review_final_paragraph = movie_review_final_paragraph - 1

    return create_movie_review_array(
        movie_review_div, movie_review_final_paragraph)


def get_movie_review(review_id):
    movie_url = create_movie_review_url(review_id)

    response = requests.get(movie_url)
    movie_review_html = BeautifulSoup(response.content, 'html.parser')

    movie_title = movie_review_html.title.string
    movie_title = format_movie_title(movie_title)

    movie_stars = get_movie_number_of_stars(movie_review_html)

    movie_review_array = get_movie_review_text(movie_review_html)

    return (movie_title, movie_stars, movie_review_array)


def create_movies_folder():
    if not os.path.exists(MOVIES_FOLDER):
        os.makedirs(MOVIES_FOLDER)


def create_movie_text(movie_title, movie_stars, movie_review_array):
    movie_title_file = movie_title.lower()
    movie_title_file = movie_title_file.replace(' ', '_')

    movie_file_path = MOVIES_FOLDER + '/' + movie_title_file + '.txt'
    with open(movie_file_path, 'w') as movie_file:
        movie_file.write(movie_title + '\n')
        movie_file.write(movie_stars + '\n')

        for paragraph in movie_review_array:
            movie_file.write(paragraph + '\n')


def main():
    review_id = 8348
    movie_title, movie_stars, movie_review_array = get_movie_review(review_id)

    create_movies_folder()
    create_movie_text(movie_title, movie_stars, movie_review_array)


if __name__ == '__main__':
    main()
