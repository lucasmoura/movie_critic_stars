import argparse
import os

import seaborn as sns
import matplotlib.pyplot as plt


INVALID_FOLDER = -1


def create_number_of_reviews_graph(website_name, reviews_count, graph_folder, graph_name):
    if not os.path.exists(graph_folder):
        os.makedirs(graph_folder)

    x = list(range(1, 6))
    ax = sns.barplot(x=x, y=reviews_count)
    ax.set(xlabel='Star rating', ylabel='Number of Movies',
           title='{}: Number of Movies X Star Rating'.format(website_name))
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

    return parser


def main():
    parser = create_argparser()
    user_args = vars(parser.parse_args())

    movies_folder = user_args['movies_folder']
    reviews_count = count_number_of_reviews(movies_folder)

    website_name = user_args['website_name']
    graph_folder = user_args['graph_folder']
    graph_name = user_args['graph_name']
    create_number_of_reviews_graph(website_name, reviews_count, graph_folder, graph_name)


if __name__ == '__main__':
    main()
