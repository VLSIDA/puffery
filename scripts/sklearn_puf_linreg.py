from sklearn.linear_model import LogisticRegression
import numpy as np
import crp_util

#Inputs and labels using randomly generated data
# challenge_size = 16
# response_size = 32
# num_examples = 20000
# challenges, responses = crp_util.get_simulated_challenge_response_pairs(num_examples, challenge_size)

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

logisticRegr = LogisticRegression()
logisticRegr.fit(x_train, y_train)

test_predictions = logisticRegr.predict(x_test)
score = logisticRegr.score(x_test, y_test)
print('Actual Responses: ', y_test)
print('Predicted Responses: ', test_predictions)
print('Test Set accuracy: ', score)