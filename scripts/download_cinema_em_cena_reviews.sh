#!/bin/bash

set -e

#usage
#./script/download_cinema_em_cena_reviews.sh

START_INDEX=0
END_INDEX=10000
BASE_URL="http://cinemaemcena.cartacapital.com.br/critica/filme/"
MOVIES_FOLDER="data/cinema_em_cena/movies/"
MOVIE_CODES_PATH="data/cinema_em_cena/movie_codes.pkl"
INVALID_MOVIES_LOG="data/cinema_em_cena/invalid_movies_log.txt"


python cinema_em_cena.py \
    --start-index=${START_INDEX} \
    --end-index=${END_INDEX} \
    --base-url=${BASE_URL} \
    --movies-folder=${MOVIES_FOLDER} \
    --movie-codes-path=${MOVIE_CODES_PATH} \
    --invalid-movies-log=${INVALID_MOVIES_LOG}
