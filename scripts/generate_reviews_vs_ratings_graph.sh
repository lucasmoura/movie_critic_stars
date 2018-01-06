#!/bin/bash

set -e

#usage: ./scripts/generate_reviews_vs_ratings_graph.sh

GRAPH_FOLDER="data_analysis/graphs/reviews_vs_ratings/"
GRAPH_NAME="reviews_vs_ratings.png"
GRAPH_COLOR="YlGn_d"
X_LABEL="Star ratings"
Y_LABEL=""

OMELETE_MOVIES_FOLDER="data/omelete/movies"
CINEMA_EM_CENA_MOVIES_FOLDER="data/cinema_em_cena/movies"
CINECLICK_MOVIES_FOLDER="data/cineclick/movies"

echo "Generating Reviews vs Ratings graph"
python data_analysis/number_of_rating_vs_movies.py \
  --omelete-folder=${OMELETE_MOVIES_FOLDER} \
  --cec-folder=${CINEMA_EM_CENA_MOVIES_FOLDER} \
  --cineclick-folder=${CINECLICK_MOVIES_FOLDER} \
  --graph-folder=${GRAPH_FOLDER} \
  --graph-name=${GRAPH_NAME} \
  --graph-color=${GRAPH_COLOR} \
  --x-label="$X_LABEL" \
  --y-label=${Y_LABEL}

