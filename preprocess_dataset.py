import argparse

from preprocessing.text_preprocessing import get_preprocessing_strategy


def create_argument_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('-rf',
                        '--reviews-folder',
                        type=str,
                        help='The path of the reviews folder to preprocess',
                        required=True)

    parser.add_argument('-pt',
                        '--preprocessing-type',
                        type=str,
                        help='The type of preprocessing to use',
                        required=True)

    parser.add_argument('-sp',
                        '--stopwords-path',
                        type=str,
                        help='The path of the stop words file',
                        required=True)
    return parser


def main():
    parser = create_argument_parser()
    user_args = vars(parser.parse_args())

    preprocessing_type = user_args['preprocessing_type']
    stopwords_path = user_args['stopwords_path']
    preprocessing_strat = get_preprocessing_strategy(preprocessing_type, stopwords_path)

    print(preprocessing_strat)


if __name__ == '__main__':
    main()
