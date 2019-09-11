#!/usr/bin/env python3
# See LICENSE for licensing information.
#
# Copyright (c) 2016-2019 Regents of the University of California and The Board
# of Regents for the Oklahoma Agricultural and Mechanical College
# (acting for and on behalf of Oklahoma State University)
# All rights reserved.
#

import weak_puf_util
    
###############################################################################    
# General Hamming Distance Script
# 1. Calculate Known based on base latent finger prints
# 2. Calculate Hamming distance of known and latent
# 3. Import data with different seeds
# 4. Extract latent fingerprints
# 5. Calculate hamming distance from known fingerprints
# 6. Plot the results with their density    
###############################################################################
    
DEFAULT_INTER_HD_DIR = "data/inter_data_64b"    
DEFAULT_INTRA_HD_DIR = "data/intra_data_64b"    
    
#Calculate known fingerprint
intra_fnames = weak_puf_util.get_data_filenames('intra', DEFAULT_INTRA_HD_DIR)
intra_bits_by_file = weak_puf_util.get_data_bits(intra_fnames)  
intra_bits = [i for list_1d in intra_bits_by_file for i in list_1d] 
known_fp = weak_puf_util.get_known_fingerprint(intra_bits)
print('Known Fingerprint: ', known_fp)
print('Expected Hamming Distance with other devices: ', len(known_fp)//2)

# Collect Hamming distance from intra-data
average_hd_intra, total_intra, hdist_dict_intra, max_hd_intra = weak_puf_util.get_hamming_info(intra_fnames, known_fp)
print('Average intra-Hamming Distance: ', average_hd_intra)    

# Collect Hamming distance from inter-data
inter_fnames = weak_puf_util.get_data_filenames('inter', DEFAULT_INTER_HD_DIR)
average_hd_inter, total_inter, hdist_dict_inter, max_hd_inter = weak_puf_util.get_hamming_info(inter_fnames, known_fp)
print('Average inter-Hamming Distance: ', average_hd_inter)    

# Plot and visualization
range_hd = range(max(max_hd_intra, max_hd_inter))
intra_values = [hdist_dict_intra[i]/total_intra if i in hdist_dict_intra else 0 for i in range_hd]
inter_values = [hdist_dict_inter[i]/total_inter if i in hdist_dict_inter else 0 for i in range_hd]
weak_puf_util.plot_intra_inter_hamming(range_hd, intra_values, inter_values)



   