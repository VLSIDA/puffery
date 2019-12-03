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
response_size = 4
accesses = 8
address_size = 4
word_size = 8
num_crps = 8000
#challenges = crp_util.gen_challenges(num_crps, challenge_size)
challenges = [crp_util.gen_challenge(challenge_size) for _ in range(num_crps)]
DEBUG_PRINT = False

# Right now, this is required. Can be changed later.
assert(challenge_size>=word_size)

num_gen_response_bits = 2**address_size
sram_words = [crp_util.int_to_bits(random.getrandbits(word_size), word_size) for _ in range(num_gen_response_bits)]

print('SRAM Words:')
for word_bits in sram_words:
    print(crp_util.bits_to_int(word_bits))

#access_range = [1,2,3,4,5,6,7,8]
access_range = [i for i in range(1,accesses+1)]
for total_accesses in access_range:
    print("Generating MAP-{} responses.".format(total_accesses))

    responses = []
    hash_count = [{} for _ in range(total_accesses)]
    prehash_values = [{} for _ in range(total_accesses)]
    x_values = [{} for _ in range(total_accesses)]
    hash_challenges = [{} for _ in range(total_accesses)]
    c_addr_hashes = [[] for _ in range(num_crps)]
        
    c_ind = 0    
    for C in challenges:
        #X = [0 for _ in range(len(C))]
        # X = crp_util.int_to_bits(21845, challenge_size)
        X = crp_util.int_to_bits(1, challenge_size)
        for _ in range(total_accesses):
            if DEBUG_PRINT:
                print('Starting Access {} with challenge {}'.format(_, C))
                print('Current X value {}'.format(X))
            # Hash the challenge and X into the address range
            prehash_value = C+X
            
            if DEBUG_PRINT:
                print('Challenge Combined with X: {}'.format(prehash_value))
            hash_address = crp_util.hash_value_mult_xor(prehash_value, address_size)
            
            if DEBUG_PRINT:
                print('Output address with C+X {}'.format(hash_address))
            
            hash_int = crp_util.bits_to_int(hash_address)
            if hash_int in hash_count[_]:
                hash_count[_][hash_int]+=1
                prehash_values[_][hash_int].append(crp_util.bits_to_int(prehash_value))
                x_values[_][hash_int].append(crp_util.bits_to_int(X))
                hash_challenges[_][hash_int].append(crp_util.bits_to_int(C))
            else:
                hash_count[_][hash_int] = 1
                prehash_values[_][hash_int] = [crp_util.bits_to_int(prehash_value)]
                x_values[_][hash_int] = [crp_util.bits_to_int(X)]
                hash_challenges[_][hash_int] = [crp_util.bits_to_int(C)]
                
            
            # Get word from 'SRAM'
            sram_ind = crp_util.bits_to_int(hash_address)
            c_addr_hashes[c_ind].append(sram_ind)
            s_word = sram_words[sram_ind]
            if DEBUG_PRINT:
                print('Address integer {}'.format(sram_ind))
                print('SRAM word accessed {}'.format(s_word))

            #Combine the word with X, hardcoded to assume 1-bit word_size
            #Implemented as an XOR and shift
            X = [0]*len(s_word)+X[:-len(s_word)]
            for i in range(len(s_word)):
                X[i] = X[i]^s_word[i]   
            # xor_repeat = len(X)/len(s_word)
            # assert(xor_repeat.is_integer())
            # for offset_mult in range(int(xor_repeat)):
                # for i in range(len(s_word)):
                    # offset = i*offset_mult
                    # X[i+offset] = X[i+offset]^s_word[i]
        c_ind+=1    
         
        if DEBUG_PRINT:
            print('')
          
        # Create a response from the challenge and X
        hash_value = C+X
        response = crp_util.hash_value_mult_xor(hash_value, response_size)
        if len(response) > 1:
            response = [response[0]]
        # This is a hack which only works with a 1-bit response
        responses.append(crp_util.bits_to_int(response))  



    # for i in range(len(hash_count)):
        # print("Access", i, "Statistics")
        # for hash_val, count in hash_count[i].items():
            # rate = count/len(challenges)
            # print("val={}, count={}, rate={}%".format(hash_val, count, rate))


    unique_mappings = set()
    for i in range(len(challenges)):
        C = challenges[i]
        addrs = c_addr_hashes[i]
        addr_map_str = str(addrs[0])
        for a in addrs[1:]:
            addr_map_str+="->{}".format(a)
        unique_mappings.add(addr_map_str)
        #print("Challenge {} addresses: {}".format(C, addrs))

    #print("All Unique address mappings: {}".format(unique_mappings))
    print("Total Mappings: {}".format(len(unique_mappings)))

    # access_num, hash_val = 0,5
    # print(hash_challenges[access_num][hash_val])

    # access_num, hash_val = 1,5
    # print(hash_challenges[access_num][hash_val])

    # access_num, hash_val = 3,13
    # print(prehash_values[access_num][hash_val])
    # print(len(prehash_values[access_num][hash_val]))
    # print(len(set(prehash_values[access_num][hash_val])))

    # prehash_values[access_num][hash_val]

    # print(x_values[access_num][hash_val])
    # print(len(x_values[access_num][hash_val]))
    # print(len(set(x_values[access_num][hash_val])))


    # for i in range(len(hash_count)):
        # unique_x = set()
        # access_num = i
        # for hash_value,x_list in x_values[access_num].items():
            # for x in x_list:
                # unique_x.add(x)
        # print("All unique X values at access {}: {}".format(access_num, len(unique_x)))
        # print(unique_x)

    # test_challenges = challenges[:5]

    # for i in range(len(hash_count)):
        
        # access_num = i
        # print("Access {}".format(access_num))
        # for hash_value,x_list in x_values[access_num].items():
            # unique_x = set()
            # for x in x_list:
                # unique_x.add(x)
            
            # # for c in test_challenges:    
                # # list_x = list(unique_x)
                # # prehash = c+crp_util.int_to_bits(list_x[0], bit_len=challenge_size)
                # # h = hash_to_length(prehash, address_size)
                # # print(h)
            # print("All unique X values at hash {}: {}".format(hash_value, len(unique_x)))
            # print(unique_x)
        # print("")
        
    # save the challenge and response to a CSV
    # Initialize first
    file_name = 'puf_map{}.csv'.format(total_accesses)
    csv_file = open(file_name, 'w')
    fields = ('challenge','response')
    csv_writer = csv.writer(csv_file, lineterminator = '\n')
    csv_writer.writerow(fields)

    # Write all the data
    for challenge_bits, response in zip(challenges, responses):
        challenge_str = "".join(map(str, challenge_bits))
        csv_writer.writerow([challenge_str, response])
    csv_file.close() 
    
    print('')
