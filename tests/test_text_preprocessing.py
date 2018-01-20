import unittest

from preprocessing.text_preprocessing import TextPreprocessing, BagOfWordsPreprocessing


class TextPreprocessingTest(unittest.TestCase):

    def setUp(self):
        self.text_preprocessing = TextPreprocessing()

    def test_add_space_between_characters(self):
        test_string = 'Test,test'
        expected_string = 'Test , test'

        self.assertEqual(self.text_preprocessing.add_space_between_characters(test_string),
                         expected_string)

        test_string = 'Test!test'
        expected_string = 'Test ! test'

        self.assertEqual(self.text_preprocessing.add_space_between_characters(test_string),
                         expected_string)

        test_string = 'Test?test'
        expected_string = 'Test ? test'

        self.assertEqual(self.text_preprocessing.add_space_between_characters(test_string),
                         expected_string)

        test_string = 'Test(test'
        expected_string = 'Test ( test'

        self.assertEqual(self.text_preprocessing.add_space_between_characters(test_string),
                         expected_string)

        test_string = 'Test)test'
        expected_string = 'Test ) test'

        self.assertEqual(self.text_preprocessing.add_space_between_characters(test_string),
                         expected_string)

        test_string = 'Test;test'
        expected_string = 'Test ; test'

        self.assertEqual(self.text_preprocessing.add_space_between_characters(test_string),
                         expected_string)

        test_string = 'Test:test'
        expected_string = 'Test : test'

        self.assertEqual(self.text_preprocessing.add_space_between_characters(test_string),
                         expected_string)

        test_string = 'Test.test'
        expected_string = 'Test . test'

        self.assertEqual(self.text_preprocessing.add_space_between_characters(test_string),
                         expected_string)

    def test_remove_special_characters_from_text(self):
        test_string = '# Test 123'
        expected_string = '  Test 123'

        self.assertEqual(self.text_preprocessing.remove_special_characters_from_text(test_string),
                         expected_string)

    def test_remove_extra_spaces(self):
        test_string = '     Test  '
        expected_string = ' Test '

        self.assertEqual(self.text_preprocessing.remove_extra_spaces(test_string),
                         expected_string)


class BagOfWordsPreprocessingTest(unittest.TestCase):

    def setUp(self):
        self.bow_preprocessing = BagOfWordsPreprocessing('tests/files/stopwords.txt')

    def test_remove_stop_words(self):
        test_string = 'a b c d'
        expected_string = 'd'

        self.assertEqual(self.bow_preprocessing.remove_stopwords(test_string),
                         expected_string)

    def test_remove_special_characters_from_text(self):
        test_string = '# (Test) 123'
        expected_string = '   Test     '

        self.assertEqual(self.bow_preprocessing.remove_special_characters_from_text(test_string),
                         expected_string)

    def test_remove_html_from_text(self):
        test_string = '<br /><br />Test<br /><br />'
        expected_string = ' Test '

        self.assertEqual(self.bow_preprocessing.remove_html_from_text(test_string),
                         expected_string)

    def test_remove_accented_characters(self):
        test_string = 'áãóéì'
        expected_string = 'aaoei'

        self.assertEqual(self.bow_preprocessing.remove_accented_characters(test_string),
                         expected_string)
