import os
import random
import re

from website_crawler.movie_reviews_downloader import (INVALID_DIRECTOR, INVALID_ACTORS,
                                                      INVALID_MOVIE_TITLE)

from preprocessing.text_preprocessing import TextPreprocessing


TITLE_LINE = 0
DIRECTORS_LINE = 1
ACTORS_LINE = 2
REVIEW_LINE = 3
DATE_LINE = 4


def load_txts_in_folder(folder):
    txt_files = []

    for file_name in os.listdir(folder):
        if file_name.endswith('.txt'):
            text_path = os.path.join(folder, file_name)

            with open(text_path, 'r') as txt_file:
                txt_data = txt_file.read().split('\n')

            txt_files.append(txt_data)

    return txt_files


def split_files(files_array, percent):
    num_files_for_split = int(len(files_array) * percent)

    random.shuffle(files_array)

    split_array = files_array[0:num_files_for_split]
    files_array = files_array[num_files_for_split:]

    return files_array, split_array


def replace_in_text(regex, text, replace_str):
    return re.sub(regex, replace_str, text)


class MovieReviewDataset:

    def __init__(self, name, movie_folder, remove_director=False, director_str='<director>',
                 remove_actor=False, actor_str='<actor>', remove_title=False,
                 title_str='<title>'):
        self.name = name
        self.movie_folder = movie_folder

        self.remove_director = remove_director
        self.remove_actor = remove_actor
        self.remove_title = remove_title

        self.director_str = director_str
        self.actor_str = actor_str
        self.title_str = title_str

        self.text_preprocessing = TextPreprocessing()

    def load_movies_txts(self):
        self.txt_files = []

        for star in range(1, 6):
            movie_path = os.path.join(self.movie_folder, str(star))

            self.txt_files.append([(star, txt_file)
                                   for txt_file in load_txts_in_folder(movie_path)])

        return self.txt_files

    def remove_text_from_review(self, text, txt_file, review,
                                invalid_text, should_split, replacement_str):
        if text == invalid_text:
            return review

        regex = text
        regex = regex.replace('+', '\+')

        if should_split:
            regex_str = text.split(',')

            # Some of these verifications should be moved to the movie_reviews_downloader script
            regex_str = [name.strip() for name in regex_str]
            regex_str = [name.replace('[', '') for name in regex_str]
            regex_str = [name.replace('(', '\(') for name in regex_str]
            regex_str = [name.replace(')', '\)') for name in regex_str]
            regex_str = [name.replace('Com de : ', '') for name in regex_str]
            regex = r'|'.join(regex_str)

        return replace_in_text(regex, review, replacement_str)

    def remove_director_from_review(self, txt_file, review):
        directors = txt_file[DIRECTORS_LINE]
        return self.remove_text_from_review(directors, txt_file, review, INVALID_DIRECTOR, True,
                                            self.director_str)

    def remove_actors_from_review(self, txt_file, review):
        actors = txt_file[ACTORS_LINE]
        return self.remove_text_from_review(actors, txt_file, review, INVALID_ACTORS, True,
                                            self.actor_str)

    def remove_title_from_review(self, txt_file, review):
        title = txt_file[TITLE_LINE]
        return self.remove_text_from_review(title, txt_file, review, INVALID_MOVIE_TITLE, False,
                                            self.title_str)

    def format_txts_files(self):
        self.formatted_txt_files = []

        for review_grades in self.txt_files:
            formatted_grade_txt = []

            for label, txt_file in review_grades:
                review = self.text_preprocessing.remove_extra_spaces(
                    txt_file[REVIEW_LINE])

                if self.remove_director:
                    review = self.remove_director_from_review(txt_file, review)

                if self.remove_actor:
                    review = self.remove_actors_from_review(txt_file, review)

                if self.remove_title:
                    review = self.remove_title_from_review(txt_file, review)

                formatted_grade_txt.append((label, review))

            self.formatted_txt_files.append(formatted_grade_txt)

    def split_dataset(self, use_formatted, percent):
        self.split_files = []
        files = self.formatted_txt_files if use_formatted else self.txt_files

        for txt_file in files:
            txt_file, split_file = split_files(txt_file, percent=percent)

            self.split_files.append((txt_file, split_file))

    def generate_train_dataset(self):
        self.train_dataset = []

        for txt_file, _ in self.split_files:
            self.train_dataset.extend(txt_file)

    def generate_validation_dataset(self):
        self.validation_dataset = []

        for _, split_file in self.split_files:
            self.validation_dataset.extend(split_file[:len(split_file) // 2])

    def generate_test_dataset(self):
        self.test_dataset = []
        for _, split_file in self.split_files:
            self.test_dataset.extend(split_file[len(split_file) // 2:])

    def get_num_reviews(self):
        return len(self.train_dataset) + len(self.validation_dataset) + len(self.test_dataset)

    def extract_dataset(self):
        self.generate_train_dataset()
        self.generate_validation_dataset()
        self.generate_test_dataset()

    def create_dataset(self, percent=0.2):
        self.load_movies_txts()
        self.format_txts_files()
        self.split_dataset(use_formatted=True, percent=percent)
        self.extract_dataset()

    def print_info(self):
        print('--------------------------------------')
        print('{} Dataset:'.format(self.name.title()))
        print('Total number of reviews: {}'.format(self.get_num_reviews()))
        print('Train dataset: {}'.format(len(self.train_dataset)))
        print('Validation dataset: {}'.format(len(self.validation_dataset)))
        print('Test dataset: {}'.format(len(self.test_dataset)))
        print('\nNumber of revies')
        print('1 star reviews: {}'.format(len(self.txt_files[0])))
        print('2 star reviews: {}'.format(len(self.txt_files[1])))
        print('3 star reviews: {}'.format(len(self.txt_files[2])))
        print('4 star reviews: {}'.format(len(self.txt_files[3])))
        print('5 star reviews: {}'.format(len(self.txt_files[4])))
        print('--------------------------------------')
        print()
