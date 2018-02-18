import argparse
import os
import random

import numpy as np
import tensorflow as tf

from collections import defaultdict, Counter
from imblearn.over_sampling import RandomOverSampler

from preprocessing.dataset import MovieReviewDataset, save
from preprocessing.text_preprocessing import get_vocab, get_preprocessing_strategy
from preprocessing.tfrecord import SentenceTFRecord
from word_embedding.word_embedding import FastTextEmbedding


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def perform_undersampling(train_dataset):
    star_reviews = defaultdict(list)

    for label, review in train_dataset:
        star_reviews[label].append((label, review))

    min_dataset = min([len(value) for value in star_reviews.values()])

    undersampling_train_dataset = []

    for value in star_reviews.values():
        random.shuffle(value)
        undersampling_train_dataset.extend(value[:min_dataset])

    random.shuffle(undersampling_train_dataset)

    return undersampling_train_dataset


def perform_oversampling(train_dataset):
    X, y = [], []

    for index, (label, review) in enumerate(train_dataset):
        X.append(index)
        y.append(label)

    X = np.array(X).reshape(-1, 1)
    y = np.array(y)
    print('Original dataset shape {}'.format(Counter(y)))
    ros = RandomOverSampler(random_state=42)

    X_res, y_res = ros.fit_sample(X, y)
    print('Ooversample dataset shape {}'.format(Counter(y_res)))

    train = []
    for review, label in zip(X_res, y_res):
        movie_review = train_dataset[review[0]][1]
        train.append((label, movie_review))

    return train


def full_preprocessing(train, validation, test, user_args, save_datasets_path,
                       undersampling=False, oversampling=False):
    if not os.path.exists(save_datasets_path):
        os.makedirs(save_datasets_path)

    print('Apply data preprocessing step to datasets ...')
    train, validation, test = apply_preprocessing_to_dataset(
        train, validation, test, user_args)

    print('Creating vocabulary ...')
    train_vocab = get_vocab(train)
    print('Found vocab with size: {} ...'.format(len(train_vocab)))

    embedding_file = user_args['embedding_file']
    embed_size = user_args['embed_size']
    embedding_path = os.path.join(save_datasets_path, user_args['embedding_path'])
    embedding_wordindex_path = os.path.join(
        save_datasets_path, user_args['embedding_wordindex_path'])

    word_embedding = load_embeddings(
        train_vocab, embedding_file, embed_size, embedding_path, embedding_wordindex_path)
    word_index, matrix, embedding_vocab = word_embedding.get_word_embedding(random_unknown=False)
    print('Embedding size: {}'.format(len(matrix)))
    print('Saving embedding for tensorflow ...')
    save_embeddings_as_ckpt(matrix, save_datasets_path)

    if undersampling:
        train = perform_undersampling(train)
    if oversampling:
        train = perform_oversampling(train)

    print('Find and replacing unknown words for reviews...')
    remove = user_args['remove']
    train, validation, test = replace_unknown_words(train, validation, test, word_embedding, remove)

    print('Transforming reviews into list of ids ...')
    train, train_all, validation, validation_all, test, test_all = transform_all_datasets(
        train, validation, test, word_index)

    print('Saving datasets ...')
    save_datasets(train_all, validation_all, test_all, save_datasets_path)

    print('Train dataset len: {}'.format(len(train)))
    print('Validation dataset len: {}'.format(len(validation)))
    print('Test dataset len: {}'.format(len(test)))

    print('Transforming train reviews into tfrecords ...')
    output_path = os.path.join(save_datasets_path, 'train.tfrecord')
    create_tfrecords(train, output_path)

    print('Transforming validation reviews into tfrecords ...')
    output_path = os.path.join(save_datasets_path, 'validation.tfrecord')
    create_tfrecords(validation, output_path)

    print('Transforming test reviews into tfrecords ...')
    output_path = os.path.join(save_datasets_path, 'test.tfrecord')
    create_tfrecords(test, output_path)
    print()


def save_embeddings_as_ckpt(embeddings, save_path):
    tf_embedding = tf.Variable(embeddings, name='tf_embedding')

    save_path = os.path.join(save_path, 'embedding.ckpt')
    saver = tf.train.Saver({"tf_embedding": tf_embedding})

    with tf.Session() as sess:
        tf_embedding.initializer.run()
        print('Embedding shape: {}'.format(
            sess.run(tf.shape(tf_embedding))))
        save_path = saver.save(sess, save_path)


def create_tfrecords(reviews, output_path):
    sentence_tfrecord = SentenceTFRecord(reviews, output_path)
    sentence_tfrecord.parse_sentences()


