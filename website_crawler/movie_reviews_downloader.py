import requests
import re
import os
import bs4

from bs4 import BeautifulSoup
from unicodedata import normalize

from utils.folder import create_folder

"""
This script is responsible for downloading the movie reviews written by
Mr. Pablo Villaca. This script will store each movie review in unique file.
This file will possess two lines and the review itself. The first line will
present the movie title and the second line, the number of stars the movie
received. Afther these two lines, the rest of the file will be populated by the
movie review. The last line of the file will possess the date on which the
movie review was published.
"""


INVALID_DIRECTOR = 'INVALID_DIRECTOR'
INVALID_MOVIE_TITLE = 'INVALID_MOVIE_TITLE'
INVALID_STARS = 'INVALID_STARS'
INVALID_ACTORS = 'INVALID_ACTORS'
PROCESSING_ERROR = 'PROCESSING_ERROR'


class MovieReview:

    def __init__(self, movie_title, movie_stars, movie_director, movie_actors,
                 movie_review_array, error_message=None):
        self.movie_title = movie_title
        self.movie_stars = movie_stars
        self.movie_director = movie_director
        self.movie_actors = movie_actors
        self.movie_review_array = movie_review_array
        self.error_message = error_message


class MovieCrawler:

    def __init__(self, base_url, movies_folder, invalid_movies_log):
        self.base_url = base_url
        self.movies_folder = movies_folder
        self.invalid_movies_log = invalid_movies_log
        self.months_dict = {'Janeiro': '1', 'Fevereiro': '2', 'Março': '3',
                            'Abril': '4', 'Maio': '5', 'Junho': '6',
                            'Julho': '7', 'Agosto': '8', 'Setembro': '9',
                            'Outubro': '10', 'Novembro': '11', 'Dezembro': '12'}

    def create_movie_review_url(self, code):
        raise NotImplementedError

    def get_movie_review(self, movie_url):
        raise NotImplementedError

    def format_date(self, date_text):
        raise NotImplementedError

    def parse_movie_title(self, movie_title):
        movie_title = movie_title.lower()
        movie_title = movie_title.replace(' ', '_')

        return movie_title

    def parse_response(self, movie_url):
        response = requests.get(movie_url)
        return BeautifulSoup(response.content, 'html.parser')

    def create_star_folders(self):
        for i in range(1, 6):
            star_path = os.path.join(self.movies_folder, str(i))
            create_folder(star_path)

    def save_invalid_movies(self, invalid_movies):
        with open(self.invalid_movies_log, 'w') as invalid_movies_file:
            for code, message in invalid_movies:
                invalid_movies_file.write(str(code) + ': ' + message + '\n')

    def get_all_movie_reviews(self, movie_codes):
        self.create_star_folders()

        invalid_movies = []

        for code in movie_codes:
            print('Downloading movie with code {} ...'.format(code))
            movie_url = self.create_movie_review_url(code)

            try:
                movie_review = self.get_movie_review(movie_url)
            except:
                invalid_movies.append((code, PROCESSING_ERROR))
                continue

            movie_review_array = movie_review.movie_review_array
            movie_title = movie_review.movie_title
            movie_stars = movie_review.movie_stars
            movie_director = movie_review.movie_director
            movie_actors = movie_review.movie_actors

            if movie_review_array != -1:
                original_title = movie_title
                movie_title = self.parse_movie_title(movie_title)
                movie_file_path = os.path.join(self.movies_folder, movie_stars)
                movie_file_path = os.path.join(movie_file_path, movie_title + '.txt')
                self.create_movie_text(movie_file_path, movie_title, original_title,
                                       movie_director, movie_actors, movie_review_array)
            else:
                error_message = movie_review.error_message
                invalid_movies.append((code, error_message))

        self.save_invalid_movies(invalid_movies)

    def create_movie_text(self, movie_file_path, movie_title, original_title, movie_director,
                          movie_actors, movie_review_array):
        with open(movie_file_path, 'w') as movie_file:
            movie_file.write(original_title + '\n')
            movie_file.write(movie_director + '\n')
            movie_file.write(movie_actors + '\n')

            for paragraph in movie_review_array:
                movie_file.write(paragraph + '\n')


