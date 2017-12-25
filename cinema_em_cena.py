import argparse
import os
import pickle

from utils.folder import create_folder
from website_crawler.discover_movies import search_for_valid_movie_codes
from website_crawler.movie_reviews_downloader import get_all_movie_reviews


def load_movie_codes(movie_codes_path):
    with open(movie_codes_path, 'rb') as codes_pkl:
        return pickle.load(codes_pkl)


def save_movie_codes(movie_codes, movie_codes_path):
    with open(movie_codes_path, 'wb') as codes_pkl:
        pickle.dump(movie_codes, codes_pkl)


def create_argument_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('-si',
                        '--start-index',
                        type=int,
                        help='The start movie index to be search on the cinema em cena website')

    parser.add_argument('-ei',
                        '--end-index',
                        type=int,
                        help='The end movie index to be search on the cinema em cena website')

    parser.add_argument('-bu',
                        '--base-url',
                        type=str,
                        help='The url used to download the movies from the cinema em cena website')

    parser.add_argument('-mf',
                        '--movies-folder',
                        type=str,
                        help='The folder to save the movies into')

    parser.add_argument('-mcf',
                        '--movie-codes-path',
                        type=str,
                        help='The path to save the movie codes into')

    return parser


def main():
    parser = create_argument_parser()
    user_args = vars(parser.parse_args())

    start_index = user_args['start_index']
    end_index = user_args['end_index']
    base_url = user_args['base_url']
    movies_folder = user_args['movies_folder']
    movie_codes_path = user_args['movie_codes_path']

    create_folder(movies_folder)

    if os.path.exists(movie_codes_path):
        print('Loading movie codes from pickle file...')
        movie_codes = load_movie_codes(movie_codes_path)
    else:
        print('Generating movie codes...')
        movie_codes = search_for_valid_movie_codes(base_url, start_index, end_index)
        save_movie_codes(movie_codes, movie_codes_path)

    get_all_movie_reviews(movie_codes, base_url, movies_folder)


if __name__ == '__main__':
    main()
