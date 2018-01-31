import itertools
import matplotlib
matplotlib.use('Agg')  # noqa


import matplotlib.pyplot as plt
import numpy as np


def accuracy_graph(train_accuracies, validation_accuracies, save_path):
    plt.gcf().clear()

    line1, = plt.plot(train_accuracies, label='Train')
    line2, = plt.plot(validation_accuracies, label='Validation')

    plt.ylabel('Accuracy')
    plt.xlabel('Epochs')
    plt.title('Train vs Validation accuracy')
    plt.legend(handles=[line1, line2], loc='lower right')
    plt.tight_layout()

    plt.savefig(save_path)


def save_confusion_matrix(confusion_matrix, save_path):
    """ Generate a confusion matrix

        This function is based on the implementation of
        outputConfusionMatrix from q1_sentiment.py from
        Stanford's cs224n course
    """

    plt.gcf().clear()
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

    plt.savefig(save_path)