class CinemaEmCenaCrawler(MovieCrawler):

    DATE_REGEX_PATTERN = '(\d{1,2}\s{0,1}de\s(?:Janeiro|Fevereiro|Março|Abril|Maio|Junho|Julho|Agosto|Setembro|Outubro|Novembro|Dezembro)\sde\s\d{4})' # noqa
    MOVIE_FESTIVAL_REGEX = 'Observa\xe7\xe3o:[^\.]*\.{0,1}'
    DIRECTED_BY_REGEX = 'Dirigido por[^\.]*\.{0,1}'
    WITH_REGEX = '\s{0,1}Com:[^\.]*\.{0,1}'
    CAST_REGEX = '[\w\s]*</a>'

    def __init__(self, base_url, movies_folder, invalid_movies_log):
        self.date_regex = re.compile(CinemaEmCenaCrawler.DATE_REGEX_PATTERN)
        self.festival_regex = re.compile(CinemaEmCenaCrawler.MOVIE_FESTIVAL_REGEX)
        self.directed_regex = re.compile(CinemaEmCenaCrawler.DIRECTED_BY_REGEX)
        self.with_regex = re.compile(CinemaEmCenaCrawler.WITH_REGEX)
        self.cast_regex = re.compile(CinemaEmCenaCrawler.CAST_REGEX)

        super().__init__(base_url, movies_folder, invalid_movies_log)

    def get_movie_review(self, movie_url):
        movie_review_html = self.parse_response(movie_url)

        movie_title = movie_review_html.title.string
        movie_title = self.format_movie_title(movie_title)
        movie_stars = self.get_movie_number_of_stars(movie_review_html)
        movie_director = self.get_movie_director(movie_review_html)
        movie_actors = self.get_movie_actors(movie_review_html)
        movie_review_array = self.get_movie_review_text(movie_review_html)

        movie_review = MovieReview(movie_title, movie_stars, movie_director,
                                   movie_actors, movie_review_array)

        return movie_review

    def format_date(self, date_text):
        date_text = date_text.replace('de', '')
        date_parts = date_text.split()

        date_parts[1] = self.months_dict[date_parts[1]]

        return '/'.join(date_parts)

    def format_movie_title(self, movie_title):
        return movie_title.split('|')[0].strip()

    def create_movie_review_url(self, review_id):
        return self.base_url + str(review_id)

    def parse_cast_str(self, cast_str):
        movie_cast = self.cast_regex.findall(cast_str)

        if not movie_cast:
            return []

        # Rermove </a>
        movie_cast = [cast[:-4] for cast in movie_cast]

        if len(movie_cast) > 1:
            return ','.join(movie_cast)
        else:
            return movie_cast[0]

    def get_movie_director(self, movie_review_html):
        movie_cast = movie_review_html.find('div', {'class': 'critica-elenco'})

        if movie_cast:
            movie_cast_str = movie_cast.decode()
            movie_directors_str = movie_cast_str[:movie_cast_str.find('Elenco')]
            directors = self.parse_cast_str(movie_directors_str)

            if not directors:
                return INVALID_DIRECTOR

            return directors

        return INVALID_DIRECTOR

    def get_movie_actors(self, movie_review_html):
        movie_cast = movie_review_html.find('div', {'class': 'critica-elenco'})

        if movie_cast:
            movie_actors_str = movie_cast.decode()
            movie_actors_str = movie_actors_str[
                movie_actors_str.find('Elenco'):movie_actors_str.find('Roteiro')]
            actors = self.parse_cast_str(movie_actors_str)

            if not actors:
                return INVALID_ACTORS

            return actors

        return INVALID_ACTORS

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
                if self.date_regex.match(text.get_text().strip()):
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

    def check_for_observation_in_movie_review(self, paragraph_text):
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
        is_festival_review = self.festival_regex.match(normalize('NFC', paragraph_text))

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
                paragraph = paragraph.get_text().strip()

                if self.check_for_observation_in_movie_review(paragraph):
                    continue

                if paragraph:
                    movie_review.append(paragraph)

        return movie_review

    def get_date_paragraph(self, movie_review_div, movie_review_date_index):
        if movie_review_date_index == -1:
            return -1

        return movie_review_div.contents[movie_review_date_index].get_text()

    def remove_movie_festival_observation(self, movie_review_paragraph):
        return self.festival_regex.sub('', movie_review_paragraph)

    def remove_directed_by(self, movie_review_paragraph):
        return self.directed_regex.sub('', movie_review_paragraph)

    def remove_with_actor(self, movie_review_paragraph):
        return self.with_regex.sub('', movie_review_paragraph)

    def extract_date_from_review(self, movie_review_paragraph):
        if self.date_regex.search(movie_review_paragraph):
            movie_review_paragraph, date_review, _ = self.date_regex.split(
                movie_review_paragraph)

            return (movie_review_paragraph, date_review)
        else:
            return (movie_review_paragraph, -1)

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
            return movie_review_paragraph

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

        movie_review_final_paragraph = movie_review_date_index

        if date_paragraph == -1:
            movie_review_final_paragraph = len(movie_review_div.contents) - 1

        if value:
            movie_review_final_paragraph = movie_review_final_paragraph - 3

        movie_review_array = self.create_movie_review_array(movie_review_div,
                                                            movie_review_final_paragraph)
        if date_paragraph != -1:
            date_paragraph = self.format_date(date_paragraph)
            movie_review_array.append(date_paragraph)

        return movie_review_array