def save_datasets(train, validation, test, save_datasets_path):
    train_save_path = os.path.join(save_datasets_path, 'train.pkl')
    save(train, train_save_path)

    validation_save_path = os.path.join(save_datasets_path, 'validation.pkl')
    save(validation, validation_save_path)

    test_save_path = os.path.join(save_datasets_path, 'test.pkl')
    save(test, test_save_path)


def sentence_to_id_list(sentence, word_index):
    return [word_index[word] for word in sentence.split()]


def transform_sentences(reviews, word_index):
    transformed_sentences = []
    all_sentences = []

    for label, review in reviews:
        review_id_list = sentence_to_id_list(review, word_index)
        size = len(review_id_list)

        transformed_sentences.append((review_id_list, label, size))
        all_sentences.append((review, review_id_list, label, size))

    return transformed_sentences, all_sentences


def transform_all_datasets(train, validation, test, word_index):
    train, train_all = transform_sentences(train, word_index)
    validation, validation_all = transform_sentences(validation, word_index)
    test, test_all = transform_sentences(test, word_index)

    return train, train_all, validation, validation_all, test, test_all


def replace_unknown_words(train, validation, test, word_embedding, remove):
    train = word_embedding.handle_unknown_words(train, None, remove)
    validation = word_embedding.handle_unknown_words(validation, None, remove)
    test = word_embedding.handle_unknown_words(test, None, remove)

    return train, validation, test


def load_embeddings(vocab, embedding_file, embed_size, embedding_path, embedding_wordindex_path):

    return FastTextEmbedding(embedding_file, embed_size, vocab, embedding_path,
                             embedding_wordindex_path)


def apply_preprocessing(reviews_array, preprocessing_strat, text_size):
    preprocessed_reviews = []
    for (label, review) in reviews_array:
        preprocessed_review = preprocessing_strat.apply_preprocessing(review, text_size)

        preprocessed_reviews.append((label, preprocessed_review))

    return preprocessed_reviews


def apply_preprocessing_to_dataset(train, validation, test, user_args):
    preprocessing_type = user_args['preprocessing_type']
    stopwords_path = user_args['stopwords_path']
    text_size = user_args['text_size']
    preprocessing_strat = get_preprocessing_strategy(preprocessing_type, stopwords_path)

    preprocessed_train = apply_preprocessing(train, preprocessing_strat, text_size)
    preprocessed_validation = apply_preprocessing(validation, preprocessing_strat, text_size)
    preprocessed_test = apply_preprocessing(test, preprocessing_strat, text_size)

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

    parser.add_argument('-r',
                        '--remove',
                        type=int,
                        help='If instead of using an unknown token to represent unknown words, we just remove them from the sentence',  # noqa
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

    parser.add_argument('-ts',
                        '--text-size',
                        type=int,
                        help='The maximum number of words a review must have')

    parser.add_argument('-sdp',
                        '--save-datasets-path',
                        type=str,
                        help='The path to save the processed dataset')

    return parser


def main():
    parser = create_argument_parser()
    user_args = vars(parser.parse_args())

    user_args['remove'] = True if user_args['remove'] == 1 else False

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

    print('Creating full processed reviews ...')
    save_datasets_path = os.path.join(user_args['save_datasets_path'], 'full')
    full_preprocessing(train, validation, test, user_args, save_datasets_path)

    print('Creating full processed reviews (with undersampling) ...')
    save_datasets_path = os.path.join(user_args['save_datasets_path'], 'full/undersampling')
    full_preprocessing(train, validation, test, user_args, save_datasets_path, undersampling=True)

    print('Creating full processed reviews (with oversampling) ...')
    save_datasets_path = os.path.join(user_args['save_datasets_path'], 'full/oversampling')
    full_preprocessing(train, validation, test, user_args, save_datasets_path, False,
                       oversampling=True)

    print('Creating Omelete preprocessed reviews')
    train = omelete_dataset.train_dataset
    validation = omelete_dataset.validation_dataset
    test = omelete_dataset.test_dataset
    save_datasets_path = os.path.join(user_args['save_datasets_path'], 'omelete')

    full_preprocessing(train, validation, test, user_args, save_datasets_path)

    print('Creating Cineclick preprocessed reviews')
    train = cineclick_dataset.train_dataset
    validation = cineclick_dataset.validation_dataset
    test = cineclick_dataset.test_dataset
    save_datasets_path = os.path.join(user_args['save_datasets_path'], 'cineclick')

    full_preprocessing(train, validation, test, user_args, save_datasets_path)

    print('Creating Cinema em Cena preprocessed reviews')
    train = cec_dataset.train_dataset
    validation = cec_dataset.validation_dataset
    test = cec_dataset.test_dataset
    save_datasets_path = os.path.join(user_args['save_datasets_path'], 'cec')

    full_preprocessing(train, validation, test, user_args, save_datasets_path)


if __name__ == '__main__':
    main()
