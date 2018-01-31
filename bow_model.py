import argparse
import os
import itertools

import matplotlib
matplotlib.use('Agg')  # noqa

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf

from pathlib import Path

from model.estimator import input_fn, model_fn
from preprocessing.dataset import load, save

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.logging.set_verbosity(tf.logging.ERROR)


def save_confusion_matrix(confusion_matrix, save_path):
    """ Generate a confusion matrix

        This function is based on the implementation of
        outputConfusionMatrix from q1_sentiment.py from
        Stanford's cs224n course
    """

    plt.figure()
    plt.imshow(confusion_matrix, interpolation='nearest', cmap=plt.cm.Reds)
    plt.colorbar()
    classes = ["1", "2", "3", "4", "5"]
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes)
    plt.yticks(tick_marks, classes)
    thresh = confusion_matrix.max() / 2.

    for i, j in itertools.product(
            range(confusion_matrix.shape[0]), range(confusion_matrix.shape[1])):
        plt.text(j, i, confusion_matrix[i, j],
                 horizontalalignment="center",
                 color="white" if confusion_matrix[i, j] > thresh else "black")

    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()

    plt.savefig(str(save_path))


def save_model_metrics(result, train_accuracies, validation_accuracies, save_path):
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    save_path = Path(save_path)

    confusion_matrix_path = save_path / 'test_confusion_matrix.png'
    save_confusion_matrix(result['confusion_matrix'], confusion_matrix_path)

    test_accuracy_path = save_path / 'test_accuracy.pkl'
    save(result['accuracy'], test_accuracy_path)

    train_accuracies_path = save_path / 'train_accuracies.pkl'
    save(train_accuracies, train_accuracies_path)

    validation_accuracies_path = save_path / 'validation_accuracies.pkl'
    save(validation_accuracies, validation_accuracies_path)


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
        model_fn=model_fn,
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
    test_file = user_args['test_file']
    save_path = user_args['save_path']
    batch_size = user_args['batch_size']
    bucket_width = user_args['bucket_width']
    num_buckets = user_args['num_buckets']

    train_accuracies = []
    validation_accuracies = []

    for i in range(num_epochs):
        print('Running epoch {}'.format(i+1))
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

        train_accuracies.append(train_result['accuracy'])
        validation_accuracies.append(eval_result['accuracy'])

        print_metrics_score(train_result, 'Train')
        print_metrics_score(eval_result, 'Validation')

    test_result = classifier.evaluate(
        input_fn=lambda: input_fn(
            tfrecord_file=test_file,
            batch_size=batch_size,
            perform_shuffle=True,
            bucket_width=bucket_width,
            num_buckets=num_buckets)
    )

    save_model_metrics(test_result, train_accuracies, validation_accuracies, save_path)


if __name__ == '__main__':
    main()
