#!/usr/bin/env python3
# See LICENSE for licensing information.
#
# Copyright (c) 2019-2021, VLSI Design & Automation Group
# All rights reserved.
#

# Simulates Data from a strong SRAM PUF which uses hashing and indirection
# to select a word in the SRAM as a response

import crp_util
import random
import csv
import math

random.seed(1)

# Get challenges, let say they are randomly generated using the random bit values thing
# There can be duplicated challenges with this method
challenge_size = 16
address_size = 4
word_size = address_size 
num_crps = 8000
challenges = [crp_util.gen_challenge(challenge_size) for _ in range(num_crps)]

# This challenge becomes the input to the hash function
repeat_hash_float = math.log2(challenge_size/address_size)
assert(repeat_hash_float.is_integer())
repeat_hash = int(repeat_hash_float)
hash_challenges = [crp_util.hash_value(c, repeat_hash)for c in challenges]

# Generates a n-bit hashed values, n-randomly generated values have been generated
# Use the n-bit hash as a selection (1 bit response)
response_size = 1
num_gen_response_bits = 2**address_size
sram_words = [crp_util.int_to_bits(random.getrandbits(word_size), word_size) for _ in range(num_gen_response_bits)]

responses = []
for hash_chal in hash_challenges:
    
    # Use the hashed challenge to access the sram
    sram_ind = crp_util.bits_to_int(hash_chal)
    s_word_access_one = sram_words[sram_ind]
    
    # Use the first access to address SRAM
    sram_ind = crp_util.bits_to_int(s_word_access_one)
    s_word_access_two = sram_words[sram_ind]
    
    # PUF analysis can only handle 1 output bit, shortened to that here
    responses.append(s_word_access_two[0])

# save the challenge and response to a CSV
# Initialize first
file_name = 'puf_hash{}_c{}_r{}.csv'.format(address_size, challenge_size,response_size)
csv_file = open(file_name, 'w')
fields = ('challenge','response')
csv_writer = csv.writer(csv_file, lineterminator = '\n')
csv_writer.writerow(fields)

# Write all the data
for challenge_bits, response in zip(challenges, responses):
    challenge_str = "".join(map(str, challenge_bits))
    csv_writer.writerow([challenge_str, response])
csv_file.close() 
