import re
import unicodedata

from tensorflow.contrib import learn


def get_preprocessing_strategy(preprocessing_type, stopwords_path):

    if preprocessing_type == 'bag_of_words':
        return BagOfWordsPreprocessing(stopwords_path)


def get_maximum_size_review(reviews_array):
    max_size = -1

    for _, review in reviews_array:
        review = review.split()
        if len(review) > max_size:
            max_size = len(review)

    return max_size


def get_vocab(reviews_array):
    max_size = get_maximum_size_review(reviews_array)

    vocabulary_processor = learn.preprocessing.VocabularyProcessor(max_size)
    reviews_array = [review for _, review in reviews_array]
    vocabulary_processor.fit(reviews_array)

    vocab = vocabulary_processor.vocabulary_._mapping
    sorted_vocab = sorted(vocab.items(), key=lambda x: x[1])

    return sorted_vocab


class TextPreprocessing:

    def __init__(self, stopwords_path=None):
        self.stopwords_path = stopwords_path
        self.stopwords = None

        self.load_stopwords()

    def load_stopwords(self):
        if not self.stopwords and self.stopwords_path:
            with open(self.stopwords_path, 'r') as stopwords_file:
                stopwords_file.readline()  # First line is a comment

                self.stopwords = self.parse_stopwords(stopwords_file.read())

    def remove_stopwords(self, text):
        return ' '.join(filter(lambda x: x not in self.stopwords,  text.split()))

    def add_space_between_characters(self, text):
        text = re.sub(r",", " , ", text)
        text = re.sub(r"!", " ! ", text)
        text = re.sub(r"\(", " ( ", text)
        text = re.sub(r"\)", " ) ", text)
        text = re.sub(r";", " ; ", text)
        text = re.sub(r":", " : ", text)
        text = re.sub(r"\.", " . ", text)
        return re.sub(r"\?", " ? ", text)

    def remove_special_characters_from_text(self, text):
        return re.sub(r"[^A-Za-z0-9(),!?\']", ' ', text)

    def remove_extra_spaces(self, text):
        return re.sub(r'\s{2,}', ' ', text)

    def to_lower(self, review_text):
        return review_text.lower()

    def apply_preprocessing(self, text):
        formatted_text = self.add_space_between_characters(text)
        formatted_text = self.remove_special_characters_from_text(formatted_text)
        formatted_text = self.remove_extra_spaces(formatted_text)
        formatted_text = self.to_lower(formatted_text)
        return self.remove_stopwords(formatted_text)


class BagOfWordsPreprocessing(TextPreprocessing):

    def __init__(self, stopwords_path):
        super().__init__(stopwords_path)

    def parse_stopwords(self, stopwords):
        stopwords = stopwords.split()
        stopwords = [self.remove_accented_characters(word) for word in stopwords]
        return stopwords

    def remove_accented_characters(self, text):
        text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore')
        return text.decode('ascii')

    def remove_special_characters_from_text(self, text):
        return re.sub(r"[^A-Za-z!?\']", ' ', text)

    def remove_html_from_text(self, text):
        return re.sub(r'<br\s/><br\s/>', ' ', text)

    def apply_preprocessing(self, text):
        formatted_text = self.remove_accented_characters(text)
        formatted_text = self.remove_html_from_text(formatted_text)
        return super().apply_preprocessing(formatted_text)
