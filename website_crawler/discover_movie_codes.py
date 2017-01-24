import requests

"""
    This script will be used to search for on the cinema em cena website
    for the valid code associated with movie reviews. This script will try
    by default the codes between 5000 and 9000.

    Basically, it will compose an url with a code and try to request the page
    to see if it actually exists.

    All the valid codes are going to be stored inside into an txt file.
"""

BASE_URL = 'http://www.cinemaemcena.com.br/Critica/Filme/{}'
VALID_CODES_FILE_PATH = 'movie_codes.txt'


def search_for_valid_movie_codes():
    start_code = 5000
    final_code = 9000

    valid_movie_codes = []

    for code in range(start_code, final_code+1):
        print('Testing code {} ...'.format(code))
        response = requests.get(BASE_URL.format(code))
        website_url = response.url

        if response.status_code == 200 and not website_url.endswith('Index'):
            valid_movie_codes.append(code)

    return valid_movie_codes


def write_valid_codes_file(valid_movie_codes):
    with open(VALID_CODES_FILE_PATH, 'w') as movie_codes_file:
        for code in valid_movie_codes:
            if code != valid_movie_codes[-1]:
                movie_codes_file.write(str(code) + '\n')
            else:
                movie_codes_file.write(str(code))


def main():
    valid_movie_codes = search_for_valid_movie_codes()
    write_valid_codes_file(valid_movie_codes)


if __name__ == '__main__':
    main()
