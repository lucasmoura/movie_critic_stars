#!/bin/bash

set -e

#usage: ./scripts/generate_number_of_reviews_graph.sh

GRAPH_FOLDER="data_analysis/graphs/total_number_of_reviews"
GRAPH_NAME="total_number_of_reviews.png"
GRAPH_COLOR="Greens_d"
X_LABEL=""
Y_LABEL=""

OMELETE_MOVIES_FOLDER="data/omelete/movies"
OMELETE_WEBSITE="Omelete"
CINEMA_EM_CENA_MOVIES_FOLDER="data/cinema_em_cena/movies"
CINEMA_EM_CENA_WEBSITE="Cinema Em Cena"
CINECLICK_MOVIES_FOLDER="data/cineclick/movies"
CINECLICK_WEBSITE="Cineclick"

echo "Generating Total Number of Reviews graph"
python data_analysis/total_number_of_reviews.py \
  --omelete-folder=${OMELETE_MOVIES_FOLDER} \
  --omelete-website=${OMELETE_WEBSITE} \
  --cec-folder=${CINEMA_EM_CENA_MOVIES_FOLDER} \
  --cec-website="$CINEMA_EM_CENA_WEBSITE" \
  --cineclick-folder=${CINECLICK_MOVIES_FOLDER} \
  --cineclick-website=${CINECLICK_WEBSITE} \
  --graph-folder=${GRAPH_FOLDER} \
  --graph-name=${GRAPH_NAME} \
  --graph-color=${GRAPH_COLOR} \
  --x-label=${X_LABEL} \
  --y-label=${Y_LABEL}

