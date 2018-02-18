import re
import unicodedata

from tensorflow.contrib import learn

from word_embedding.word_embedding import UNK_TOKEN


def get_preprocessing_strategy(preprocessing_type, stopwords_path):

    if preprocessing_type == 'bag_of_words':
        return BagOfWordsPreprocessing(stopwords_path)
    elif preprocessing_type == 'rnn':
        return BagOfWordsPreprocessing(None)
    elif preprocessing_type == 'cnn':
        return BagOfWordsPreprocessing(None)


def get_vocab(reviews_array):
    def tokenizer_fn(iterator):
        return (x.split(' ') for x in iterator)

    reviews_array = [review for _, review in reviews_array]
    max_size = max([len(review) for review in reviews_array])

    vocabulary_processor = learn.preprocessing.VocabularyProcessor(
        max_size, tokenizer_fn=tokenizer_fn, min_frequency=10)

    vocabulary_processor.fit(reviews_array)

    vocab = vocabulary_processor.vocabulary_._mapping
    sorted_vocab = sorted(vocab.items(), key=lambda x: x[1])

    return sorted_vocab


class TextPreprocessing:

    def __init__(self, stopwords_path=None):
        self.stopwords_path = stopwords_path
        self.stopwords = None

        if self.stopwords_path:
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

    def reduce_text(self, text, text_size):
        splitted_text = text.split()
        splitted_text_size = len(splitted_text)

        if splitted_text_size >= text_size:
            splitted_text = splitted_text[:text_size]
        else:
            splitted_text.extend(
                [UNK_TOKEN for _ in range(text_size - splitted_text_size)])

        assert len(splitted_text) == text_size

        return ' '.join(splitted_text)

    def apply_preprocessing(self, text, text_size=10):

        formatted_text = self.add_space_between_characters(text)
        formatted_text = self.remove_special_characters_from_text(formatted_text)
        formatted_text = self.remove_extra_spaces(formatted_text)
        formatted_text = self.to_lower(formatted_text)

        if text_size:
            formatted_text = self.reduce_text(formatted_text, text_size)

        return self.remove_stopwords(formatted_text) if self.stopwords else formatted_text


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

    def apply_preprocessing(self, text, text_size):
        formatted_text = self.remove_accented_characters(text)
        formatted_text = self.remove_html_from_text(formatted_text)
        return super().apply_preprocessing(formatted_text, text_size)
