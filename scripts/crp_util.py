import random
import hashlib
import zlib
import csv

seed = 1
random.seed(seed)


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