class OmeleteCrawler(MovieCrawler):

    def create_movie_review_url(self, code):
        return code

    def get_movie_review(self, movie_url):
        movie_review_html = self.parse_response(movie_url)

        movie_title = self.get_movie_title(movie_review_html)
        movie_stars = self.get_movie_number_of_stars(movie_review_html)
        movie_director = self.get_movie_director(movie_review_html)
        error_message = None

        if movie_title == -1:
            movie_review_array = -1
            error_message = INVALID_MOVIE_TITLE
        elif movie_stars == -1:
            movie_review_array = -1
            error_message = INVALID_STARS
        else:
            movie_review_array = self.create_movie_review_array(movie_review_html)

        movie_review = MovieReview(movie_title, movie_stars, movie_director, movie_review_array,
                                   error_message)

        return movie_review

    def check_text(self, text):
            if not text:
                return False

            if text.startswith('Leia mais'):
                return False

            if text.endswith('filme est\xE1 passando'):
                return False

            if text.endswith('filme est\xE1 sendo exibido'):
                return False

            if 'Cinemas e hor\xE1rios' in text:
                return False

            if text.endswith('Clipes'):
                return False

            if text.endswith('Trailer legendado'):
                return False

            if 'Omelete entrevista' in text:
                return False

            if 'Omelete Entrevista' in text:
                return False

            if '| Assista' in text:
                return False

            if '| Cinemas' in text:
                return False

            if '| Trailer' in text:
                return False

            if '| Entrevistas' in text:
                return False

            if 'Acompanhe as nossas' in text:
                return False

            if 'Veja clipes' in text:
                return False

            if 'Baixe of filmes' in text:
                return False

            if text.startswith('Confira nosso especial'):
                return False

            return True

    def format_date(self, date_text):
        return date_text.split('-')[0].strip()

    def create_movie_review_array(self, movie_review_html):
        movie_review_div = self.get_movie_review_div(movie_review_html)
        movie_review_array = []

        for paragraph in movie_review_div.contents:
            if type(paragraph) != bs4.element.NavigableString:
                text = paragraph.get_text()
            else:
                text = paragraph.replace('\n', ' ').strip()

            text = text.replace('\n', ' ').strip()

            if self.check_text(text):
                movie_review_array.append(text)

        review_date = self.get_movie_review_date(movie_review_html)
        review_date = self.format_date(review_date)
        movie_review_array.append(review_date)

        return movie_review_array

    def get_movie_review_div(self, movie_review_html):
        return movie_review_html.find('div', itemprop='reviewBody')

    def get_movie_review_date(self, movie_review_html):
        review_date = movie_review_html.find('span', itemprop='datePublished')
        return review_date.contents[0].strip()

    def get_movie_number_of_stars(self, movie_review_html):
        sem_nota = movie_review_html.find('span', {'class': 'nota-texto'}).contents[0]

        if sem_nota and 'Sem nota' in sem_nota:
            return -1

        review_rate = movie_review_html.find('span', itemprop='ratingValue')
        return review_rate['content']

    def get_movie_title(self, movie_review_html):
        movie_title = movie_review_html.find('div', {'class': 'title'})

        if not movie_title:
            return -1

        movie_title = movie_title.get('content', '')

        if not movie_title:
            movie_title = movie_review_html.find('h1', {'class': 'title'})

            if not movie_title:
                return INVALID_MOVIE_TITLE

            movie_title = movie_title.get_text().split('|')[0].strip()
        else:
            movie_title = movie_title.replace('/', '')

        return movie_title

    def get_movie_director(self, movie_review_html):
        movie_director = movie_review_html.find('div', itemprop='director')

        if movie_director:
            movie_director = movie_director.find('span', itemprop='name')['content']

        if not movie_director:
            return INVALID_DIRECTOR

        return movie_director.strip()


