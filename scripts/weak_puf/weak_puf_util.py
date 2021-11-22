#!/usr/bin/env python3
# See LICENSE for licensing information.
#
# Copyright (c) 2019-2021, VLSI Design & Automation Group
# All rights reserved.
#

import random
import hashlib
import zlib
import csv
import sys
import matplotlib.pyplot as plt
import os

seed = 1
random.seed(seed)

def bit_str_to_int_list(bit_str):
    #Does not check that all values are either 1 or 0
    return [int(bit_char) for bit_char in bit_str]
  
def get_weak_puf_bits(csv_file):
    bits = []
    
    reader = csv.DictReader(csv_file)
    for row in reader:
        bits.append(bit_str_to_int_list(row['bits']))
    return bits

def get_known_fingerprint(latent_fingerprints):
    
    if not latent_fingerprints or len(latent_fingerprints)==0:
        return []
        
    known_fp = [0 for _ in range(len(latent_fingerprints[0]))]
    
    # Element wise sum of latent fingerprints
    for fingerprint in latent_fingerprints:
        for pos in range(len(fingerprint)):
            known_fp[pos]+=fingerprint[pos]
    
    # Average by number of latent fingerprints and round.
    # Round function: > .5 -> 1 and <= .5 -> 0
    for pos in range(len(known_fp)):
        known_fp[pos] = int(round(known_fp[pos]/len(latent_fingerprints)))
    
    return known_fp
    
def compare_known_and_latent_fps(known_fingerprint, latent_fingerprints):
    
    hamming_dists = []
    for latent_fp in latent_fingerprints:
        hamming_dists.append(get_hamming_distance(known_fingerprint, latent_fp))
        
    return hamming_dists
    
def get_hamming_distance(fingerprint_a, fingerprint_b):
    """Assuming input bit lists, returns hamming distance between the two"""
    
    # It might be more efficient to have the values stored as ints then just
    # count the bits after the XOR
    assert(len(fingerprint_a) == len(fingerprint_b))
    
    ham_dist = 0
    for bit_a, bit_b in zip(fingerprint_a, fingerprint_b):
        bit_dist = bit_a^bit_b
        if bit_dist > 1:
            print('Hamming distance bits must be binary.')
            sys.exit(1)
        ham_dist+=bit_dist
    
    return ham_dist
    
def get_data_filenames(type_str, default_val):
    # Get latent fingerprint of SRAM PUF with different variations
    data_dir = input("Enter data directory for {}-Hamming distance (Default: {}): ".format(type_str, default_val))
    if not data_dir:
        data_dir = default_val
        print('Using default data:', data_dir)   
    if not os.path.isdir(data_dir):
        print('Directory ',data_dir,' not found. Exiting...')
        sys.exit(1)
    bare_fnames = os.listdir(data_dir)
    return ["{}/{}".format(data_dir, fname) for fname in bare_fnames]
    
def get_data_bits(data_file_names):
    bits = []
    for csv_fname in data_file_names:
        csv_data = open(csv_fname,newline='')
        bits.append(get_weak_puf_bits(csv_data))
    # Returns double list    
    return bits
    
def get_hamming_info(data_file_names, known_fp):
    bits = get_data_bits(data_file_names)

    # Get Hamming distances from these devices
    average_hd = 0
    total = 0
    hdist_dict = {}
    max_hd = 0

    for latent_fps, csv_fname in zip(bits, data_file_names):
        hammings = compare_known_and_latent_fps(known_fp, latent_fps)
        print('Hamming Distances from', csv_fname,': ', hammings)
        average_hd+=sum(hammings)
        total+=len(hammings)
        max_hd = max(max_hd, max(hammings))
        
        # Add increment hamming distance counters
        for hd in hammings:
            if hd not in hdist_dict:
                hdist_dict[hd] = 0
            hdist_dict[hd]+=1
    average_hd/=total            
    return average_hd, total, hdist_dict, max_hd    
    
def plot_intra_inter_hamming(x_hdist, y_intra, y_inter):    
    
    #plt.style.use('ggplot')

    plt.bar(x_hdist, y_inter, color='red')
    plt.bar(x_hdist, y_intra, color='blue')
    plt.xlabel("Hamming Distance")
    plt.ylabel("Probability")

    #plt.xticks(x_pos, x)

    plt.show()    