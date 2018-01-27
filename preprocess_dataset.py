import argparse
import random

from preprocessing.dataset import MovieReviewDataset
from preprocessing.text_preprocessing import get_vocab, get_preprocessing_strategy


def apply_preprocessing(reviews_array, preprocessing_strat):
    preprocessed_reviews = []
    for (label, review) in reviews_array:
        preprocessed_review = preprocessing_strat.apply_preprocessing(review)

        preprocessed_reviews.append((label, preprocessed_review))

    return preprocessed_reviews


def apply_preprocessing_to_dataset(train, validation, test, user_args):
    preprocessing_type = user_args['preprocessing_type']
    stopwords_path = user_args['stopwords_path']
    preprocessing_strat = get_preprocessing_strategy(preprocessing_type, stopwords_path)

    preprocessed_train = apply_preprocessing(train, preprocessing_strat)
    preprocessed_validation = apply_preprocessing(validation, preprocessing_strat)
    preprocessed_test = apply_preprocessing(test, preprocessing_strat)

    return preprocessed_train, preprocessed_validation, preprocessed_test


def combine_datasets(omelete_dataset, cec_dataset, cineclick_dataset):
    train_dataset = omelete_dataset.train_dataset + cec_dataset.train_dataset
    train_dataset = train_dataset + cineclick_dataset.train_dataset

    validation_dataset = omelete_dataset.validation_dataset + cec_dataset.validation_dataset
    validation_dataset = validation_dataset + cineclick_dataset.validation_dataset

    test_dataset = omelete_dataset.test_dataset + cec_dataset.test_dataset
    test_dataset = test_dataset + cineclick_dataset.test_dataset

    random.shuffle(train_dataset)
    random.shuffle(validation_dataset)
    random.shuffle(test_dataset)

    return train_dataset, validation_dataset, test_dataset


def create_argument_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('-of',
                        '--omelete-folder',
                        type=str,
                        help='The path of the omelete reviews folder',
                        required=True)

    parser.add_argument('-cf',
                        '--cineclick-folder',
                        type=str,
                        help='The path of the cineclick reviews folder',
                        required=True)

    parser.add_argument('-cecf',
                        '--cec-folder',
                        type=str,
                        help='The path of the cinema em cena reviews folder',
                        required=True)

    parser.add_argument('-pt',
                        '--preprocessing-type',
                        type=str,
                        help='The type of preprocessing to use',
                        required=True)

    parser.add_argument('-sp',
                        '--stopwords-path',
                        type=str,
                        help='The path of the stop words file',
                        required=True)
    return parser


def main():
    parser = create_argument_parser()
    user_args = vars(parser.parse_args())

    omelete_folder = user_args['omelete_folder']
    omelete_dataset = MovieReviewDataset(
            'omelete',
            omelete_folder,
            remove_director=True,
            director_str='',
            remove_actor=True,
            actor_str='',
            remove_title=True,
            title_str='')

    cineclick_folder = user_args['cineclick_folder']
    cineclick_dataset = MovieReviewDataset(
            'cineclick',
            cineclick_folder,
            remove_director=True,
            director_str='',
            remove_actor=True,
            actor_str='',
            remove_title=True,
            title_str='')

    cec_folder = user_args['cec_folder']
    cec_dataset = MovieReviewDataset(
            'cinema em cena',
            cec_folder,
            remove_director=True,
            director_str='',
            remove_actor=True,
            actor_str='',
            remove_title=True,
            title_str='')

    omelete_dataset.create_dataset()
    cineclick_dataset.create_dataset()
    cec_dataset.create_dataset()

    omelete_dataset.print_info()
    cineclick_dataset.print_info()
    cec_dataset.print_info()

    print('Combining datasets ...')
    train, validation, test = combine_datasets(
        omelete_dataset, cec_dataset, cineclick_dataset)

    print('Creating vocabulary ...')
    train_vocab = get_vocab(train)

    print('Apply data preprocessing step to datasets ...')
    train, validation, test = apply_preprocessing_to_dataset(train, validation, test, user_args)


if __name__ == '__main__':
    main()
