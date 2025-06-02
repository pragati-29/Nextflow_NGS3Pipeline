#!/usr/bin/env bash

# Exit on error and undefined variables
set -euo pipefail

# Ensure correct number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <location> <csv_file>"
    exit 1
fi

# Assign input arguments to variables
location=$1
echo "$location"
csv_file=$2
echo "$csv_file"

# Load setup
source "$location/setup.sh"
echo "$Ambiliz"
echo "$chrLenFile"

cnv_dir="$location/cnv"

echo "Location: $location"
echo "Directory: $cnv_dir"
echo "Sample file: $csv_file"

# Create directory if it doesn't exist
mkdir -p "$cnv_dir"
#basemount-cmd refresh "${location}/basespace"

# Extract Sample ID (15th column) and Project Name (5th column)
awk -F',' 'BEGIN {OFS=","} {if (NR>1) print $(NF-2),$4}' "$csv_file" > "$cnv_dir/list.txt"

input="$cnv_dir/list.txt"
cd "$cnv_dir" || { echo "Failed to change directory to $cnv_dir"; exit 1; }

# Loop through each line in the extracted list
while IFS=',' read -r sample_id project_name; do
    echo "Processing Sample: $sample_id, Project: $project_name"
    
    bam_path="$location/basespace/Projects/${project_name}/AppResults/${sample_id}/Files/${sample_id}.bam"
    bed_file=$(ls $location/basespace/Projects/${project_name}/AppResults/${sample_id}/Files/*.bed | awk -F/ '!($NF ~ /'${sample_id}'/) { print $0 }')
    echo "bed file: $bed_file"

    echo "BAM path: $bam_path"
   
    mkdir -p "$sample_id"

    echo "########## Starting config preparation #################"
    perl "$cnv_config" "$bam_path" "$bed_file" $sample_id $chrLenFile $chrFiles $sambamba
    echo "########## Config file prepared #######################"

    echo "########## Starting CNV Control-FREEC ##################"
    "$FREEC_PATH" -conf "${sample_id}/config_CNV.txt"
    echo "########## Finished CNV Control-FREEC ##################"

    echo "########## Starting annotation #########################"
    cd "$sample_id"

    cp "$python_bam_ratio" .
    python3 "$(basename "$python_bam_ratio")" $bed_file

    mkdir -p MS_Cov
    cp "$Ambiliz" .
    echo "Running AmpliZ_cov_V3.py with args: $sample_id $location/basespace/Projects/$project_name"
    python3 "$(basename "$Ambiliz")" "$sample_id" "$location/basespace/Projects/$project_name" "$Ambiliz_folder"

    cd ..

    # Copy final CNV results to main directory
    find "$sample_id" -type f -name "*_stat_cntf_cnv_combined.txt" -exec cp {} ./ \;

    echo "########## Finished annotation for $sample_id ##########"
done < "$input"

echo "################## ALL FILES ARE DONE ###################"

