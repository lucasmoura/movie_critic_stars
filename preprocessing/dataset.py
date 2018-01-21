import os
import random
import re

from website_crawler.movie_reviews_downloader import (INVALID_DIRECTOR, INVALID_ACTORS,
                                                      INVALID_MOVIE_TITLE)


TITLE_LINE = 0
DIRECTORS_LINE = 1
ACTORS_LINE = 2
REVIEW_LINE = 3
DATE_LINE = 4


def load_txts_in_folder(self, folder):
    txt_files = []

    for file_name in os.listdir(folder):
        if file_name.endswith('.txt'):
            text_path = os.path.join(folder, file_name)

            with open(text_path, 'r') as txt_file:
                txt_data = txt_file.read().split()

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

    def __init__(self, movie_folder, remove_director=False, director_str='<director>',
                 remove_actor=False, actor_str='<actor>', remove_title=False,
                 title_str='<title>'):
        self.movie_folder = movie_folder
        self.remove_director = remove_director
        self.remove_actor = remove_actor
        self.remove_title = remove_title

        self.director_str = director_str
        self.actor_str = actor_str
        self.title_str = title_str

    def load_movies_txts(self):
        self.txt_files = []

        for star in range(1, 5):
            movie_path = os.path.join(self.movie_folder, star)

            self.txt_files.append([(star, txt_file)
                                   for txt_file in load_txts_in_folder(movie_path)])

        return self.txt_files

    def remove_text_from_review(self, text, txt_file, invalid_text, should_split, replacement_str):
        if text == invalid_text:
            return txt_file[REVIEW_LINE]

        regex_str = text

        if should_split:
            regex_str = text.split(',')

        regex = r'|'.join(regex_str)

        return replace_in_text(regex, txt_file[REVIEW_LINE], replacement_str)

    def remove_director_from_review(self, txt_file):
        directors = txt_file[DIRECTORS_LINE]
        return self.remove_text_from_review(directors, txt_file, INVALID_DIRECTOR, True,
                                            self.director_str)

    def remove_actors_from_review(self, txt_file):
        actors = txt_file[ACTORS_LINE]
        return self.remove_text_from_review(actors, txt_file, INVALID_ACTORS, True,
                                            self.actor_str)

    def remove_title_from_review(self, txt_file):
        title = txt_file[TITLE_LINE]
        return self.remove_text_from_review(title, txt_file, INVALID_MOVIE_TITLE, True,
                                            self.title_str)

    def format_txts_files(self):
        self.formatted_txt_files = []

        for label, txt_file in self.txt_files:
            review = txt_file[REVIEW_LINE]

            if self.remove_director:
                review = self.remove_director_from_review(txt_file)

            if self.remove_actor:
                review = self.remove_actors_from_review(txt_file)

            if self.remove_title:
                review = self.remove_title(txt_file)

            self.format_txts_files.append((label, review))

    def split_dataset(self, percent):
        self.split_files = []
        for txt_file in self.txt_files:
            txt_file, split_file = split_files(txt_file, percent=percent)

            self.split_files.append((txt_file, split_file))

    def generate_train_dataset(self):
        self.train_dataset = []
        self.train_dataset.extend([txt_file for txt_file, _ in self.split_files])

    def generate_validation_dataset(self):
        self.validation_dataset = []
        self.validation_dataset.extend(
            [split_file for _, split_file in self.split_files[:len(self.split_files) // 2]])

    def generate_test_dataset(self):
        self.test_dataset = []
        self.test_dataset.extend(
            [split_file for _, split_file in self.split_files[len(self.split_files) // 2:]])

    def combine_datasets(self):
        self.generate_train_dataset()
        self.generate_validation_dataset()
        self.generate_test_dataset()

    def create_dataset(self, percent=0.2):
        self.load_movies_txts()
        self.format_txts_files()
        self.split_dataset(percent=percent)
        self.extract_dataset()
