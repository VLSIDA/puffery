#!/usr/bin/env python3
# See LICENSE for licensing information.
#
# Copyright (c) 2016-2019 Regents of the University of California and The Board
# of Regents for the Oklahoma Agricultural and Mechanical College
# (acting for and on behalf of Oklahoma State University)
# All rights reserved.
#

import sys
import os
import numpy as np

import crp_util
import sklearn_helper

#Challenge and response from actual PUF data
DEFAULT_DATA_DIR = "data/crp_c16_r1"
crp_names = crp_util.get_data_filenames(DEFAULT_DATA_DIR)
challenges, responses = [], []
for fname in crp_names:
    print('Using Data from {}'.format(fname))
    data_file = open(fname,newline='')
    cur_chal, cur_resp = crp_util.get_challenge_response_from_csv(data_file)
    challenges+=cur_chal
    responses+=cur_resp
    
# Convert to np arrays
challenges, responses = np.asarray(challenges), np.ravel(responses)

if len(challenges) != len(responses):
    print("Number of challenges does not equal number of responses.")
    sys.exit(1)

# Get training/test dataset split from user.
print("Total CRPs available:", len(challenges))    
size_str = input("Enter percentage for CRPs for training (default 90%): ")
if not size_str :
    training_size = int(len(challenges)*0.9)
else:
    training_size = int(len(challenges)*int(size_str)/100)

# import warnings filter
from warnings import simplefilter
# ignore all future warnings
simplefilter(action='ignore', category=FutureWarning)

# Use sklearn models to attack the data and vary amount of training data to model.
train_data, test_data = sklearn_helper.split_data(training_size, challenges, responses, 123457)    
sklearn_helper.model_accuracy_with_varied_training(train_data, test_data)    
 

