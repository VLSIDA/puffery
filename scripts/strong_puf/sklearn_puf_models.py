from sklearn.linear_model import LogisticRegression
from sklearn import tree  
from sklearn.ensemble import RandomForestClassifier  
from sklearn.svm import SVC  
from sklearn.neighbors import KNeighborsClassifier  
from sklearn.naive_bayes import GaussianNB
import sys
import numpy as np
import crp_util

def seed_and_shuffle(np_array, seed):
    np.random.seed(seed)
    np.random.shuffle(np_array)

def split_data(training_size, features, labels, seed):
    #If total examples is not a multiple of 10 it will break... 
    num_examples = len(features)
    test_size = num_examples - training_size

    # Order is maintained as shuffle uses the same random seed 
    seed_and_shuffle(features, seed)
    seed_and_shuffle(labels, seed)

    x_train, y_train = features[:training_size], labels[:training_size]
    x_test, y_test = features[training_size:], labels[training_size:]
    return x_train, y_train, x_test, y_test

def get_learning_rates(training_size, features, labels):

    num_examples = len(features)
    print('Total Samples: {}'.format(num_examples))
    print('Training with {} samples. Accuracy tested with {} samples.\n'.format(training_size, num_examples-training_size))

    # Split the data in different ways depending on the run and average the accuracies 
    starting_seed = 123456
    num_runs = 10
    models = ['Logic Regression', 'Decision Tree', 
              'Random Forest', 'Support Vector Machines', 
              'K-Nearest Neighbors', 'Two-Class Bayes']
    accuracies = {name:[] for name in models} 
    for seed in range(starting_seed, starting_seed+num_runs):
    
        x_train, y_train, x_test, y_test = split_data(training_size, features, labels, seed)
    

        #Classifier instantiations
        log_reg = LogisticRegression()
        tree_model = tree.DecisionTreeClassifier(max_depth=3) 
        rand_forest = RandomForestClassifier()  
        svm_model = SVC(probability=True)
        knn_model = KNeighborsClassifier(n_neighbors=3)   
        bayes_model = GaussianNB()  
        classifiers = [('Logic Regression', log_reg), 
                       ('Decision Tree',tree_model), 
                       ('Random Forest', rand_forest),
                       ('Support Vector Machines',svm_model), 
                       ('K-Nearest Neighbors', knn_model), 
                       ('Two-Class Bayes', bayes_model)]

        for name, model in classifiers:
            model.fit(x_train, y_train)
            test_predictions = model.predict(x_test)
            score = model.score(x_test, y_test)
            accuracies[name].append(score)
            #print('{} Accuracy: {}'.format(name,score))

    # Average accuracies of the runs and print
    print('Data trained on {} splits of dataset'.format(num_runs))
    print('Displaying average accuracies:')
    for name in models:
        avg_accuracy = sum(accuracies[name])/len(accuracies[name])
        print('{} Accuracy: {:.3f}'.format(name,avg_accuracy))

#Challenge and response from actual PUF data
puf_csv = open('data/puf_data_c16_r1.csv',newline='')
challenges, responses = crp_util.get_challenge_response_from_csv(puf_csv)
challenge_size = len(challenges[0])
response_size = len(responses[0]) # Can only handle response size=1
# Convert to np arrays
challenges, responses = np.asarray(challenges), np.ravel(responses)

if len(challenges) != len(responses):
    print("Number of challenges does not equal number of responses.")
    sys.exit(1)

print("Total CRPs available:", len(challenges))    
size_str = input("Enter number for CRPs for training (default 80% of total): ")
if not size_str :
    training_size = int(len(challenges)*.8)
else:
    training_size = int(size_str)

# import warnings filter
from warnings import simplefilter
# ignore all future warnings
simplefilter(action='ignore', category=FutureWarning)    
get_learning_rates(training_size, challenges, responses)    
 

