import shutil
import glob
import os

# Array to store sample file names
samples = []

# Read file line by line and extract sample names
with open("/media/bioinfoa/bioinfo2/Pragati/Lung_annotation/200_sam_ids_new.txt", "r") as file:
    for line in file:
        # Split the line at '-' and take the first part as the sample name
        sample_name = line.split('-')[0].strip()
        samples.append(sample_name)
#print(samples)
# Source folder path
source_folder = "/media/bioinfoa/bioinfo2/Pragati/Lung_annotation/Multianno_lung/FE_merged"

# Destination folder path
destination_folder = "/media/bioinfoa/bioinfo2/Pragati/Lung_annotation/200_merged_file"
# Copy files based on sample names using glob for wildcard matching
for sample in samples:
    '''try:
        file_path = os.path.join(destination_folder, sample)
        os.remove(file_path)
    except:
        FileNotFoundError'''
    files_to_copy = glob.glob(f"{source_folder}/{sample}*")
    for file_path in files_to_copy:
        shutil.copy(file_path, destination_folder)
  
