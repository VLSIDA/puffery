#!/usr/bin/env python3
# See LICENSE for licensing information.
#
# Copyright (c) 2019-2021, VLSI Design & Automation Group
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
       
    style_bank = ['ro', 'bs', 'g^', 'c*', 'kX', 'mD', 'yP']
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

def display_accuracy_by_access(x_data, y_model_data, name_order=None):
    """Models share the same x axis (number of training examples) with different y values.
       Displayed together in a single graph"""
       
    style_bank = ['ro', 'bs', 'g^', 'c*', 'kX', 'mD', 'yP']
    if len(style_bank) < len(y_model_data):
        print('Not enough styles for every model.')
        sys.exit(1)
        
    style_pos = 0    
    names = list(y_model_data.keys())
    names_with_10bits = [name for name in names]
    
    names.sort()
    
    if name_order:
        for name in name_order:
            plt.plot(x_data, y_model_data[name], style_bank[style_pos], linestyle='solid', label=name)
            #plt.plot(x_data, y_model_data[name], style_bank[style_pos], linestyle='', label=name)
            style_pos+=1
    else:
        for name, accuracy in y_model_data.items():
            plt.plot(x_data, accuracy, style_bank[style_pos], linestyle='solid', label=name)
            #plt.plot(x_data, accuracy, style_bank[style_pos], linestyle='', label=name)
            style_pos+=1
    
    plt.xlabel("MAP Accesses")
    plt.ylabel("Prediction Accuracy")
    plt.gca().legend()
    plt.show()

def save_data(x_data, y_model_data):
    """Save all accuracies to a single csv"""
        
    import csv    
    
    # File setup
    file_name = 'puf_accuracies.csv'
    csv_file = open(file_name, 'w')
    fields = ['training_examples'] + list(y_model_data.keys())
    csv_writer = csv.writer(csv_file, lineterminator = '\n')
    csv_writer.writerow(fields)    
        
    # write training examples and accuracies
    for example_ind in range(len(x_data)):
        row = [x_data[example_ind]]
        for model_name in y_model_data.keys():
            row.append("%.3g" % y_model_data[model_name][example_ind])
        csv_writer.writerow(row) 
    csv_file.close()     

def model_accuracy_with_varied_training(train_data, test_data, train_point=None, display_and_save=True):
    
    train_features, train_labels = train_data
    test_features, test_labels = test_data
    
    print('Total Samples: {}'.format(len(train_features)+len(test_features)))
    print('Training with {} samples. Accuracy tested with {} samples.\n'.format(len(train_features), len(test_features)))

    # Can define a single point of training as an option rather than dividing the range
    if train_point:
        assert(type(train_point)==float)
        progressive_training_steps = [int(len(train_features)*train_point)]
    else:
        progressive_training_steps = get_train_steps(len(train_features), 0.05)
    
    starting_seed = 123456
    num_runs = 2
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
        
    if display_and_save:    
        display_data(progressive_training_steps, avg_accuracies)
        save_data(progressive_training_steps, avg_accuracies)
    
    return avg_accuracies
    
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

 

