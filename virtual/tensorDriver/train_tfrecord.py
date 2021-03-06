import argparse
import os
import tensorflow as tf
import time
from driving_data import HandleData
import model
import model_util as util

# Example: python train.py --input=DrivingData.h5 --gpu=0 --checkpoint_dir=save/model.ckpt
parser = argparse.ArgumentParser(description='Train network')
parser.add_argument('--input_list', type=str, required=False, default='FileList.txt', help='Training list of TFRecord files')
parser.add_argument('--input_val', type=str, required=False, default='', help='Validation TFRecord file')
parser.add_argument('--gpu', type=int, required=False, default=0, help='GPU number (-1) for CPU')
parser.add_argument('--checkpoint_dir', type=str, required=False, default='', help='Load checkpoint')
parser.add_argument('--logdir', type=str, required=False, default='./logs', help='Tensorboard log directory')
parser.add_argument('--savedir', type=str, required=False, default='./save', help='Tensorboard checkpoint directory')
parser.add_argument('--epochs', type=int, required=False, default=600, help='Number of epochs')
parser.add_argument('--batch', type=int, required=False, default=400, help='Batch size')
parser.add_argument('--learning_rate', type=float, required=False, default=0.0001, help='Initial learning rate')
args = parser.parse_args()

def train_network(input_list, input_val_hdf5, gpu, pre_trained_checkpoint, epochs, batch_size, logs_path, save_dir):

    # Create log directory if it does not exist
    if not os.path.exists(logs_path):
        os.makedirs(logs_path)

    # Set enviroment variable to set the GPU to use
    if gpu != -1:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)
    else:
        print('Set tensorflow on CPU')
        os.environ["CUDA_VISIBLE_DEVICES"] = ""

    # Get file list
    list_tfrecord_files = HandleData.get_list_from_file(input_list)

    # Create the graph input part (Responsible to load files, do augmentations, etc...)
    images, labels = util.create_input_graph(list_tfrecord_files, epochs, batch_size)

    # Build Graph
    model_out, dropout_prob = model.build_graph_no_placeholder(images)

    # Create histogram for labels
    tf.summary.histogram("steer_angle", labels)

    # Define number of epochs and batch size, where to save logs, etc...
    iter_disp = 10
    start_lr = args.learning_rate

    # Avoid allocating the whole memory
    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.6)
    sess = tf.InteractiveSession(config=tf.ConfigProto(gpu_options=gpu_options))

    # Regularization value
    L2NormConst = 0.001

    # Get all model "parameters" that are trainable
    train_vars = tf.trainable_variables()

    # Loss is mean squared error plus l2 regularization
    # model.y (Model output), model.y_(Labels)
    # tf.nn.l2_loss: Computes half the L2 norm of a tensor without the sqrt
    # output = sum(t ** 2) / 2
    with tf.name_scope("MSE_Loss_L2Reg"):
        loss = tf.reduce_mean(tf.square(tf.subtract(labels, model_out))) + tf.add_n(
            [tf.nn.l2_loss(v) for v in train_vars]) * L2NormConst

    # Add model accuracy
    with tf.name_scope("Loss_Validation"):
        loss_val = tf.reduce_mean(tf.square(tf.subtract(labels, model_out)))

    # Solver configuration
    with tf.name_scope("Solver"):
        global_step = tf.Variable(0, trainable=False)
        starter_learning_rate = start_lr
        # decay every 10000 steps with a base of 0.96
        learning_rate = tf.train.exponential_decay(starter_learning_rate, global_step,
                                                   1000, 0.9, staircase=True)

        train_step = tf.train.AdamOptimizer(learning_rate).minimize(loss, global_step=global_step)

    # Initialize all random variables (Weights/Bias)
    init_op = tf.group(tf.global_variables_initializer(),tf.local_variables_initializer())
    sess.run(init_op)

    # Start input enqueue threads.
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(sess=sess, coord=coord)

    # Load checkpoint if needed
    if pre_trained_checkpoint:
        # Load tensorflow model
        print("Loading pre-trained model: %s" % args.checkpoint_dir)
        # Create saver object to save/load training checkpoint
        saver = tf.train.Saver(max_to_keep=None)
        saver.restore(sess, args.checkpoint_dir)
    else:
        # Just create saver for saving checkpoints
        saver = tf.train.Saver(max_to_keep=None)

    # Monitor loss, learning_rate, global_step, etc...
    tf.summary.scalar("loss_train", loss)
    tf.summary.scalar("loss_val", loss_val)
    tf.summary.scalar("learning_rate", learning_rate)
    tf.summary.scalar("global_step", global_step)
    # merge all summaries into a single op
    merged_summary_op = tf.summary.merge_all()

    # Configure where to save the logs for tensorboard
    summary_writer = tf.summary.FileWriter(logs_path, graph=tf.get_default_graph())

    try:
        step = 0
        while not coord.should_stop():
            start_time = time.time()

            # Run one step of the model.  The return values are
            # the activations from the `train_op` (which is
            # discarded) and the `loss` op.  To inspect the values
            # of your ops or variables, you may include them in
            # the list passed to sess.run() and the value tensors
            # will be returned in the tuple from the call.
            _, loss_value = sess.run([train_step, loss], feed_dict={dropout_prob: 0.8})

            duration = time.time() - start_time

            # Print an overview fairly often.
            if step % 100 == 0:
                print('Step %d: loss = %.2f (%.3f sec)' % (step, loss_value,
                                                           duration))
            step += 1

            # write logs at every iteration
            summary = merged_summary_op.eval(feed_dict={dropout_prob: 1.0})
            summary_writer.add_summary(summary, batch_size + step)

    except tf.errors.OutOfRangeError:
        #print('Done training for %d epochs, %d steps.' % (FLAGS.num_epochs, step))
        print('error')
    finally:
        # When done, ask the threads to stop.
        coord.request_stop()

        # Wait for threads to finish.
    coord.join(threads)
    sess.close()



if __name__ == "__main__":
    # Call function that implement the auto-pilot
    train_network(args.input_list, args.input_val, args.gpu,
                  args.checkpoint_dir, args.epochs, args.batch, args.logdir, args.savedir)
