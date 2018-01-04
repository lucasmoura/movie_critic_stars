import argparse
import os

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


INVALID_FOLDER = -1


def create_number_of_reviews_graph(reviews_count, title, x_index, graph_folder,
                                   graph_name, graph_color):
    if not os.path.exists(graph_folder):
        os.makedirs(graph_folder)

    fig = plt.figure()

    pal = sns.color_palette(graph_color, len(reviews_count))
    rank = np.argsort(reviews_count).argsort().tolist()

    ax = sns.barplot(x=x_index, y=reviews_count, palette=np.array(pal[::-1])[rank])

    for index, row in enumerate(reviews_count):
        ax.text(index, row, str(row), color='black', ha="center")

    ax.set(xlabel='Star rating', ylabel='Number of Movies')

    fig.suptitle(title, fontsize=14, fontweight='bold')

    plt.savefig(os.path.join(graph_folder, graph_name))


def count_files_in_folder(movie_folder):
    movie_files = next(os.walk(movie_folder))[2]
    return len(movie_files)


def count_number_of_reviews(movies_folder):
    if not os.path.exists(movies_folder):
        return INVALID_FOLDER

    reviews_count = []
    for star in range(1, 6):
        star_folder = os.path.join(movies_folder, str(star))

        reviews_count.append(count_files_in_folder(star_folder))

    return reviews_count


def create_argparser():
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
    parser = create_argparser()
    user_args = vars(parser.parse_args())

    movies_folder = user_args['movies_folder']
    reviews_count = count_number_of_reviews(movies_folder)

    website_name = user_args['website_name']
    title = '{}: Number of Movies X Star Rating'.format(website_name)
    x_index = list(range(1, 6))
    graph_folder = user_args['graph_folder']
    graph_name = user_args['graph_name']
    graph_color = user_args['graph_color']
    create_number_of_reviews_graph(reviews_count, title, x_index, graph_folder, graph_name,
                                   graph_color)


if __name__ == '__main__':
    main()
