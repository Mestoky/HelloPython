import os
import xlrd
import numpy as np
import tensorflow as tf
import tensorflow.contrib.slim as slim


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
STEPS = 50000
work_dir = r'E:\pyex\data'
array = [6, 7, 8, 9, 11, 28, 29, 30, 31, 32, 33, 34, 40, 41, 68, 69, 72]
train_log_dir = r'Z:\train_log'
BATCH = 64


def inference(net):
    with slim.arg_scope([slim.fully_connected],
                        activation_fn=tf.nn.crelu,
                        weights_initializer=slim.xavier_initializer(),  # 你尝试一下这个初始化器，网上推荐的
                        weights_regularizer=slim.l2_regularizer(0.0005)):
        net = slim.stack(net, slim.fully_connected, [32, 128, 32, 8], scope='fc')
        net = slim.fully_connected(net, 1, activation_fn=None, scope='fc/fc_5')
    return net


def get_data():
    os.chdir(work_dir)
    dataset = []
    for parent, _, filenames in os.walk(work_dir, followlinks=True):
        for filename in filenames:  # 如果你的数据可放在同一目录下的话，可以考虑使用for filename in os.listdir(...)
            wb = xlrd.open_workbook(filename=os.path.join(parent, filename))
            ws = wb.sheet_by_name('1')
            dataset += [[ws.cell(r, c).value for c in array] for r in range(2, ws.nrows, 3)]  # 我觉得xlrd应该会有批量读取的方法吧
    data = np.array(dataset)
    y = (data[:, 7] - data[:, 6]) * data[:, 5] * (4200 * 1000 / 3600) / 1000000  # 我不确定这样改是对的，你需要确认一下
    data = np.c_[dataset, y]
    data = np.delete(data, 7, axis=1)
    return data


def normal(m):
    col_max, col_min = m.max(axis=0), m.min(axis=0)
    return np.nan_to_num((m-col_min)/(col_max - col_min))


def start_training(datas):
    tf.gfile.MakeDirs(train_log_dir)  # tf.gfile.MakeDirs会自己检测文件夹是否已存在

    # 对于绝大多数问题，建议还是把图建在原生default graph上，而不是在新建的tf.Graph上，目的是方便调试
    # 所以这里去除了with tf.Graph().as_default():
    # Set up the data loading:
    feature = tf.placeholder(dtype=tf.float32, shape=[None, 16])
    heat = tf.placeholder(dtype=tf.float32, shape=[None])  # 我理解你的目标应该是1维列表而不是2维

    # Define the model:
    predictions = inference(feature)

    # Specify the loss function:
    abs_loss = tf.losses.absolute_difference(heat, predictions)  # 常见loss函数建议使用tf.losses
    sq_loss = tf.losses.mean_squared_error(heat, predictions, loss_collection=None))  # 不将sq_loss纳入总损失
    total_loss = tf.losses.get_total_loss()  # 现在的总损失是abs损失+正则损失

    # Specify the optimization scheme:
    global_step = tf.train.get_or_create_global_step()  # 建议使用tf.train.get_or_create_global_step建立global step

    ema = tf.train.ExponentialMovingAverage(0.99, num_updates=global_step)
    average_op = ema.apply(tf.trainable_variables())
    train_op = tf.train.AdamOptimizer().minimize(total_loss, global_step=global_step)  # Adam优化器基本不需要自设定学习率
    with tf.control_dependencies([train_op, average_op]):
        train_op_with_total_loss = tf.identity(total_loss)  # 建议使用这种方式连接train op，方便后续训练过程中观察损失

    # 变量存取器
    saver = tf.train.Saver()  # Saver的实例化应该放在训练循环外，因为每次实例化过程都会在计算图中增加新的Saver节点
    restorer = tf.train.Saver(ema.variables_to_restore())

    # initialize var in graph`
    sess = tf.Session()
    sess.run([tf.global_variables_initializer(), tf.local_variables_initializer()])  # 全局和局部变量用这一句初始化就可以了

    # train and test data  # 这一段事实上不应该放在主函数里，而应该放在数据准备部分的函数里
    data_size = datas.shape[0]
    random_order = np.random.permutation(data_size)
    split_index = int(data_size * 0.9)
    data, datat = datas[random_order[:split_index]], datas[random_order[split_index:]]  # 更pythonic随机数据抽取
    num = data.shape[0]

    # Main Loop
    start = 0
    for step in range(1, STEPS+1):
        # 主训练部分
        total_loss_, sq_loss_, abs_loss_ = \
            sess.run([train_op_with_total_loss, sq_loss, abs_loss],  # ↓numpy会自动处理超过范围的索引（只返回有效索引内的数据）
                     feed_dict={feature: data[start:start+BATCH, :-1], heat: data[start:start+BATCH, -1]})
        start += BATCH
        if start >= num:
            data = data[np.random.permutation(num)]
            start = 0

        # 验证部分
        if step % 1000 == 0:
            # Apply the Moving Average Variables
            saver.save(sess, train_log_dir + '\model.ckpt')
            restorer.restore(sess, train_log_dir + '\model.ckpt')
            # Test the model
            loss_t, abs_loss_t = \
                sess.run([sq_loss, abs_loss], feed_dict={feature: datat[:, :-1], heat: datat[:, -1]})
            print('STEP:%d'
                  '\nTrain:   SQLOSS:%.6f, Mean_absolute_loss:%.6f'
                  '\nTest:   SQLOSS:%.6f, Mean_absolute_loss:%.6f'
                  % (step, sq_loss_, abs_loss_, loss_t, abs_loss_t))
            # 现在这样验证就要求一次性把datat全部喂入，如果未来数据量过大不能一次性喂入，
            # 之前应考虑使用tf.metrics.mean_squared_error、tf.metrics.mean_absolute_error这样的评判函数，
            # 然后就可以把datat分多批次喂入，最后统计累计平均误差

    sess.close()


if __name__ == '__main__':
    data_ = get_data()
    data_[:, :-1] = normal(data_[:, :-1])
    start_training(data_)
