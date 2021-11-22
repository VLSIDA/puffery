#!/usr/bin/env python3
# See LICENSE for licensing information.
#
# Copyright (c) 2019-2021, VLSI Design & Automation Group
# All rights reserved.
#

#########################################################################
#
# gen_puf_sram_hash.py - Python simulated data of a SRAM PUF which hashes the 
# challenge to select an address in the SRAM.
#
#########################################################################


import crp_util
import random
import csv
import sys

random.seed(1)

def universal_hash(message, key, w_size):
    
    if w_size == 0:
        print("w partitions must be non-zero")
        sys.exit(1) 

    if len(message) != len(key):
        print("Key and message must be the same length")
        sys.exit(1)
    
    if len(message)%2 or len(key)%2:
        print("Key and message must have an even length.")
        sys.exit(1)
        
    if len(message)%w_size or len(key)%w_size:
        print("Key and message must be divisible by w")
        sys.exit(1)    

    

#Challenge and response from the arbiter strong PUF
DEFAULT_DATA_DIR = "data/crp_c16_r1"
crp_names = crp_util.get_data_filenames(DEFAULT_DATA_DIR)
challenges, responses = [], []
for fname in crp_names:
    print('Using Data from {}'.format(fname))
    data_file = open(fname,newline='')
    cur_chal, cur_resp = crp_util.get_challenge_response_from_csv(data_file)
    challenges+=cur_chal
    responses+=cur_resp

print(challenges)
print(responses)

# This challenge becomes the input to the hash function
hash_challenges = [crp_util.hash_value_to_8bit(c)for c in challenges]

if len(challenges) == 0:
    print('Challenges not found!')
    sys.exit(1)
# Assuming all challenges have the same length    
challenge_size = len(challenges[0])

# We only expect the data to be 1-bit response, confirm that
if len(responses) == 0:
    print('Responses not found!')
    sys.exit(1)
    
if len(responses[0]) != 1:
    print('Expected PUF data to have a 1-bit output.')
    sys.exit(1)    
  
#Convert 2d list to 1d, again, assuming all bits responses are consistent length
arbiter_responses = [r_bit for resp in responses for r_bit in resp]  

print(responses)
# Now, Create faux SRAM startup values with the assumption that they are random
address_size = 8
startup_values = [round(random.random()) for _ in range(2**address_size)]    
print(startup_values)    

# Now the actual response will be based on this value and the arbiter.
# The rule will be used: if arbiter value is 0, then use the sram value
# if its 1, then invert the value.
responses = []
response_size = 1
for i in range(len(challenges)):
    hash_challenge = crp_util.hash_value_to_8bit(challenges[i])
    sram_address = crp_util.bits_to_int(hash_challenge)
    print(sram_address)
    sram_output = startup_values[sram_address]
    if sram_output == 0:
        sram_output_bar = 1
    else:
        sram_output_bar = 0
    
    if arbiter_responses[i] == 0:
        responses.append(sram_output)
    else:
        responses.append(sram_output_bar)

# save the challenge and response to a CSV
# Initialize first
file_name = 'puf_sram_hash_c{}_r{}.csv'.format(challenge_size,response_size)
csv_file = open(file_name, 'w')
fields = ('challenge','response')
csv_writer = csv.writer(csv_file, lineterminator = '\n')
csv_writer.writerow(fields)

# Write all the data
for challenge_bits, response in zip(challenges, responses):
    challenge_str = "".join(map(str, challenge_bits))
    csv_writer.writerow([challenge_str, response])
csv_file.close() 
