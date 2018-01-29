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


def eval_confusion_matrix(labels, predictions, num_classes):
    with tf.variable_scope("eval_confusion_matrix"):
        con_matrix = tf.confusion_matrix(labels=labels, predictions=predictions,
                                         num_classes=num_classes)

        con_matrix_sum = tf.Variable(
            tf.zeros(shape=(num_classes, num_classes), dtype=tf.int32),
            trainable=False,
            name="confusion_matrix_result",
            collections=[tf.GraphKeys.LOCAL_VARIABLES])

        update_op = tf.assign_add(con_matrix_sum, con_matrix)

        return tf.convert_to_tensor(con_matrix_sum), update_op


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

    softmax_loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)
    l2_loss = params['weight_decay'] * tf.add_n(
        [tf.nn.l2_loss(v) for v in tf.trainable_variables()])

    loss = softmax_loss + l2_loss

    logging_hook = tf.train.LoggingTensorHook({}, every_n_iter=100)
    if params['show_loss']:
        logging_hook = tf.train.LoggingTensorHook({"loss": loss}, every_n_iter=10)

    if mode == tf.estimator.ModeKeys.TRAIN:
        optimizer = tf.train.AdamOptimizer(learning_rate=params['lr'])
        train_op = optimizer.minimize(loss, global_step=tf.train.get_global_step())

        return tf.estimator.EstimatorSpec(
            mode,
            loss=loss,
            train_op=train_op,
            training_hooks=[logging_hook])

    eval_metric_ops = {
        'accuracy': tf.metrics.accuracy(
            labels=labels, predictions=predicted_classes),
        'confusion_matrix': eval_confusion_matrix(labels, predicted_classes, params['num_labels'])
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
        combiner='sqrtn',
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

    h1 = tf.layers.dense(
        bow_dropout,
        params['num_units'],
        activation=tf.nn.relu)

    h1_dropout = tf.layers.dropout(
        h1,
        rate=params['dropout'],
        training=training)

    logits = tf.layers.dense(
        h1_dropout,
        params['num_labels'],
        activation=None)

    return estimator_spec_for_softmax_classification(
        logits=logits, labels=labels, mode=mode, params=params)