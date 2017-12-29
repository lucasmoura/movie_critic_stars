#!/bin/bash

set -e

#usage
#./script/download_from_all_websites.sh

echo "Downloading Cinema Em Cena reviews"
sh ./scripts/download_cinema_em_cena_reviews.sh

echo "Downloading Omelete reviews"
sh ./scripts/download_omelete_reviews.sh

echo "Downloading Cineclick Em Cena reviews"
sh ./scripts/download_cineclick_reviews.sh
