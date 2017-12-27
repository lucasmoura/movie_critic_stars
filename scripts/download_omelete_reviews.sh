#!/bin/bash

set -e

#usage
#./script/download_omelete_reviews.sh

START_INDEX=1
END_INDEX=220
BASE_URL="http://omelete.uol.com.br"
REVIEWS_PAGE_URL="http://omelete.uol.com.br/filmes/critica/"
MOVIES_FOLDER="data/omelete/movies/"
MOVIE_URLS_PATH="data/omelete/movie_urls.pkl"
INVALID_MOVIES_LOG="data/omelete/invalid_movies_log.txt"


python omelete.py \
    --start-index=${START_INDEX} \
    --end-index=${END_INDEX} \
    --base-url=${BASE_URL} \
    --reviews-page-url=${REVIEWS_PAGE_URL} \
    --movies-folder=${MOVIES_FOLDER} \
    --movie-urls-path=${MOVIE_URLS_PATH} \
    --invalid-movies-log=${INVALID_MOVIES_LOG}
