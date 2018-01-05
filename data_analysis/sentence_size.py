import argparse
import os
import re

from scipy.stats import norm

import matplotlib.pyplot as plt
import seaborn as sns


def create_graph(sentences_size, sentence_mean, sentence_std,
                 website_name, graph_folder, graph_name, graph_color):
    if not os.path.exists(graph_folder):
        os.makedirs(graph_folder)

    sns.set_style('dark')
    sns.distplot(sentences_size, color=graph_color)

    plt.xlabel('Sentence Size')
    plt.title(
        'Histogram of {0} Sentence Sizes\n u={1:.2f}, sigma={2:.2f}'.format(
             website_name, sentence_mean, sentence_std))

    graph_path = os.path.join(graph_folder, graph_name)
    plt.savefig(graph_path)

    plt.close()


def get_review_size(sentences_dir, review_file):
    review_file = os.path.join(sentences_dir, review_file)

    with open(review_file, 'r') as rf:
        sentence = rf.read()

    words = re.findall(r'\w+', sentence)
    return len(words)


def get_all_sentences_from_folder(sentences_dir):
    sentences_size = []

    for review in os.scandir(sentences_dir):
        review_size = get_review_size(sentences_dir, review.name)
        sentences_size.append(review_size)

    return sentences_size


def perform_dataset_analysis(user_args):
    website_name = user_args['website_name']
    movies_folder = user_args['movies_folder']
    graph_folder = user_args['graph_folder']
    graph_name = user_args['graph_name']
    graph_color = user_args['graph_color']
    sentences_size = []

    for star in range(1, 6):
        star_folder = os.path.join(movies_folder, str(star))
        sentences_size.extend(get_all_sentences_from_folder(star_folder))

    mean, std = norm.fit(sentences_size)

    create_graph(
        sentences_size, mean, std, website_name, graph_folder, graph_name, graph_color)


def create_argument_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('-wm',
                        '--website-name',
                        type=str,
                        help='Name of the website to generate the graph')

    parser.add_argument('-mf',
                        '--movies-folder',
                        type=str,
                        help='Movies folder to count the number of reviews')

    parser.add_argument('-gf',
                        '--graph-folder',
                        type=str,
                        help='Folder where the graph file will be saved on')

    parser.add_argument('-gn',
                        '--graph-name',
                        type=str,
                        help='Name of the graph that will be generated')

    parser.add_argument('-gc',
                        '--graph-color',
                        type=str,
                        help='Color of the graph that will be generated')

    return parser


def main():
    parser = create_argument_parser()
    user_args = vars(parser.parse_args())

    perform_dataset_analysis(user_args)


if __name__ == '__main__':
    main()
