import pickle

import tensorflow as tf

from model.input_pipeline import MovieReviewDataset
from utils.metrics import print_metrics_score, save_model_metrics


class EstimatorManager:
    def __init__(self, estimator_name, model_params, pipeline_params, num_epochs, save_path):
        self.estimator_name = estimator_name
        self.model_params = model_params
        self.pipeline_params = pipeline_params
        self.num_epochs = num_epochs
        self.save_path = save_path

        self.get_estimator()

    def get_estimator(self):
        if self.estimator_name == 'bag_of_words':
            self.estimator = BagOfWords()
        elif self.estimator_name == 'recurrent':
            self.estimator = RecurrentModel()
        elif self.estimator_name == 'cnn':
            self.estimator = CNNModel()

    def get_input_pipeline(self, file_type, perform_shuffle):
        return self.estimator.input_fn(
            tfrecord_file=self.pipeline_params[file_type],
            batch_size=self.pipeline_params['batch_size'],
            perform_shuffle=perform_shuffle,
            bucket_width=self.pipeline_params['bucket_width'],
            num_buckets=self.pipeline_params['num_buckets'])

    def show_wrong_predictions(self, file_type):
        with open(file_type, 'rb') as ft:
            validation = pickle.load(ft)

        labels = [label for _, _, label, _ in validation]
        reviews = [review for review, _, _, _ in validation]

        predictions = self.classifier.predict(
                input_fn=lambda: self.get_input_pipeline(
                    'validation_file', False)
        )

        num_predictions = 10
        i = 0

        for pred, label, review in zip(predictions, labels, reviews):
            pred_label = pred['class']
            if pred_label != label - 1 and i < num_predictions:
                print("Predicted label: {}\nCorrect label: {}\n{}\n".format(
                    pred_label, label - 1, review))
                i += 1

            if i == num_predictions:
                break

    def run_estimator(self):
        self.classifier = tf.estimator.Estimator(
            model_fn=self.estimator.model_fn,
            params=self.model_params
        )

        train_accuracies = []
        validation_accuracies = []

        for i in range(self.num_epochs):
            print('Running epoch {}'.format(i+1))
            self.classifier.train(
                input_fn=lambda: self.get_input_pipeline(
                    'train_file', True)
            )

            train_result = self.classifier.evaluate(
                input_fn=lambda: self.get_input_pipeline(
                    'train_file', False)
            )

            eval_result = self.classifier.evaluate(
                input_fn=lambda: self.get_input_pipeline(
                    'validation_file', False)
            )

            train_accuracies.append(train_result['accuracy'])
            validation_accuracies.append(eval_result['accuracy'])

            print_metrics_score(train_result, 'Train')
            print_metrics_score(eval_result, 'Validation')

        test_result = self.classifier.evaluate(
            input_fn=lambda: self.get_input_pipeline(
                'test_file', False)
        )

        file_type = self.pipeline_params['validation_file'].replace('tfrecord', 'pkl')
        self.show_wrong_predictions(file_type)

        print('Saving model results ...')
        save_model_metrics(test_result, train_accuracies, validation_accuracies, self.save_path)


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

        if mode != tf.estimator.ModeKeys.PREDICT:
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


class CNNModel(ModelEstimator):

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
        with tf.variable_scope('CNNModel', reuse=params['reuse']):
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

            # Add an extra dimension to inputs for convolutional purposes
            expanded_inputs = tf.expand_dims(inputs, -1)

            pooled_outputs = []
            for i, filter_size in enumerate(params['filters_size']):
                with tf.name_scope("conv-maxpool-{}".format(filter_size)):

                    conv = tf.layers.conv2d(
                        inputs=expanded_inputs,
                        filters=params['num_filters'],
                        kernel_size=[filter_size, params['embed_size']],
                        padding='valid',
                        activation=tf.nn.relu
                    )

                    max_pool = tf.layers.max_pooling2d(
                        inputs=conv,
                        pool_size=[params['text_size'] - filter_size + 1, 1],
                        strides=[1, 1],
                        padding='valid'
                    )

                pooled_outputs.append(max_pool)

            num_filters_total = params['num_filters'] * len(params['filters_size'])

            """
            The max_pool operation returns tensor with the following dimension:
            [batch_size, 1, 1, num_filters]. When applying the concat, we only want to concat
            the num_filters position.
            """
            pool = tf.concat(pooled_outputs, 3)
            pool_flat = tf.reshape(pool, [-1, num_filters_total])

            drop_pool = tf.layers.dropout(
                pool_flat,
                rate=params['dropout_rate'],
                training=params['training']
            )

            logits = tf.layers.dense(
                drop_pool,
                params['num_labels'],
                activation=None)

            return logits
