import os

from pathlib import Path

from preprocessing.dataset import save
from utils.graphs import save_confusion_matrix, accuracy_graph


def save_model_metrics(result, train_accuracies, validation_accuracies, save_path):
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    save_path = Path(save_path)

    confusion_matrix_graph_path = save_path / 'test_confusion_matrix.png'
    save_confusion_matrix(result['confusion_matrix'], str(confusion_matrix_graph_path))

    confusion_matrix_pickle_path = save_path / 'test_confusion_matrix.pkl'
    save(result['confusion_matrix'], confusion_matrix_pickle_path)

    test_accuracy_path = save_path / 'test_accuracy.pkl'
    save(result['accuracy'], test_accuracy_path)

    train_accuracies_path = save_path / 'train_accuracies.pkl'
    save(train_accuracies, train_accuracies_path)

    validation_accuracies_path = save_path / 'validation_accuracies.pkl'
    save(validation_accuracies, validation_accuracies_path)

    accuracies_graph_path = save_path / 'accuracies.png'
    accuracy_graph(train_accuracies, validation_accuracies, str(accuracies_graph_path))


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
