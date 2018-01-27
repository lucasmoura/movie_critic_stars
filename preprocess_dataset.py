import argparse
import random

from preprocessing.dataset import MovieReviewDataset
from preprocessing.text_preprocessing import get_vocab, get_preprocessing_strategy
from word_embedding.word_embedding import FastTextEmbedding


def replace_unknown_words(train, validation, test, word_embedding):
    train = word_embedding.handle_unknown_words(train, sentence_size=None)
    validation = word_embedding.handle_unknown_words(validation, sentence_size=None)
    test = word_embedding.handle_unknown_words(test, sentence_size=None)

    return train, validation, test


def load_embeddings(user_args, vocab):
    embedding_file = user_args['embedding_file']
    embed_size = user_args['embed_size']
    embedding_path = user_args['embedding_path']
    embedding_wordindex_path = user_args['embedding_wordindex_path']

    return FastTextEmbedding(embedding_file, embed_size, vocab, embedding_path,
                             embedding_wordindex_path)


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

    parser.add_argument('-ef',
                        '--embedding-file',
                        type=str,
                        help='The location of the embedding file')

    parser.add_argument('-ep',
                        '--embedding-path',
                        type=str,
                        help='Location of the embedding file (Testing Dataset Only)')

    parser.add_argument('-ewi',
                        '--embedding-wordindex-path',
                        type=str,
                        help='Location of the embedding word index file (Testing Dataset Only)')

    parser.add_argument('-es',
                        '--embed-size',
                        type=int,
                        help='The embedding size of the embedding file')
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

    word_embedding = load_embeddings(user_args, train_vocab)
    word_index, matrix, embedding_vocab = word_embedding.get_word_embedding()

    print('Apply data preprocessing step to datasets ...')
    train, validation, test = apply_preprocessing_to_dataset(train, validation, test, user_args)

    print('Find and replacing unknown words for reviews...')
    train, validation, test = replace_unknown_words(train, validation, test, word_embedding)
    print()


if __name__ == '__main__':
    main()
