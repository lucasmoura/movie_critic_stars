import argparse
from number_of_reviews import count_number_of_reviews, create_number_of_reviews_graph


def create_argparser():
    parser = argparse.ArgumentParser()

    parser.add_argument('-of',
                        '--omelete-folder',
                        type=str,
                        help='Omelete folder to count the number of reviews')

    parser.add_argument('-cecf',
                        '--cec-folder',
                        type=str,
                        help='Cinema Em Cena folder to count the number of reviews')

    parser.add_argument('-cf',
                        '--cineclick-folder',
                        type=str,
                        help='Cineclick folder to count the number of reviews')

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

    parser.add_argument('-xl',
                        '--x-label',
                        type=str,
                        help='Label for X axis')

    parser.add_argument('-yl',
                        '--y-label',
                        type=str,
                        help='Label for Y axis')

    return parser


def main():
    parser = create_argparser()
    user_args = vars(parser.parse_args())

    omelete_folder = user_args['omelete_folder']
    omelete_reviews_count = count_number_of_reviews(omelete_folder)

    cec_folder = user_args['cec_folder']
    cec_reviews_count = count_number_of_reviews(cec_folder)

    cineclick_folder = user_args['cineclick_folder']
    cineclick_reviews_count = count_number_of_reviews(cineclick_folder)

    graph_folder = user_args['graph_folder']
    graph_name = user_args['graph_name']
    graph_color = user_args['graph_color']
    x_label = user_args['x_label']
    y_label = user_args['y_label']
    reviews_count = [omelete_reviews_count, cec_reviews_count,
                     cineclick_reviews_count]
    reviews_count = [sum(x) for x in zip(*reviews_count)]
    title = 'Number of Movies vs Ratings'
    x_index = list(range(1, 6))

    create_number_of_reviews_graph(reviews_count, title, x_index, graph_folder, graph_name,
                                   graph_color, x_label, y_label)


if __name__ == '__main__':
    main()
