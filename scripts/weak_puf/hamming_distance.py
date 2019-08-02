import weak_puf_util

#Challenge and response from actual PUF data
puf_csv = open('data/sram_puf_data_3_16_seed_103.csv',newline='')

# Files contain the Weak PUF bits with the same devices under different conditions 
# but the same transistor variations per file marked by the seed in the file name. 
device_bits = weak_puf_util.get_weak_puf_bits(puf_csv)
print(device_bits)


# General Hamming Distance Script
# 1. Calculate Known based on base latent finger prints
# 2. Calculate Hamming distance of known and latent
# 3. Import data with different seeds
# 4. Extract latent fingerprints
# 5. Calculate hamming distance from known fingerprints
# 6. Plot the results with their density

# Calculate Known fingerprint
known_fp = weak_puf_util.get_known_fingerprint(device_bits)
print('Known Fingerprint: ', known_fp)

# Calculate hamming distances
hammings = weak_puf_util.compare_known_and_latent_fps(known_fp, device_bits)
print('Hamming Distances with main device: ', hammings)

# Expected Hamming Distance against other devices
print('Expected Hamming Distance with other devices: ', len(known_fp)//2)

# Get latent fingerprint of SRAM PUF with different variations
# FIXME: Add attomated method of collecting data for comparison. Currently hardcoded.
device_seeds = [104, 105, 106, 107, 108, 109]
secondary_pufs_files = 'data/sram_puf_data_3_16_seed_{}.csv'
secondary_bits = []
for seed in device_seeds:
    csv_data = open('data/sram_puf_data_3_16_seed_{}.csv'.format(seed),newline='')
    secondary_bits.append(weak_puf_util.get_weak_puf_bits(csv_data))
    
# Get Hamming distances from these devices
average_hd = 0
total = 0
for latent_fps, seed in zip(secondary_bits, device_seeds):
    hammings = weak_puf_util.compare_known_and_latent_fps(known_fp, latent_fps)
    print('Hamming Distances with seed ', seed,': ', hammings)
    average_hd+=sum(hammings)
    total+=1
    
average_hd/=total
print('Average Hamming Distance: ', average_hd)    

# TODO: plot and visualization