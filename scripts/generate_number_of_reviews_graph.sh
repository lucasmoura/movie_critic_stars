#!/bin/bash

set -e

#usage: ./scripts/generate_number_of_reviews_graph.sh

GRAPH_FOLDER="data_analysis/graphs/number_of_reviews"

OMELETE_MOVIES_FOLDER="data/omelete/movies"
OMELETE_GRAPH_NAME="omelete_number_of_reviews.png"
OMELETE_WEBSITE="Omelete"
OMELETE_GRAPH_COLOR="Wistia_d"

echo "Generating $OMELETE_WEBSITE graph"
python data_analysis/number_of_reviews.py \
  --website-name=${OMELETE_WEBSITE} \
  --movies-folder=${OMELETE_MOVIES_FOLDER} \
  --graph-folder=${GRAPH_FOLDER} \
  --graph-name=${OMELETE_GRAPH_NAME} \
  --graph-color=${OMELETE_GRAPH_COLOR}

CINEMA_EM_CENA_MOVIES_FOLDER="data/cinema_em_cena/movies"
CINEMA_EM_CENA_GRAPH_NAME="cinema_em_cena_number_of_reviews.png"
CINEMA_EM_CENA_WEBSITE="Cinema Em Cena"
CINEMA_EM_CENA_GRAPH_COLOR="OrRd_d"

echo "Generating $CINEMA_EM_CENA_WEBSITE graph"
python data_analysis/number_of_reviews.py \
  --website-name="$CINEMA_EM_CENA_WEBSITE" \
  --movies-folder=${CINEMA_EM_CENA_MOVIES_FOLDER} \
  --graph-folder=${GRAPH_FOLDER} \
  --graph-name=${CINEMA_EM_CENA_GRAPH_NAME} \
  --graph-color=${CINEMA_EM_CENA_GRAPH_COLOR}

CINECLICK_MOVIES_FOLDER="data/cineclick/movies"
CINECLICK_GRAPH_NAME="cineclick_number_of_reviews.png"
CINECLICK_WEBSITE="Cineclick"
CINECLICK_GRAPH_COLOR="Blues_d"

echo "Generating $CINECLICK_WEBSITE graph"
python data_analysis/number_of_reviews.py \
  --website-name=${CINECLICK_WEBSITE} \
  --movies-folder=${CINECLICK_MOVIES_FOLDER} \
  --graph-folder=${GRAPH_FOLDER} \
  --graph-name=${CINECLICK_GRAPH_NAME} \
  --graph-color=${CINECLICK_GRAPH_COLOR}
