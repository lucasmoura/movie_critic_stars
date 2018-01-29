import argparse
import os

import tensorflow as tf

from model.estimator import input_fn, bag_of_words_model
from preprocessing.dataset import load

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.logging.set_verbosity(tf.logging.ERROR)


def get_num_words(embedding_path):
    matrix = load(embedding_path)
    return len(matrix)


def precision(confusion_matrix, row, num_columns):
    tp = confusion_matrix[row][row]

    if tp == 0:
        return 0

    tp_fp = sum([confusion_matrix[j][row] for j in range(num_columns)])

    return tp / tp_fp


def recall(confusion_matrix, row, num_columns):
    tp = confusion_matrix[row][row]

    if tp == 0:
        return 0

    tp_fn = sum([confusion_matrix[row][j] for j in range(num_columns)])

    return tp / tp_fn


def f1(p, r):
    if p == 0 and r == 0:
        return 0

    return (2 * (p * r)) / (p + r)


def print_metrics_score(result, name):

    confusion_matrix = result['confusion_matrix']
    accuracy = result['accuracy']

    num_labels = num_columns = confusion_matrix.shape[1]

    print('{0} set accuracy: {1:.3f}'.format(name, accuracy))

    for i in range(num_labels):
        p = precision(confusion_matrix, i, num_columns)
        r = recall(confusion_matrix, i, num_columns)
        f1_score = f1(p, r)

        print(
            '{0} set metrics for {1} label: precision {2:.3f}, recall: {3:.3f}, f1: {4:.3f}'.format(
                name, (i+1), p, r, f1_score))

    print()


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

    num_epochs = user_args['num_epochs']
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

    classifier = tf.estimator.Estimator(
        model_fn=bag_of_words_model,
        params={
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
    )

    train_file = user_args['train_file']
    validation_file = user_args['validation_file']
    batch_size = user_args['batch_size']
    bucket_width = user_args['bucket_width']
    num_buckets = user_args['num_buckets']

    for i in range(num_epochs):
        print('Running on epoch {}'.format(i+1))
        classifier.train(
            input_fn=lambda: input_fn(
                tfrecord_file=train_file,
                batch_size=batch_size,
                perform_shuffle=True,
                bucket_width=bucket_width,
                num_buckets=num_buckets))

        train_result = classifier.evaluate(
            input_fn=lambda: input_fn(
                tfrecord_file=train_file,
                batch_size=batch_size,
                perform_shuffle=True,
                bucket_width=bucket_width,
                num_buckets=num_buckets),
        )

        eval_result = classifier.evaluate(
            input_fn=lambda: input_fn(
                tfrecord_file=validation_file,
                batch_size=batch_size,
                perform_shuffle=True,
                bucket_width=bucket_width,
                num_buckets=num_buckets)
        )

        print_metrics_score(train_result, 'Train')
        print_metrics_score(eval_result, 'Validation')

    print(eval_result['confusion_matrix'])


if __name__ == '__main__':
    main()