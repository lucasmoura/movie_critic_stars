import os
import random


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


class MovieReviewDataset:

    def __init__(self, movie_folder):
        self.movie_folder = movie_folder

    def load_movies_txts(self):
        self.txt_files = []

        for star in range(1, 5):
            movie_path = os.path.join(self.movie_folder, star)

            self.txt_files.append([(star, txt_file)
                                   for txt_file in load_txts_in_folder(movie_path)])

        return self.txt_files

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
        self.split_dataset(percent=percent)
        self.extract_dataset()
