#!/bin/bash

set -e

#usage
#./script/download_cinema_em_cena_reviews.sh

START_INDEX=8400
END_INDEX=8500
BASE_URL="http://cinemaemcena.cartacapital.com.br/critica/filme/"
MOVIES_FOLDER="data/cinema_em_cena/movies/"
MOVIE_CODES_PATH="data/cinema_em_cena/movie_codes.pkl"


python cinema_em_cena.py \
    --start-index=${START_INDEX} \
    --end-index=${END_INDEX} \
    --base-url=${BASE_URL} \
    --movies-folder=${MOVIES_FOLDER} \
    --movie-codes-path=${MOVIE_CODES_PATH}
