'''
Adapted from Aymeric Damien's Tensorflow examples.
'''

from __future__ import print_function

import tensorflow as tf
import crp_util

#Inputs and labels using randomly generated data
# challenge_size = 16
# response_size = 32
# num_examples = 20000
# challenges, responses = crp_util.get_simulated_challenge_response_pairs(num_examples, challenge_size)

#Challenge and response from actual PUF data
puf_csv = open('../data/puf_data_c16_r1.csv',newline='')
challenges, responses = crp_util.get_challenge_response_from_csv(puf_csv)
#If total examples is not a multiple of 10 and 20 then it will break... 
#(training set is multiple of 10, batch size requires multiple of 20, can be fixed.)
num_examples = len(challenges)
test_size = num_examples//10
training_size = num_examples - test_size
challenge_size = len(challenges[0])
response_size = len(responses[0])

# Parameters
learning_rate = 0.01
training_epochs = 25
batch_size = 20
display_step = 1

# tf Graph Input
x = tf.placeholder(tf.float32, [None, challenge_size]) # mnist data image of shape 28*28=784
y = tf.placeholder(tf.float32, [None, response_size]) # 0-9 digits recognition => 10 classes

# Set model weights
W = tf.Variable(tf.zeros([challenge_size, response_size]))
b = tf.Variable(tf.zeros([response_size]))

# Construct model
pred = tf.nn.sigmoid(tf.matmul(x, W) + b) 
pre_activation = tf.matmul(x, W) + b 

# Minimize error using cross entropy
#cost = tf.reduce_mean(-tf.reduce_sum(y*tf.log(pred), reduction_indices=1))
cost = tf.losses.sigmoid_cross_entropy(y, pre_activation)

#These two combined are equivalent to the cost function above.
#https://stackoverflow.com/questions/46291253/tensorflow-sigmoid-and-cross-entropy-vs-sigmoid-cross-entropy-with-logits
#sig_cost = tf.nn.sigmoid_cross_entropy_with_logits(labels=y, logits=pre_activation)
#sum_cost = tf.reduce_mean(sig_cost)

# Gradient Descent
optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)

# Initialize the variables (i.e. assign their default value)
init = tf.global_variables_initializer()

# Start training
with tf.Session() as sess:

    # Run the initializer
    sess.run(init)

    # Training cycle
    for epoch in range(training_epochs):
        avg_cost = 0.
        total_batch = int(training_size/batch_size)
        # Loop over all batches
        for i in range(0, training_size, batch_size):
            batch_xs, batch_ys = challenges[i:i+batch_size], responses[i:i+batch_size]
            # Run optimization op (backprop) and cost op (to get loss value)
            _, c = sess.run([optimizer, cost], feed_dict={x: batch_xs,
                                                          y: batch_ys})
            # Compute average loss
            avg_cost += c / total_batch
        # Display logs per epoch step
        if (epoch+1) % display_step == 0:
            print("Epoch:", '%04d' % (epoch+1), "cost=", "{:.9f}".format(avg_cost))

    print("Optimization Finished!")

    test_inp, test_labels = challenges[training_size:], responses[training_size:]

    print('Responses: ',test_labels)
    print('Cost:',cost.eval({x: test_inp, y: test_labels}))
    preds = pred.eval({x: test_inp, y: test_labels})
    #print('Prediction Probabilities:', preds)
    rounded_preds = [crp_util.round_predictions(word) for word in preds]
    print('Rounded Predictions:', rounded_preds)
    accuracies = [crp_util.get_accuracy(pred,label) for pred,label in zip(rounded_preds, test_labels)]
    print('Accuracy Per CRP:', accuracies)
    print('Average Accuracy:', sum(accuracies)/len(accuracies))
