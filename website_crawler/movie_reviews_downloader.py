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
movie review. The last line of the file will possess the date on which the
movie review was published.
"""

DATE_REGEX_PATTERN = '(\d{1,2}\s{0,1}de\s(?:Janeiro|Fevereiro|Março|Abril|Maio|Junho|Julho|Agosto|Setembro|Outubro|Novembro|Dezembro)\sde\s\d{4})' # noqa
MOVIE_FESTIVAL_REGEX = 'Observa\xe7\xe3o:[^\.]*\.{0,1}'
DIRECTED_BY_REGEX = 'Dirigido por[^\.]*\.{0,1}'
WITH_REGEX = '\s{0,1}Com:[^\.]*\.{0,1}'

date_regex = re.compile(DATE_REGEX_PATTERN)
festival_regex = re.compile(MOVIE_FESTIVAL_REGEX)
directed_regex = re.compile(DIRECTED_BY_REGEX)
with_regex = re.compile(WITH_REGEX)


class MovieCrawler:

    def __init__(self, base_url, movies_folder):
        self.base_url = base_url
        self.movies_folder = movies_folder

    def create_movie_review_url(self, code):
        raise NotImplementedError

    def get_movie_review(self, movie_url):
        raise NotImplementedError

    def parse_movie_title(self, movie_title):
        movie_title = movie_title.lower()
        movie_title = movie_title.replace(' ', '_')

        return movie_title

    def parse_response(self, movie_url):
        response = requests.get(movie_url)
        return BeautifulSoup(response.content, 'html.parser')

    def get_all_movie_reviews(self, movie_codes):
        invalid_movies = []
        for code in movie_codes:
            print('Downloading movie with code {} ...'.format(code))
            movie_url = self.create_movie_review_url(code)

            # try:
            #     movie_title, movie_stars, movie_review_array = self.get_movie_review(movie_url)
            # except:
            #     invalid_movies.append(code)
            #     continue
            movie_title, movie_stars, movie_review_array = self.get_movie_review(movie_url)

            if movie_review_array != -1:
                movie_title = self.parse_movie_title(movie_title)
                movie_file_path = os.path.join(self.movies_folder, movie_title + '.txt')
                self.create_movie_text(movie_file_path, movie_title,
                                       movie_stars, movie_review_array)

        print('\n Movies that could not be downloaded:\n')
        print(invalid_movies)

    def create_movie_text(self, movie_file_path, movie_title, movie_stars, movie_review_array):
        with open(movie_file_path, 'w') as movie_file:
            movie_file.write(movie_title + '\n')
            movie_file.write(movie_stars + '\n')

            for paragraph in movie_review_array:
                movie_file.write(paragraph + '\n')


class CinemaEmCenaCrawler(MovieCrawler):

    def get_movie_review(self, movie_url):
        movie_review_html = self.parse_response(movie_url)

        movie_title = movie_review_html.title.string
        movie_title = self.format_movie_title(movie_title)

        movie_stars = self.get_movie_number_of_stars(movie_review_html)

        movie_review_array = self.get_movie_review_text(movie_review_html)

        return (movie_title, movie_stars, movie_review_array)

    def format_movie_title(self, movie_title):
        return movie_title.split('|')[0].strip()

    def create_movie_review_url(self, review_id):
        return self.base_url + str(review_id)

    def get_movie_number_of_stars(self, movie_review_html):
        movie_stars_div = movie_review_html.find('div', {'class': 'rateit'})
        return movie_stars_div.attrs['data-rateit-value']

    def get_date_index_from_movie_review(self, movie_review_div):
        """
            The movie reviews found on the website have the full text inside a
            single HTML div. All movie reviews possess a paragraph containing the
            date when that particular movie review was written. This will be used
            as way to know when the movie review has ended.
        """
        index = -1

        for number, text in enumerate(movie_review_div.contents):
            if text != '\n':
                if date_regex.match(text.get_text().strip()):
                    index = number

        return index

    def get_last_paragraph(self, movie_review_div, movie_review_final_index):
        last_paragraph = movie_review_div.contents[movie_review_final_index]

        if last_paragraph == '\n':
            return False

        return last_paragraph.get_text()

    def check_for_critics_published_in_movie_festivals(self, movie_review_div,
                                                       movie_review_date_index):
        """
        When a movie review was produced during a movie festival, there is another
        paragraph inside the movie review, like the following example:

        'Texto originalmente publicado durante a cobertura do Festival de...'

        This method will be used to check if that is the case. If it is, the movie
        review should not include this paragraph as well.
        """
        last_paragraph = self.get_last_paragraph(movie_review_div, movie_review_date_index)

        if not last_paragraph:
            return False

        return last_paragraph.startswith('Texto originalmente publicado')

    def check_for_observation_in_movie_review(self, movie_review_div, movie_review_final_index):
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
        last_paragraph = self.get_last_paragraph(movie_review_div, movie_review_final_index)

        if not last_paragraph:
            return False

        is_festival_review = festival_regex.match(normalize('NFC', last_paragraph))

        return is_festival_review is not None

    def create_movie_review_array(self, movie_review_div, movie_review_final_paragraph):
        """
        The first three paragraphs of any movie review are not relevant, since they
        only possess some break line characters and the name of the movie director
        and the actors which were on the movie. Therefore, the count starts at
        the fourth paragraph.
        """
        movie_review = []
        for paragraph_number in range(2, movie_review_final_paragraph):
            paragraph = movie_review_div.contents[paragraph_number]
            if paragraph != '\n':
                movie_review.append(paragraph.get_text())

        return movie_review

    def get_date_paragraph(self, movie_review_div, movie_review_date_index):
        if movie_review_date_index == -1:
            return -1

        return movie_review_div.contents[movie_review_date_index].get_text()

    def remove_movie_festival_observation(self, movie_review_paragraph):
        return festival_regex.sub('', movie_review_paragraph)

    def remove_directed_by(self, movie_review_paragraph):
        return directed_regex.sub('', movie_review_paragraph)

    def remove_with_actor(self, movie_review_paragraph):
        return with_regex.sub('', movie_review_paragraph)

    def extract_date_from_review(self, movie_review_paragraph):
        if date_regex.search(movie_review_paragraph):
            movie_review_paragraph, date_review, _ = date_regex.split(
                movie_review_paragraph)

            return (movie_review_paragraph, date_review)
        else:
            return [-1, -1]

    def create_movie_review_from_single_paragraph(self, movie_review_div):
        movie_review_paragraph = ''
        for line in movie_review_div.contents:
            if line != '\n' and line.get_text():
                movie_review_paragraph = line.get_text()

        movie_review_paragraph = self.remove_movie_festival_observation(movie_review_paragraph)

        movie_review_paragraph = self.remove_directed_by(movie_review_paragraph)
        movie_review_paragraph = self.remove_with_actor(movie_review_paragraph)

        movie_review_paragraph, date_review = self.extract_date_from_review(movie_review_paragraph)

        if date_review != -1:
            return [movie_review_paragraph, date_review]
        else:
            return -1

    def get_movie_review_text(self, movie_review_html):
        movie_review_div = movie_review_html.find(
            'div', {'class': 'critica-conteudo'})

        """
        Some movie reviews are not in the paragraph format found on most of the
        text. Therefore, the whole movie review is inside a single paragraph.
        In that case, a different approach must be taken in order to extract the
        movie review from it.
        """
        if len(movie_review_div.contents) <= 5:
            return self.create_movie_review_from_single_paragraph(movie_review_div)

        movie_review_date_index = self.get_date_index_from_movie_review(movie_review_div)
        value = self.check_for_critics_published_in_movie_festivals(
            movie_review_div, movie_review_date_index - 2)

        date_paragraph = self.get_date_paragraph(movie_review_div, movie_review_date_index)

        if date_paragraph == -1:
            return -1

        movie_review_final_paragraph = movie_review_date_index

        if value:
            movie_review_final_paragraph = movie_review_final_paragraph - 3

        value = self.check_for_observation_in_movie_review(
            movie_review_div, movie_review_final_paragraph - 1)

        if value:
            movie_review_final_paragraph = movie_review_final_paragraph - 1

        movie_review_array = self.create_movie_review_array(movie_review_div,
                                                            movie_review_final_paragraph)

        movie_review_array.append(date_paragraph)
        return movie_review_array


class OmeleteCrawler(MovieCrawler):

    def create_movie_review_url(self, code):
        return code

    def get_movie_review(self, movie_url):
        movie_review_html = self.parse_response(movie_url)

        movie_title = self.get_movie_title(movie_review_html)
        movie_stars = self.get_movie_number_of_stars(movie_review_html)
        movie_review_array = self.create_movie_review_array(movie_review_html)

        return movie_title, movie_stars, movie_review_array

    def parse_movie_title(self, movie_title):
        raise NotImplementedError

    def create_movie_review_array(self, movie_review_html):
        movie_review_div = self.get_movie_review_div(movie_review_html)
        movie_review_array = []

        for paragraph in movie_review_div.contents:
            if paragraph != '\n':
                text = paragraph.get_text()
                movie_review_array.append(text)

        review_date = self.get_movie_review_date(movie_review_html)
        movie_review_array.append(review_date)

        return movie_review_array

    def get_movie_review_div(self, movie_review_html):
        return movie_review_html.find('div', itemprop='reviewBody')

    def get_movie_review_date(self, movie_review_html):
        review_date = movie_review_html.find('span', itemprop='datePublished')
        return review_date.contents[0].strip()

    def get_movie_number_of_stars(self, movie_review_html):
        review_rate = movie_review_html.find('span', itemprop='ratingValue')
        return review_rate['content']

    def get_movie_title(self, movie_review_html):
        movie_title = movie_review_html.find('div', {'class': 'original-title'})
        movie_title = movie_title.contents[0].strip()

        # Remove parenthesis from movie title
        return movie_title[1:-1]
