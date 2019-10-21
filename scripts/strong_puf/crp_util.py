#!/usr/bin/env python3
# See LICENSE for licensing information.
#
# Copyright (c) 2016-2019 Regents of the University of California and The Board
# of Regents for the Oklahoma Agricultural and Mechanical College
# (acting for and on behalf of Oklahoma State University)
# All rights reserved.
#

import random
import hashlib
import zlib
import csv
import os

seed = 1
random.seed(seed)


def append_inverted_challenge(challenge):
    """Given input challenge list, adds inverted challenge as an additional feature"""
    
    inverted_challenge = []
    for cbit in challenge:
        if cbit == 0:
            inverted_challenge.append(1)
        elif cbit == 1:
            inverted_challenge.append(0)
        else:
            print("Challenge bit is non-binary: c_bit = {}".format(cbit))
            assert(False)
            
    return challenge+inverted_challenge
    
def gen_byte_str(byte_len, byte_range=[33,126]):
    bytes = []
    for i in range(byte_len):
        bytes.append(random.randint(*byte_range))
    char_bytes = ''.join(map(chr, bytes))
    return char_bytes.encode()

def gen_bytes(num_bytes):
    bytes = []
    rand_byte_int = random.getrandbits(8)
    for i in range(num_bytes):
        rand_byte_int = random.getrandbits(8)
        bytes.append(rand_byte_int.to_bytes(1, 'big'))
    return b''.join(bytes)    
    
def gen_challenge(num_bits):
    rand_bits = random.getrandbits(num_bits)
    return int_to_bits(rand_bits, num_bits)  
    
def bits_to_bytes(bit_list):
    if len(bit_list)%8 != 0:
        print('Bit lengths must be a multiple of 8')
        return None
    byte_int = int(''.join(map(str, bit_list)), 2) 
    return byte_int.to_bytes(len(bit_list)//8, 'big') 
    
def bytes_to_bits(bytes):
    int_val = int.from_bytes(bytes, 'big')
    return int_to_bits(int_val, len(bytes)*8)

def bits_to_int(bits):
    # Given a list of bits (0/1), convert to an int
    # Assumes the first item in the list is the least significant bit
    sum = 0
    for i in range(len(bits)):
        if bits[i]:
            sum += 2**i
    return sum
    
def int_to_bits(val, bit_len=None):
    if bit_len != None:
        bin_str = format(val, '0{}b'.format(bit_len))
    else: 
        bin_str = format(val, '0b')
    return [int(bit) for bit in bin_str]
    
def gen_hash_response(challenge_bits):
    # bits -> bytes -> hashed bytes -> bits
    chal_bytes = bits_to_bytes(challenge_bits)
    crc_int = zlib.crc32(chal_bytes)
    return int_to_bits(crc_int, 32) 
    
def get_simulated_challenge_response_pairs(num_pairs, num_chal_bits):
    #response bits are currently fixed
    challenges = []
    responses = []
    for _ in range(num_pairs):
        challenges.append(gen_challenge(num_chal_bits))
        responses.append(gen_hash_response(challenges[-1]))
    return challenges,responses
  
def get_challenge_response_from_csv(csv_file):
    challenges = []
    responses = []
    
    reader = csv.DictReader(csv_file)
    for row in reader:
        challenges.append(bit_str_to_int_list(row['challenge']))
        responses.append(bit_str_to_int_list(row['response']))
    return challenges,responses
    
def bit_str_to_int_list(bit_str):
    #Does not check that all values are either 1 or 0
    return [int(bit_char) for bit_char in bit_str]
 
def round_predictions(pred_probs, round_point=.5):
    #Given array of prediction probabilities [0,1]. Rounds them to 0 or 1
    #Anything above .5 is 1 while below is 0
    decisions = []
    for pred in pred_probs:
        if pred >= round_point:
            decisions.append(1)
        else:
            decisions.append(0)
    return decisions         
    
def get_accuracy(prediction, label):
    #Both assumed to be rounded to 1 or 0.
    correct = 0
    for label_bit, pred_bit in zip(prediction, label):
        if label_bit == pred_bit:
            correct+=1
    return correct/len(label)
    
def get_data_filenames(default_dir):
    inter_dir = input("Enter directory path for CRPs (Default:{}): ".format(default_dir))
    if not inter_dir:
        inter_dir = default_dir
        print('Using default data:', inter_dir)
    data_dir = 'data/{}'.format(inter_dir)    
    if not os.path.isdir(inter_dir):
        print('Directory ',inter_dir,' not found. Exiting...')
        sys.exit(1)
    bare_fnames = os.listdir(inter_dir)
    return ["{}/{}".format(inter_dir, fname) for fname in bare_fnames]    
    
def hash_value(bit_list):
    """Given an input, this function will hash the value down to a specific bit length"""
    
    #This function only works if challenge size=16, output size=4
    assert(len(bit_list)%2==0)
    # Assume the 16 challenge length, generalize later
    # Reduce the list twice
    
    reduced_list = []
    for _ in range(2):
        half_point = len(bit_list)//2
        first_half = bit_list[:half_point]
        second_half = bit_list[half_point:]
        
        reduced_list = []
        for bit_left,bit_right in zip(first_half, second_half):
            reduced_list.append(bit_left^bit_right)
            
        bit_list = reduced_list
    
    return bit_list    
    
def hash_value_to_8bit(bit_list):
    """Given an input, this function will hash the value down to a specific bit length"""
    
    #This function only works if challenge size=16, output size=8
    assert(len(bit_list)%2==0)
    # Assume the 16 challenge length, generalize later
    # Reduce the list twice
    
    half_point = len(bit_list)//2
    first_half = bit_list[:half_point]
    second_half = bit_list[half_point:]
    
    reduced_list = []
    for bit_left,bit_right in zip(first_half, second_half):
        reduced_list.append(bit_left^bit_right)
        
    bit_list = reduced_list
    
    return bit_list      