import tensorflow as tf


class SentenceTFRecord():
    def __init__(self, reviews, output_path):
        self.reviews = reviews
        self.output_path = output_path

    def parse_sentences(self):
        writer = tf.python_io.TFRecordWriter(self.output_path)

        for sentence, label, size in self.reviews:
            example = self.make_example(sentence, label, size)
            writer.write(example.SerializeToString())

        writer.close()

    def make_example(self, sentence, label, size):
        example = tf.train.SequenceExample()

        example.context.feature['size'].int64_list.value.append(size)
        example.context.feature['label'].int64_list.value.append(label)

        sentence_tokens = example.feature_lists.feature_list['tokens']

        for token in sentence:
            sentence_tokens.feature.add().int64_list.value.append(int(token))

        return example
