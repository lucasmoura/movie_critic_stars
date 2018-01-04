import argparse
import os

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from number_of_reviews import count_number_of_reviews


INVALID_FOLDER = -1


def create_number_of_reviews_graph(reviews_count, x_index, graph_folder, graph_name):
    if not os.path.exists(graph_folder):
        os.makedirs(graph_folder)

    fig = plt.figure()

    pal = sns.color_palette("Greens_d", len(reviews_count))
    rank = np.argsort(reviews_count).argsort().tolist()

    ax = sns.barplot(x=x_index, y=reviews_count, palette=np.array(pal[::-1])[rank])

    for index, row in enumerate(reviews_count):
        ax.text(index, row, str(row), color='black', ha="center")

    title = 'Number of Movies per Website\nTotal Number of Movies: {}'.format(
        sum(reviews_count))
    fig.suptitle(title, fontsize=14, fontweight='bold')

    plt.savefig(os.path.join(graph_folder, graph_name))


def create_argparser():
    parser = argparse.ArgumentParser()

    parser.add_argument('-of',
                        '--omelete-folder',
                        type=str,
                        help='Omelete folder to count the number of reviews')

    parser.add_argument('-ow',
                        '--omelete-website',
                        type=str,
                        help='Name of the Omelete Website to be used in the graph')

    parser.add_argument('-cecf',
                        '--cec-folder',
                        type=str,
                        help='Cinema Em Cena folder to count the number of reviews')

    parser.add_argument('-cecw',
                        '--cec-website',
                        type=str,
                        help='Name of the Cinema Em Cena Website to be used in the graph')

    parser.add_argument('-cf',
                        '--cineclick-folder',
                        type=str,
                        help='Cineclick folder to count the number of reviews')

    parser.add_argument('-cw',
                        '--cineclick-website',
                        type=str,
                        help='Name of the Cineclick Website to be used in the graph')

    parser.add_argument('-gf',
                        '--graph-folder',
                        type=str,
                        help='Folder where the graph file will be saved on')

    parser.add_argument('-gn',
                        '--graph-name',
                        type=str,
                        help='Name of the graph that will be generated')

    return parser


def main():
    parser = create_argparser()
    user_args = vars(parser.parse_args())

    omelete_folder = user_args['omelete_folder']
    omelete_reviews_count = sum(count_number_of_reviews(omelete_folder))

    cec_folder = user_args['cec_folder']
    cec_reviews_count = sum(count_number_of_reviews(cec_folder))

    cineclick_folder = user_args['cineclick_folder']
    cineclick_reviews_count = sum(count_number_of_reviews(cineclick_folder))

    omelete_website = user_args['omelete_website']
    cec_website = user_args['cec_website']
    cineclick_website = user_args['cineclick_website']

    x_index = [omelete_website, cec_website, cineclick_website]

    graph_folder = user_args['graph_folder']
    graph_name = user_args['graph_name']
    reviews_count = [omelete_reviews_count, cec_reviews_count,
                     cineclick_reviews_count]
    create_number_of_reviews_graph(reviews_count, x_index, graph_folder, graph_name)


if __name__ == '__main__':
    main()
