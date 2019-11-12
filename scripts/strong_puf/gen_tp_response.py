#!/usr/bin/env python3
# See LICENSE for licensing information.
#
# Copyright (c) 2016-2019 Regents of the University of California and The Board
# of Regents for the Oklahoma Agricultural and Mechanical College
# (acting for and on behalf of Oklahoma State University)
# All rights reserved.
#

import crp_util
import random
import csv
import math
import sys

random.seed(1)

# Get challenges, let say they are randomly generated using the random bit values thing
# There can be duplicated challenges with this method
challenge_size = 16
response_size = 1
accesses = 4
address_size = 4
word_size = 2
num_crps = 1000
challenges = [crp_util.gen_challenge(challenge_size) for _ in range(num_crps)]

# Right now, this is required. Can be changed later.
assert(response_size == 1)
assert(challenge_size>=word_size)

num_gen_response_bits = 2**address_size
sram_words = [crp_util.int_to_bits(random.getrandbits(word_size), word_size) for _ in range(num_gen_response_bits)]
responses = []

for C in challenges:
    X = [0 for i in range(len(C))]
    for _ in range(accesses):
        # Hash the challenge and X into the address range
        hash_value = C+X
        repeat_hash_float = math.log2(len(hash_value)/address_size)
        assert(repeat_hash_float.is_integer())
        repeat_hash = int(repeat_hash_float)
        hash_address = crp_util.hash_value(hash_value, repeat_hash)
        
        # Get word from 'SRAM'
        sram_ind = crp_util.bits_to_int(hash_address)
        s_word = sram_words[sram_ind]

        # Combine the word with X, hardcoded to assume 1-bit word_size
        # Implemented as an XOR and shift
        X = [0]*len(s_word)+X[:-len(s_word)]
        for i in range(len(s_word)):
            X[i] = X[i]^s_word[i]    
      
    # Create a response from the challenge and X
    hash_value = C+X
    repeat_hash_float = math.log2(len(hash_value)/response_size)
    assert(repeat_hash_float.is_integer())
    repeat_hash = int(repeat_hash_float)
    response = crp_util.hash_value(hash_value, repeat_hash)

    # This is a hack which only works with a 1-bit response
    responses.append(crp_util.bits_to_int(response))  

# save the challenge and response to a CSV
# Initialize first
file_name = 'puf_tp_hash{}_c{}_r{}.csv'.format(address_size, challenge_size,response_size)
csv_file = open(file_name, 'w')
fields = ('challenge','response')
csv_writer = csv.writer(csv_file, lineterminator = '\n')
csv_writer.writerow(fields)

# Write all the data
for challenge_bits, response in zip(challenges, responses):
    challenge_str = "".join(map(str, challenge_bits))
    csv_writer.writerow([challenge_str, response])
csv_file.close() 
