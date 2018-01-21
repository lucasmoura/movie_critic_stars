import unittest

from preprocessing.dataset import MovieReviewDataset


class MovieReviewDatasetTest(unittest.TestCase):

    def setUp(self):
        self.movie_dataset = MovieReviewDataset(None)

    def test_split_dataset(self):
        self.movie_dataset.txt_files = [
            [(1, [1, 2]), (1, [3, 4]), (1, [5, 6]), (1, [7, 8])],
            [(2, [1, 2]), (2, [3, 4]), (2, [5, 6]), (2, [7, 8]), (2, [9, 10]), (2, [11, 12])],
            [(3, [1, 2]), (3, [3, 4]), (3, [5, 6]), (3, [7, 8])],
            [(4, [1, 2]), (4, [3, 4]), (4, [5, 6]), (4, [7, 8]), (4, [9, 10]), (4, [11, 12])],
            [(5, [1, 2]), (5, [3, 4]), (5, [5, 6]), (5, [7, 8])]
        ]

        self.movie_dataset.split_dataset(use_formatted=False, percent=0.5)

        expected_lens = [2, 3, 2, 3, 2]
        actual_lens = [len(txt_file) for txt_file, _ in self.movie_dataset.split_files]
        self.assertEqual(expected_lens, actual_lens)

        expected_lens = [2, 3, 2, 3, 2]
        actual_lens = [len(split_file) for _, split_file in self.movie_dataset.split_files]
        self.assertEqual(expected_lens, actual_lens)

        self.movie_dataset.split_dataset(use_formatted=False, percent=0.25)

        expected_lens = [3, 5, 3, 5, 3]
        actual_lens = [len(txt_file) for txt_file, _ in self.movie_dataset.split_files]
        self.assertEqual(expected_lens, actual_lens)

        expected_lens = [1, 1, 1, 1, 1]
        actual_lens = [len(split_file) for _, split_file in self.movie_dataset.split_files]
        self.assertEqual(expected_lens, actual_lens)

    def test_get_train_dataset(self):
        self.movie_dataset.split_files = [(
            [(1, 2), (5, 6), (9, 10)], [(3, 4), (7, 8)]
        )]

        self.movie_dataset.generate_train_dataset()

        expected_train_dataset = [(1, 2), (5, 6), (9, 10)]
        self.assertEqual(expected_train_dataset, self.movie_dataset.train_dataset)

    def test_get_validation_dataset(self):
        self.movie_dataset.split_files = [(
            [(1, 2), (5, 6), (9, 10)], [(3, 4), (7, 8), (11, 12), (15, 16)]
        )]

        self.movie_dataset.generate_validation_dataset()

        expected_validation_dataset = [(3, 4), (7, 8)]
        self.assertEqual(expected_validation_dataset, self.movie_dataset.validation_dataset)

    def test_get_test_dataset(self):
        self.movie_dataset.split_files = [(
            [(1, 2), (5, 6), (9, 10)], [(3, 4), (7, 8), (11, 12), (15, 16)]
        )]

        self.movie_dataset.generate_test_dataset()

        expected_test_dataset = [(11, 12), (15, 16)]
        self.assertEqual(expected_test_dataset, self.movie_dataset.test_dataset)

    def test_remove_director_from_movie(self):
        self.movie_dataset.director_str = '<director>'

        txt_file = [
            'title',
            'director1,director2',
            [],
            'director1 and director2 are working together again',
            []
        ]

        expected_review = '<director> and <director> are working together again'
        self.assertEqual(self.movie_dataset.remove_director_from_review(txt_file),
                         expected_review)

    def test_remove_actors_from_movie(self):
        self.movie_dataset.actor_str = '<actors>'

        txt_file = [
            'title',
            [],
            'actors1,actors2',
            'actors1 and actors2 are working together again',
            []
        ]

        expected_review = '<actors> and <actors> are working together again'
        self.assertEqual(self.movie_dataset.remove_actors_from_review(txt_file),
                         expected_review)

    def test_remove_title_from_movie(self):
        self.movie_dataset.title_str = '<title>'

        txt_file = [
            'Movie1',
            [],
            [],
            'Movie1 is awesome',
            []
        ]

        expected_review = '<title> is awesome'
        self.assertEqual(self.movie_dataset.remove_title_from_review(txt_file),
                         expected_review)
