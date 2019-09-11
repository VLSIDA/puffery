#!/usr/bin/env python3
# See LICENSE for licensing information.
#
# Copyright (c) 2016-2019 Regents of the University of California and The Board
# of Regents for the Oklahoma Agricultural and Mechanical College
# (acting for and on behalf of Oklahoma State University)
# All rights reserved.
#

from sklearn.linear_model import LogisticRegression
from sklearn import tree  
from sklearn.ensemble import RandomForestClassifier  
from sklearn.svm import SVC  
from sklearn.neighbors import KNeighborsClassifier  
from sklearn.naive_bayes import GaussianNB
import matplotlib.pyplot as plt
import sys
import os
import numpy as np
import crp_util

def seed_and_shuffle(np_array, seed):
    np.random.seed(seed)
    np.random.shuffle(np_array)

def split_data(training_size, features, labels, seed):
    if not isinstance(training_size, int):
        print('Cannot split dataset using a non-integer value: {}.'.format(type(training_size)))
        sys.exit(1)
    num_examples = len(features)
    test_size = num_examples - training_size

    # Order is maintained as shuffle uses the same random seed 
    seed_and_shuffle(features, seed)
    seed_and_shuffle(labels, seed)

    x_left, y_left = features[:training_size], labels[:training_size]
    x_right, y_right = features[training_size:], labels[training_size:]
    return (x_left, y_left), (x_right, y_right)

def get_train_steps(total, step_size):
    step = max(1, int(step_size * total))
    steps = [i for i in range(step, total, step)]
    steps.append(total)
    return steps
    
def display_data(x_data, y_model_data):
    """Models share the same x axis (number of training examples) with different y values.
       Displayed together in a single graph"""
       
    style_bank = ['ro', 'bs', 'g^', 'c*', 'kX', 'mD']
    if len(style_bank) < len(y_model_data):
        print('Not enough styles for every model.')
        sys.exit(1)
        
    style_pos = 0    
    for name, accuracy in y_model_data.items():
        plt.plot(x_data, accuracy, style_bank[style_pos], linestyle='solid', label=name)
        style_pos+=1
    
    plt.xlabel("Size of Training Set")
    plt.ylabel("Prediction Accuracy")
    plt.gca().legend()
    plt.show()

def model_accuracy_with_varied_training(train_data, test_data):
    
    train_features, train_labels = train_data
    test_features, test_labels = test_data
    
    print('Total Samples: {}'.format(len(train_features)+len(test_features)))
    print('Training with {} samples. Accuracy tested with {} samples.\n'.format(len(train_features), len(test_features)))

    progressive_training_steps = get_train_steps(len(train_features), 0.05)
    
    starting_seed = 123456
    num_runs = 10
    train_split_seeds = range(starting_seed, starting_seed+num_runs)
    models = ['Logistic Regression', 'Decision Tree', 
              'Random Forest', 'Support Vector Machines', 
              'K-Nearest Neighbors', 'Two-Class Bayes']
    avg_accuracies = {name:[] for name in models} 
    
    print('Data trained on {} different splits of dataset'.format(num_runs))
    print('Displaying average accuracies:')
    for training_size in progressive_training_steps:
        print("Using {} examples to train models.".format(training_size))
        # Split the data in different ways depending on the run and save accuracies per model
        temp_accr = {name:[] for name in models} 
        for seed in train_split_seeds:
            train_split, train_unused = split_data(training_size, train_features, train_labels, seed)
            seed_accuracy = train_and_predict_with_models(train_split, test_data)
            for name in models:
                temp_accr[name].append(seed_accuracy[name])
            
        # Average accuracies of the runs and print
        for name in models:
            avg_accuracy = sum(temp_accr[name])/len(temp_accr[name])
            avg_accuracies[name].append(avg_accuracy)
            print('{} Accuracy: {:.3f}'.format(name,avg_accuracy))
        print('')
        
    display_data(progressive_training_steps, avg_accuracies)
    
def train_and_predict_with_models(train_data, test_data):
    """Given training (features, labels) and test (features, labels) data. Trains data
       on different models and returns accuracies on the test data."""
       
    x_train, y_train = train_data 
    x_test, y_test = test_data
    accuracies = {}
    
    #Classifier instantiations
    log_reg = LogisticRegression()
    tree_model = tree.DecisionTreeClassifier(max_depth=3) 
    rand_forest = RandomForestClassifier()  
    svm_model = SVC(probability=True)
    knn_model = KNeighborsClassifier(n_neighbors=3)   
    bayes_model = GaussianNB()  
    classifiers = [('Logistic Regression', log_reg), 
                   ('Decision Tree',tree_model), 
                   ('Random Forest', rand_forest),
                   ('Support Vector Machines',svm_model), 
                   ('K-Nearest Neighbors', knn_model), 
                   ('Two-Class Bayes', bayes_model)]

    for name, model in classifiers:
        model.fit(x_train, y_train)
        #test_predictions = model.predict(x_test)
        accuracies[name] = model.score(x_test, y_test)
        #print('{} Accuracy: {}'.format(name,score))
        
    return accuracies   

 

