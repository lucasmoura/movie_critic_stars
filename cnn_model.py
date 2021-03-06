import argparse
import os

import tensorflow as tf

from model.estimator import EstimatorManager
from preprocessing.dataset import load

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.logging.set_verbosity(tf.logging.ERROR)


def get_embedding(embedding_path):
    return load(embedding_path)


def create_argument_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('-tf',
                        '--train-file',
                        type=str,
                        help='The path of the train tfrecord file',
                        required=True)

    parser.add_argument('-vf',
                        '--validation-file',
                        type=str,
                        help='The path of the validation tfrecord file',
                        required=True)

    parser.add_argument('-tsf',
                        '--test-file',
                        type=str,
                        help='The path of the test tfrecord file',
                        required=True)

    parser.add_argument('-sp',
                        '--save-path',
                        type=str,
                        help='The path to save the model results',
                        required=True)

    parser.add_argument('-em',
                        '--embedding-path',
                        type=str,
                        help='The path of the embedding file to be used',
                        required=True)

    parser.add_argument('-es',
                        '--embed-size',
                        type=int,
                        help='The embedding size',
                        required=True)

    parser.add_argument('-nl',
                        '--num-labels',
                        type=int,
                        help='The number of labels that a review can be classified')

    parser.add_argument('-nf',
                        '--num-filters',
                        type=int,
                        help='number of filters to use on the convolutional layer')

    parser.add_argument('-fs',
                        '--filters-size',
                        type=str,
                        help='A comma separated string containing the filters size to use')

    parser.add_argument('-ts',
                        '--text-size',
                        type=int,
                        help='The maximum number of words a review must have')

    parser.add_argument('-wd',
                        '--weight-decay',
                        type=float,
                        help='Weight decay variable for l2 loss')

    parser.add_argument('-emd',
                        '--embedding-dropout',
                        type=float,
                        help='Embedding dropout value')

    parser.add_argument('-dr',
                        '--dropout-rate',
                        type=float,
                        help='Dropout value')

    parser.add_argument('-lr',
                        '--learning-rate',
                        type=float,
                        help='Learning rate to be used when training the model')

    parser.add_argument('-bs',
                        '--batch-size',
                        type=int,
                        help='The batch size to be used')

    parser.add_argument('-ne',
                        '--num-epochs',
                        type=int,
                        help='The number of epochs to train the model')

    parser.add_argument('-bw',
                        '--bucket-width',
                        type=int,
                        help='The bucket width allowed')

    parser.add_argument('-nb',
                        '--num-buckets',
                        type=int,
                        help='The maximum number of buckets')
    return parser


def main():
    parser = create_argument_parser()
    user_args = vars(parser.parse_args())

    train_file = user_args['train_file']
    validation_file = user_args['validation_file']
    test_file = user_args['test_file']
    batch_size = user_args['batch_size']
    bucket_width = user_args['bucket_width']
    num_buckets = user_args['num_buckets']

    pipeline_params = {
        'train_file': train_file,
        'validation_file': validation_file,
        'test_file': test_file,
        'batch_size': batch_size,
        'bucket_width': bucket_width,
        'num_buckets': num_buckets
    }

    embed_size = user_args['embed_size']
    embedding_path = user_args['embedding_path']
    num_labels = user_args['num_labels']
    num_filters = user_args['num_filters']

    filters_size = user_args['filters_size']
    filters_size = [int(value) for value in filters_size.split(',')]

    text_size = user_args['text_size']
    weight_decay = user_args['weight_decay']
    embedding_dropout = user_args['embedding_dropout']
    dropout_rate = user_args['dropout_rate']
    lr = user_args['learning_rate']
    show_loss = False

    if show_loss:
        tf.logging.set_verbosity(tf.logging.INFO)

    matrix = get_embedding(embedding_path)
    model_params = {
        'embedding': matrix,
        'embed_size': embed_size,
        'vocab_size': len(matrix),
        'num_labels': num_labels,
        'num_filters': num_filters,
        'text_size': text_size,
        'filters_size': filters_size,
        'weight_decay': weight_decay,
        'embedding_dropout': embedding_dropout,
        'dropout_rate': dropout_rate,
        'lr': lr,
        'show_loss': show_loss
    }

    num_epochs = user_args['num_epochs']
    save_path = user_args['save_path']

    estimator_manager = EstimatorManager(
        estimator_name='cnn',
        model_params=model_params,
        pipeline_params=pipeline_params,
        num_epochs=num_epochs,
        save_path=save_path)

    estimator_manager.run_estimator()


if __name__ == '__main__':
    main()
