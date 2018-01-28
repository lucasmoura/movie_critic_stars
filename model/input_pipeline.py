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

    def create_bucket_dataset(self, movie_dataset):
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

        movie_dataset = movie_dataset.apply(
            tf.contrib.data.group_by_window(
                key_func=key_func, reduce_func=reduce_func, window_size=self.batch_size))

        return movie_dataset

    def create_dataset(self):
        movie_dataset = tf.data.TFRecordDataset(self.data_file).map(self.parser)

        if self.perform_shuffle:
            movie_dataset = movie_dataset.shuffle(buffer_size=self.batch_size * 2)

        self.movie_dataset = self.create_bucket_dataset(movie_dataset)

        return self.movie_dataset