class CineclickCrawler(MovieCrawler):
    DATE_REGEX_PATTERN = '(\d{1,2}\s{0,1}de\s(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\sde\s\d{4})' # noqa

    def __init__(self, base_url, movies_folder, invalid_movies_log):
        self.date_regex = re.compile(CineclickCrawler.DATE_REGEX_PATTERN)

        super().__init__(base_url, movies_folder, invalid_movies_log)

    def create_movie_review_url(self, code):
        return code

    def get_movie_review(self, movie_url):
        movie_review_html = self.parse_response(movie_url)

        movie_title = self.get_movie_title(movie_review_html)
        movie_director = self.get_movie_director(movie_review_html)
        movie_stars = self.get_movie_number_of_stars(movie_review_html)
        error_message = None

        if movie_title == -1:
            movie_review_array = -1
            error_message = INVALID_MOVIE_TITLE
        elif movie_stars == -1:
            movie_review_array = -1
            error_message = INVALID_STARS
        else:
            movie_review_array = self.create_movie_review_array(movie_review_html)

        movie_review = MovieReview(movie_title, movie_stars, movie_director, movie_review_array,
                                   error_message)

        return movie_review

    def remove_reviewer_info(self, text):
        string_match = self.date_regex.search(text)

        if not string_match:
            return text

        info_str = string_match.group(0)

        text = text[:text.find(info_str)]
        return text.strip()

    def format_date(self, date_text):
        return date_text.split()[0].strip()

    def create_movie_review_array(self, movie_review_html):
        movie_review_div = self.get_movie_review_div(movie_review_html)
        movie_review_array = []

        for paragraph in movie_review_div.contents:
            if type(paragraph) != bs4.element.NavigableString:
                text = paragraph.get_text()
            else:
                text = paragraph.replace('\n', ' ').strip()

            text = text.replace('\n', ' ').strip()
            text = text.replace(u'\xa0', u' ')

            if text:
                text = self.remove_reviewer_info(text)
                movie_review_array.append(text)

        review_date = self.get_movie_review_date(movie_review_html)
        movie_review_array.append(review_date)

        return movie_review_array

    def get_movie_review_div(self, movie_review_html):
        return movie_review_html.find('div', {'class': 'body color-gray'})

    def get_movie_review_date(self, movie_review_html):
        review_date = movie_review_html.find('span', {'class': 'time'})
        review_date = review_date.get_text().strip()

        return self.format_date(review_date)

    def get_movie_number_of_stars(self, movie_review_html):
        movie_stars_div = movie_review_html.find('div', {'class': 'rating'})

        if movie_stars_div:
            movie_stars = movie_stars_div.decode().count('active')
            return str(movie_stars)

        return -1

    def get_movie_title(self, movie_review_html):
        movie_title_div = movie_review_html.find('div', {'id': 'breadcrumb'})

        if not movie_title_div:
            return -1

        movie_title_ul = movie_title_div.find('ul')

        if not movie_title_ul:
            return -1

        movie_title_li = movie_title_ul.findAll('li')

        if not movie_title_li:
            return -1

        # The movie title is in the third entry of the list
        movie_title = movie_title_li[2].get_text().strip()
        movie_title = movie_title.replace('/', '')

        return movie_title.title()

    def get_movie_director(self, movie_review_html):
        movie_director = movie_review_html.find('ul', {'class': 'directors'})

        movie_directors = None
        if movie_director:
            movie_directors = movie_director.findAll('li')

        if movie_directors:
            directors = []
            for director in movie_directors:
                directors.append(director.get_text().strip())

            if len(directors) > 1:
                return ','.join(directors)
            else:
                return directors[0]

        return INVALID_DIRECTOR
