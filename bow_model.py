import argparse
import os

import tensorflow as tf

from model.estimator import get_estimator, run_estimator
from preprocessing.dataset import load

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.logging.set_verbosity(tf.logging.ERROR)


def get_num_words(embedding_path):
    matrix = load(embedding_path)
    return len(matrix)


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

    parser.add_argument('-emckpt',
                        '--embedding-ckpt',
                        type=str,
                        help='The path of the embedding ckpt file',
                        required=True)

    parser.add_argument('-emckptn',
                        '--embedding-ckpt-name',
                        type=str,
                        help='The name of the embedding var in the ckpt file',
                        required=True)

    parser.add_argument('-es',
                        '--embed-size',
                        type=int,
                        help='The embedding size',
                        required=True)

    parser.add_argument('-d',
                        '--dropout',
                        type=float,
                        help='The dropout rate',
                        required=True)

    parser.add_argument('-nl',
                        '--num-labels',
                        type=int,
                        help='The number of labels that a review can be classified')

    parser.add_argument('-nu',
                        '--num-units',
                        type=int,
                        help='Number of units for hidden layer')

    parser.add_argument('-wd',
                        '--weight-decay',
                        type=float,
                        help='Weight decay variable for l2 loss')

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
    ckpt_path = user_args['embedding_ckpt']
    ckpt_tensor_name = user_args['embedding_ckpt_name']
    dropout = user_args['dropout']
    num_labels = user_args['num_labels']
    num_units = user_args['num_units']
    weight_decay = user_args['weight_decay']
    lr = user_args['learning_rate']
    show_loss = False

    if show_loss:
        tf.logging.set_verbosity(tf.logging.INFO)

    model_params = {
        'num_words': get_num_words(embedding_path),
        'embed_size': embed_size,
        'ckpt_path': ckpt_path,
        'ckpt_tensor_name': ckpt_tensor_name,
        'dropout': dropout,
        'num_labels': num_labels,
        'num_units': num_units,
        'weight_decay': weight_decay,
        'lr': lr,
        'show_loss': show_loss
    }

    num_epochs = user_args['num_epochs']
    save_path = user_args['save_path']

    estimator = get_estimator('bag_of_words')
    run_estimator(estimator, model_params, pipeline_params, num_epochs, save_path)


if __name__ == '__main__':
    main()
