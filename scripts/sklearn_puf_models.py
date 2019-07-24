from sklearn.linear_model import LogisticRegression
from sklearn import tree  
from sklearn.ensemble import RandomForestClassifier  
from sklearn.svm import SVC  
from sklearn.neighbors import KNeighborsClassifier  
from sklearn.naive_bayes import GaussianNB
import numpy as np
import crp_util

#Challenge and response from actual PUF data
puf_csv = open('data/puf_data_c16_r1.csv',newline='')
challenges, responses = crp_util.get_challenge_response_from_csv(puf_csv)
#If total examples is not a multiple of 10 it will break... 
num_examples = len(challenges)
test_size = num_examples//10
training_size = num_examples - test_size
challenge_size = len(challenges[0])
response_size = len(responses[0])

#Cross validation not implemented. Simple split of dataset.
x_train, y_train = challenges[:training_size], np.ravel(responses[:training_size])
x_test, y_test = challenges[training_size:], np.ravel(responses[training_size:])

print('Model learning of PUF data intiated.')
print('Total Samples: {}'.format(num_examples))
print('Training with {} samples. Accuracy tested with {} samples.'.format(training_size, test_size))
print('')

#Classifier instantiations
log_reg = LogisticRegression()
tree_model = tree.DecisionTreeClassifier(max_depth=3) 
rand_forest = RandomForestClassifier()  
svm_model = SVC(probability=True)
knn_model = KNeighborsClassifier(n_neighbors=3)   
bayes_model = GaussianNB()  
classifiers = [('Logic Regression', log_reg), 
               ('Descision Tree',tree_model), 
               ('Random Forest', rand_forest),
               ('Support Vector Machines',svm_model), 
               ('K-Nearest Neighbors', knn_model), 
               ('Two-Class Bayes', bayes_model)]

print('Building PUF models with {} classifiers'.format(len(classifiers)))
for name, model in classifiers:
    model.fit(x_train, y_train)
    test_predictions = model.predict(x_test)
    score = model.score(x_test, y_test)
    print('{} Accuracy: {}'.format(name,score))

