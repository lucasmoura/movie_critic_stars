import argparse
import os
import pickle

from utils.folder import create_folder
from website_crawler.discover_movies import CineclickUrlFinder


def load_movie_codes(movie_urls_path):
    with open(movie_urls_path, 'rb') as codes_pkl:
        return pickle.load(codes_pkl)


def save_movie_codes(movie_urls, movie_urls_path):
    with open(movie_urls_path, 'wb') as codes_pkl:
        pickle.dump(movie_urls, codes_pkl)


def create_argument_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('-si',
                        '--start-index',
                        type=int,
                        help='The start movie index to be search on the cineclick website')

    parser.add_argument('-ei',
                        '--end-index',
                        type=int,
                        help='The end movie index to be search on the cineclick website')

    parser.add_argument('-bu',
                        '--base-url',
                        type=str,
                        help='The website main url')

    parser.add_argument('-rpu',
                        '--reviews-page-url',
                        type=str,
                        help='The url used to access the movies from the cineclick website')

    parser.add_argument('-mf',
                        '--movies-folder',
                        type=str,
                        help='The folder to save the movies into')

    parser.add_argument('-muf',
                        '--movie-urls-path',
                        type=str,
                        help='The path to save the movie urls into')

    parser.add_argument('-ivl',
                        '--invalid-movies-log',
                        type=str,
                        help='The path to save the movies url that could not be downloaded')

    return parser


def main():
    parser = create_argument_parser()
    user_args = vars(parser.parse_args())

    start_index = user_args['start_index']
    end_index = user_args['end_index']
    base_url = user_args['base_url']
    reviews_page_url = user_args['reviews_page_url']
    movies_folder = user_args['movies_folder']
    movie_urls_path = user_args['movie_urls_path']
    # invalid_movies_log = user_args['invalid_movies_log']

    create_folder(movies_folder)

    if os.path.exists(movie_urls_path):
        print('Loading movie urls from pickle file...')
        movie_urls = load_movie_codes(movie_urls_path)
    else:
        print('Generating movie codes...')
        cineclick_url_finder = CineclickUrlFinder(base_url, reviews_page_url, start_index,
                                                  end_index)
        movie_urls = cineclick_url_finder.search_for_urls()
        save_movie_codes(movie_urls, movie_urls_path)


if __name__ == '__main__':
    main()
