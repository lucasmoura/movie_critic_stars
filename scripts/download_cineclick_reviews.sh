#!/bin/bash

set -e

#usage
#./script/download_cineclick_reviews.sh

START_INDEX=1
END_INDEX=214
BASE_URL="http://www.cineclick.com.br"
REVIEWS_PAGE_URL="https://www.cineclick.com.br/criticas"
MOVIES_FOLDER="data/cineclick/movies/"
MOVIE_URLS_PATH="data/cineclick/movie_urls.pkl"
INVALID_MOVIES_LOG="data/cineclick/invalid_movies_log.txt"


python cineclick.py \
    --start-index=${START_INDEX} \
    --end-index=${END_INDEX} \
    --base-url=${BASE_URL} \
    --reviews-page-url=${REVIEWS_PAGE_URL} \
    --movies-folder=${MOVIES_FOLDER} \
    --movie-urls-path=${MOVIE_URLS_PATH} \
    --invalid-movies-log=${INVALID_MOVIES_LOG}
