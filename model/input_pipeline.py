import tensorflow as tf


class MovieReviewDataset:

    def __init__(self, data_file, batch_size, perform_shuffle, bucket_width, num_buckets):
        self.data_file = data_file
        self.batch_size = batch_size
        self.perform_shuffle = perform_shuffle
        self.bucket_width = bucket_width
        self.num_buckets = num_buckets

    def parser(self, tfrecord):
        feature_names = ['words', 'size']
        context_features = {
            'size': tf.FixedLenFeature([], dtype=tf.int64),
            'label': tf.FixedLenFeature([], dtype=tf.int64)
        }
        sequence_features = {
            'tokens': tf.FixedLenSequenceFeature([], dtype=tf.int64)
        }

        tfrecord_parsed = tf.parse_single_sequence_example(
            tfrecord, context_features, sequence_features)

        tokens = tfrecord_parsed[1]['tokens']
        label = tfrecord_parsed[0]['label']
        size = tfrecord_parsed[0]['size']

        return dict(zip(feature_names, [tokens, size])), label

    def create_dataset(self):
        sentiment_dataset = tf.data.TFRecordDataset(self.data_file).map(self.parser)

        if self.perform_shuffle:
            sentiment_dataset = sentiment_dataset.shuffle(buffer_size=self.batch_size * 2)

        def batching_func(dataset):
            return dataset.padded_batch(
                    self.batch_size,
                    padded_shapes=(
                        {
                            'words': tf.TensorShape([None]),
                            'size': tf.TensorShape([])
                        },
                        tf.TensorShape([]))  # size
                    )

        def key_func(features, label):
            size = features['size']
            bucket_id = size // self.bucket_width

            return tf.to_int64(tf.minimum(bucket_id, self.num_buckets))

        def reduce_func(bucket_key, widowed_data):
            return batching_func(widowed_data)

        self.sentiment_dataset = sentiment_dataset.apply(
            tf.contrib.data.group_by_window(
                key_func=key_func, reduce_func=reduce_func, window_size=self.batch_size))

        return self.sentiment_dataset


class InputPipeline:

    def __init__(self, train_files, validation_files, test_files, batch_size, perform_shuffle,
                 bucket_width, num_buckets):
        self.train_files = train_files
        self.validation_files = validation_files
        self.test_files = test_files
        self.batch_size = batch_size
        self.perform_shuffle = perform_shuffle
        self.bucket_width = bucket_width
        self.num_buckets = num_buckets

        self._train_iterator_op = None
        self._validation_iterator_op = None
        self._test_iterator_op = None

    @property
    def train_iterator(self):
        return self._train_iterator_op

    @property
    def validation_iterator(self):
        return self._validation_iterator_op

    @property
    def test_iterator(self):
        return self._test_iterator_op

    def create_datasets(self):
        train_dataset = MovieReviewDataset(
            self.train_files, self.batch_size, self.perform_shuffle,
            self.bucket_width, self.num_buckets)
        validation_dataset = MovieReviewDataset(
            self.validation_files, self.batch_size, self.perform_shuffle,
            self.bucket_width, self.num_buckets)
        test_dataset = MovieReviewDataset(
            self.test_files, self.batch_size, self.perform_shuffle,
            self.bucket_width, self.num_buckets)

        self.train_dataset = train_dataset.create_dataset()
        self.validation_dataset = validation_dataset.create_dataset()
        self.test_dataset = test_dataset.create_dataset()

    def create_iterator(self):
        self._iterator = tf.data.Iterator.from_structure(
            self.train_dataset.output_types, self.train_dataset.output_shapes)

        self._train_iterator_op = self._iterator.make_initializer(self.train_dataset)
        self._validation_iterator_op = self._iterator.make_initializer(self.validation_dataset)
        self._test_iterator_op = self._iterator.make_initializer(self.test_dataset)

    def make_batch(self):
        tokens_batch, labels_batch, size_batch = self._iterator.get_next()

        return tokens_batch, labels_batch, size_batch

    def get_num_batches(self, iterator):
        with tf.Session() as sess:
            num_batches = 0
            sess.run(iterator)

            while True:
                try:
                    _, _, _ = sess.run(self.make_batch())
                    num_batches += 1
                except tf.errors.OutOfRangeError:
                    break

        return num_batches

    def get_datasets_num_batches(self):
        self.train_batches = self.get_num_batches(self.train_iterator)
        self.validation_batches = self.get_num_batches(self.validation_iterator)
        self.test_batches = self.get_num_batches(self.test_iterator)

    def build_pipeline(self):
        self.create_datasets()
        self.create_iterator()
