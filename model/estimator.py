import tensorflow as tf

from model.input_pipeline import MovieReviewDataset
from utils.metrics import print_metrics_score, save_model_metrics


def get_estimator(estimator_name):
    if estimator_name == 'bag_of_words':
        estimator = BagOfWords()
    elif estimator_name == 'recurrent':
        estimator = RecurrentModel()

    return estimator


def run_estimator(estimator, model_params, pipeline_params, num_epochs, save_path):
    classifier = tf.estimator.Estimator(
        model_fn=estimator.model_fn,
        params=model_params
    )

    train_accuracies = []
    validation_accuracies = []

    for i in range(num_epochs):
        print('Running epoch {}'.format(i+1))
        classifier.train(
            input_fn=lambda: estimator.input_fn(
                tfrecord_file=pipeline_params['train_file'],
                batch_size=pipeline_params['batch_size'],
                perform_shuffle=True,
                bucket_width=pipeline_params['bucket_width'],
                num_buckets=pipeline_params['num_buckets'])
        )

        train_result = classifier.evaluate(
            input_fn=lambda: estimator.input_fn(
                tfrecord_file=pipeline_params['train_file'],
                batch_size=pipeline_params['batch_size'],
                perform_shuffle=True,
                bucket_width=pipeline_params['bucket_width'],
                num_buckets=pipeline_params['num_buckets'])
        )

        eval_result = classifier.evaluate(
            input_fn=lambda: estimator.input_fn(
                tfrecord_file=pipeline_params['validation_file'],
                batch_size=pipeline_params['batch_size'],
                perform_shuffle=False,
                bucket_width=pipeline_params['bucket_width'],
                num_buckets=pipeline_params['num_buckets'])
        )

        train_accuracies.append(train_result['accuracy'])
        validation_accuracies.append(eval_result['accuracy'])

        print_metrics_score(train_result, 'Train')
        print_metrics_score(eval_result, 'Validation')

    test_result = classifier.evaluate(
        input_fn=lambda: estimator.input_fn(
            tfrecord_file=pipeline_params['test_file'],
            batch_size=pipeline_params['batch_size'],
            perform_shuffle=False,
            bucket_width=pipeline_params['bucket_width'],
            num_buckets=pipeline_params['num_buckets'])
    )

    print('Saving model results ...')
    save_model_metrics(test_result, train_accuracies, validation_accuracies, save_path)


class ModelEstimator:

    def input_fn(self, tfrecord_file, batch_size, perform_shuffle, bucket_width, num_buckets):
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

    def eval_confusion_matrix(self, labels, predictions, num_classes):
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

    def estimator_spec_for_softmax_classification(self, logits, labels, mode, params):

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
            'confusion_matrix': self.eval_confusion_matrix(
                labels, predicted_classes, params['num_labels'])
        }

        return tf.estimator.EstimatorSpec(
            mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)

    def model_fn(self, features, labels, mode, params):
        labels = self.preprocess_labels(labels)
        params = self.set_training_params(params)

        logits_train = self.model(
            features,
            mode,
            params)

        params = self.set_test_params(params)

        logits_test = self.model(
            features,
            mode,
            params)

        if mode == tf.estimator.ModeKeys.TRAIN:
            return self.estimator_spec_for_softmax_classification(
                logits_train, labels, mode, params)

        return self.estimator_spec_for_softmax_classification(
            logits_test, labels, mode, params)

    def preprocess_labels(self, labels):
        raise NotImplementedError

    def set_training_params(self, params):
        raise NotImplementedError

    def set_test_params(self, params):
        raise NotImplementedError

    def model(self, features, mode, params):
        raise NotImplementedError


class BagOfWords(ModelEstimator):

    def preprocess_labels(self, labels):
        return labels - 1

    def set_training_params(self, params):
        params['reuse'] = False
        params['training'] = True

        return params

    def set_test_params(self, params):
        params['reuse'] = True
        params['training'] = False

        return params

    def model(self, features, mode, params):
        with tf.variable_scope('BagOfWords', reuse=params['reuse']):
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

            bow_dropout = tf.layers.dropout(
                bow,
                rate=params['dropout'],
                training=params['training'])

            logits = tf.layers.dense(
                bow_dropout,
                params['num_labels'],
                activation=None)

        return logits


class RecurrentModel(ModelEstimator):

    def preprocess_labels(self, labels):
        return labels - 1

    def set_training_params(self, params):
        params['reuse'] = False
        params['training'] = True

        return params

    def set_test_params(self, params):
        params['reuse'] = True
        params['training'] = False
        params['embedding_dropout'] = 1.0
        params['lstm_output_dropout'] = 1.0
        params['lstm_variational_dropout'] = 1.0

        return params

    def model(self, features, mode, params):
        with tf.variable_scope('RecurrentModel', reuse=params['reuse']):
            """RNN model to predict from sequence of words to a class."""
            base_embeddings = tf.get_variable(
                'embeddings',
                shape=(params['vocab_size'], params['embed_size']),
                initializer=tf.constant_initializer(params['embedding']),
                dtype=tf.float32)
            embeddings_dropout = tf.layers.dropout(
                base_embeddings,
                rate=params['embedding_dropout'],
                training=params['training'])
            inputs = tf.nn.embedding_lookup(embeddings_dropout, features['words'])

            cell = tf.nn.rnn_cell.LSTMCell(params['num_units'])

            dropout_cell = tf.nn.rnn_cell.DropoutWrapper(
                    cell,
                    output_keep_prob=params['lstm_output_dropout'],
                    state_keep_prob=params['lstm_variational_dropout'],
                    variational_recurrent=True,
                    input_size=params['embed_size'],
                    dtype=tf.float32)

            _, state = tf.nn.dynamic_rnn(
                dropout_cell,
                inputs,
                sequence_length=features['size'],
                dtype=tf.float32)

            logits = tf.layers.dense(
                state.h,
                params['num_labels'],
                activation=None)

            return logits
