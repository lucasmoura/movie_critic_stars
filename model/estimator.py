import tensorflow as tf

from model.input_pipeline import MovieReviewDataset


def input_fn(tfrecord_file, batch_size, perform_shuffle, bucket_width, num_buckets):
    movie_dataset = MovieReviewDataset(
        data_file=tfrecord_file,
        batch_size=batch_size,
        perform_shuffle=perform_shuffle,
        bucket_width=bucket_width,
        num_buckets=num_buckets)
    dataset = movie_dataset.create_dataset()

    iterator = dataset.make_one_shot_iterator()
    batch_features, batch_labels = iterator.get_next()

    return batch_features, batch_labels


def estimator_spec_for_softmax_classification(logits, labels, mode, params):

    """Returns EstimatorSpec instance for softmax classification."""
    predicted_classes = tf.argmax(logits, 1)

    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(
            mode=mode,
            predictions={
                'class': predicted_classes,
                'prob': tf.nn.softmax(logits),
                'logits': logits
            })

    loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)

    if mode == tf.estimator.ModeKeys.TRAIN:
        optimizer = tf.train.AdamOptimizer(learning_rate=params['lr'])
        train_op = optimizer.minimize(loss, global_step=tf.train.get_global_step())

        return tf.estimator.EstimatorSpec(mode, loss=loss, train_op=train_op)

    eval_metric_ops = {
        'accuracy': tf.metrics.accuracy(
            labels=labels, predictions=predicted_classes)
    }

    return tf.estimator.EstimatorSpec(
        mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)


def bag_of_words_model(features, labels, mode, params):
    labels = labels - 1
    bow_column = tf.feature_column.categorical_column_with_identity(
        key='words',
        num_buckets=params['num_words'])

    bow_embedding = tf.feature_column.embedding_column(
        bow_column,
        dimension=params['embed_size'],
        combiner='mean',
        ckpt_to_load_from=params['ckpt_path'],
        tensor_name_in_ckpt=params['ckpt_tensor_name'])

    bow = tf.feature_column.input_layer(
        features,
        feature_columns=[bow_embedding])

    training = False
    if mode == tf.estimator.ModeKeys.TRAIN:
        training = True

    bow_dropout = tf.layers.dropout(
        bow,
        rate=params['dropout'],
        training=training)

    logits = tf.layers.dense(
        bow_dropout,
        params['num_labels'],
        activation=None)

    return estimator_spec_for_softmax_classification(
        logits=logits, labels=labels, mode=mode, params=params)
