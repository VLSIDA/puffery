#!/usr/bin/env python3
# See LICENSE for licensing information.
#
# Copyright (c) 2016-2019 Regents of the University of California and The Board
# of Regents for the Oklahoma Agricultural and Mechanical College
# (acting for and on behalf of Oklahoma State University)
# All rights reserved.
#

import sklearn_helper
import csv
import sys

if len(sys.argv < 2):
    print("Data file must be provided")
    sys.exit()
read_file_name = sys.argv[1]

if len(sys.argv < 3):
    append_file_name = 'new_data.csv'
else:
    append_file_name = sys.argv[2]

# Take in first input file and compute average accuracies of the data
csv_file = open(file_name, 'r')

csv_reader = csv.reader(csv_file, delimiter=',')
line_count = 0

x_examples = []
y_accuracies = {}
y_average = []
for row in csv_reader:
    if line_count == 0:
        model_names = row[1:]
        num_models = len(model_names)
        y_accuracies = {name:[] for name in model_names}
    else:
        x_examples.append(int(row[0]))
        sum = 0
        for i in range(1, len(row)):
            accuracy = float(row[i])
            sum+=accuracy
            y_accuracies[model_names[i-1]].append(float(row[i]))
        y_average.append(sum/num_models)
        
    line_count+=1        

y_avg_dict = {'Average Accuracy':y_average}
#y_accuracies['Average Accuracy'] = y_average
sklearn_helper.display_data(x_examples, y_avg_dict)

#sklearn_helper.display_data(x_examples, y_accuracies)

# Next take that data and place it into a different csv which
# is either created if not specified or appended









