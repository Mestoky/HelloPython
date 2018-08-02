import os
import xlrd
import numpy as np
import tensorflow as tf
import tensorflow.contrib.slim as slim


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
STEPS = 50000
work_dir = r'E:\pyex\data'
train_log_dir = r'Z:\pyex\train_log'
BATCH = 64


def inference(net):
    with slim.arg_scope([slim.fully_connected],
                        activation_fn=tf.nn.crelu,
                        weights_initializer=tf.truncated_normal_initializer(0.0, 0.01),
                        weights_regularizer=slim.l2_regularizer(0.0005)):
        net = slim.stack(net, slim.fully_connected, [32, 128, 32, 8], scope='fc1')
        net = slim.fully_connected(net, 1, activation_fn=None, scope='fc3')
    return net


def get_data():
    os.chdir(work_dir)
    dataset = []
    for parent, dirnames, filenames in os.walk(work_dir, followlinks=True):
        for filename in filenames:
            file_path = os.path.join(parent)
            os.chdir(file_path)
            wb = xlrd.open_workbook(filename=filename)
            ws = wb.sheet_by_name('1')
            dataset += [[ws.cell(r, c).value for c in range(1, 12)] for r in range(2, ws.nrows, 3)]
    data = np.array(dataset)
    return data


def normal(m):
    col_max = m.max(axis=0)
    col_min = m.min(axis=0)
    return np.nan_to_num((m-col_min)/(col_max - col_min))


def start_training(datas):
    if not tf.gfile.Exists(train_log_dir):
        tf.gfile.MakeDirs(train_log_dir)

    with tf.Graph().as_default():
        # Set up the data loading:
        feature = tf.placeholder(dtype=tf.float32, shape=[None, 10])
        power = tf.placeholder(dtype=tf.float32, shape=[None, 1])

        # Define the model:
        predictions = inference(feature)

        # Specify the loss function:
        absloss = tf.reduce_mean(tf.abs(power-predictions))
        sqloss = tf.reduce_mean(tf.square(power - predictions))
        slim.losses.add_loss(absloss)

        total_loss = slim.losses.get_total_loss()  # tf.losses.get_total_loss()  #

        # Specify the optimization scheme:
        global_step = tf.Variable(0, trainable=False)
        learning_rate = tf.train.exponential_decay(0.07, global_step, 100, 0.999)
        ema = tf.train.ExponentialMovingAverage(0.99, global_step)
        average_op = ema.apply(tf.trainable_variables())
        train_step = tf.train.AdamOptimizer(learning_rate=learning_rate) \
            .minimize(total_loss, global_step=global_step)
        train_op = tf.group(train_step, average_op)

        # initialize var in graph`
        sess = tf.Session()
        init_op = tf.group(tf.global_variables_initializer(),
                           tf.local_variables_initializer())  # the local var is for update_op
        sess.run(init_op)

        # train and test data
        train_indices = np.random.choice(datas.shape[0], round(datas.shape[0] * 0.9), replace=False)
        test_indices = np.array(list(set(range(datas.shape[0])) - set(train_indices)))
        data = datas[train_indices, :]
        datat = datas[test_indices, :]

        # Main Loop
        restart = 0
        num = data.shape[0]
        shuffled_data = 0.0
        start = 0
        end = BATCH

        for step in range(1, STEPS+1):
            if step == 1 or restart:
                # print('Step:%d: Start Again!!!' % sess.run(global_step))
                restart = 0
                start = 0
                end = BATCH
                permutation = np.random.permutation(num)
                shuffled_data = data[permutation, :]
                # print(shuffled_data[start:end, 0].reshape((end-start, 1)).shape)
            _, loss_, mean_absolute_loss_ = sess.run([train_op, sqloss, absloss], feed_dict={
                feature: shuffled_data[start:end, 1:11],
                power: shuffled_data[start:end, 0].reshape((end-start, 1))
            })
            start += BATCH
            end += BATCH
            if end >= num:
                restart = 1
                end = num
            if step % 1000 == 0:
                # Apply the Moving Average Variables
                saver = tf.train.Saver()
                saver.save(sess, train_log_dir + '\model.ckpt')
                saver = tf.train.Saver(ema.variables_to_restore())
                saver.restore(sess, train_log_dir + '\model.ckpt')
                # Test the model
                loss_t, mean_absolute_loss_t = sess.run([sqloss, absloss], feed_dict={
                    feature: datat[:, 1:11],
                    power: datat[:, 0].reshape((datat.shape[0], 1))
                })
                print('STEP:%d'
                      '\nTrain:   SQLOSS:%.6f, Mean_absolute_loss:%.6f'
                      '\nTest:   SQLOSS:%.6f, Mean_absolute_loss:%.6f'
                      % (step, loss_, mean_absolute_loss_, loss_t, mean_absolute_loss_t))
        sess.close()


if __name__ == '__main__':
    data_ = get_data()
    data_[:, 1:11] = normal(data_[:, 1:11])
    start_training(data_)


