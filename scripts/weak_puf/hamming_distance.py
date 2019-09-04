import os
import sys
import weak_puf_util

def get_data_filenames(type_str, default_val):
    # Get latent fingerprint of SRAM PUF with different variations
    inter_dir = input("Enter data directory for {}-Hamming distance (Leave blank for default 64b): ".format(type_str))
    if not inter_dir:
        inter_dir = default_val
        print('Using default data:', inter_dir)
    data_dir = 'data/{}'.format(inter_dir)    
    if not os.path.isdir(data_dir):
        print('Directory ',data_dir,' not found. Exiting...')
        sys.exit(1)
    bare_fnames = os.listdir(data_dir)
    return ["{}/{}".format(data_dir, fname) for fname in bare_fnames]
    
def get_data_bits(data_file_names):
    bits = []
    for csv_fname in data_file_names:
        csv_data = open(csv_fname,newline='')
        bits.append(weak_puf_util.get_weak_puf_bits(csv_data))
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
        hammings = weak_puf_util.compare_known_and_latent_fps(known_fp, latent_fps)
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
    
###############################################################################    
# General Hamming Distance Script
# 1. Calculate Known based on base latent finger prints
# 2. Calculate Hamming distance of known and latent
# 3. Import data with different seeds
# 4. Extract latent fingerprints
# 5. Calculate hamming distance from known fingerprints
# 6. Plot the results with their density    
###############################################################################
    
DEFAULT_INTER_HD_DIR = "inter_data_64b"    
DEFAULT_INTRA_HD_DIR = "intra_data_64b"    
    
#Calculate known fingerprint
intra_fnames = get_data_filenames('intra', DEFAULT_INTRA_HD_DIR)
intra_bits_by_file = get_data_bits(intra_fnames)  
intra_bits = [i for list_1d in intra_bits_by_file for i in list_1d] 
known_fp = weak_puf_util.get_known_fingerprint(intra_bits)
print('Known Fingerprint: ', known_fp)
print('Expected Hamming Distance with other devices: ', len(known_fp)//2)

# Collect Hamming distance from intra-data
average_hd_intra, total_intra, hdist_dict_intra, max_hd_intra = get_hamming_info(intra_fnames, known_fp)
print('Average intra-Hamming Distance: ', average_hd_intra)    

# Collect Hamming distance from inter-data
inter_fnames = get_data_filenames('inter', DEFAULT_INTER_HD_DIR)
average_hd_inter, total_inter, hdist_dict_inter, max_hd_inter = get_hamming_info(inter_fnames, known_fp)
print('Average inter-Hamming Distance: ', average_hd_inter)    


# Plot and visualization
range_hd = range(max(max_hd_intra, max_hd_inter))
intra_values = [hdist_dict_intra[i]/total_intra if i in hdist_dict_intra else 0 for i in range_hd]
inter_values = [hdist_dict_inter[i]/total_inter if i in hdist_dict_inter else 0 for i in range_hd]

import matplotlib.pyplot as plt

plt.style.use('ggplot')

plt.bar(range_hd, inter_values, color='red')
plt.bar(range_hd, intra_values, color='blue')
plt.xlabel("Hamming Distance")
plt.ylabel("Probability")

#plt.xticks(x_pos, x)

plt.show()


   