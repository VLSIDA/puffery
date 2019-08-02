import random
import hashlib
import zlib
import csv
import sys

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
    