#!/usr/bin/env bash

# Exit on error and undefined variables
set -euo pipefail

# Ensure correct number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <output_dir> <csv_file>"
    exit 1
fi

# Assign input arguments to variables
output_dir=$1
echo "$output_dir"
csv_file=$2
echo "$csv_file"

# Load setup
source "$output_dir/setup.sh"
echo "$Ambiliz"
echo "$chrLenFile"
echo "$chrFiles"

cnv_dir="$output_dir/cnv_FeV2"

echo "Location: $output_dir"
echo "Directory: $cnv_dir"
echo "Sample file: $csv_file"

mkdir -p "$cnv_dir"

# Extract only TARGET_FIRST samples with Sample ID and Project Name
awk -F',' 'BEGIN {OFS=","} NR > 1 && $1 == "TARGET_FIRST" {print $(NF-2), $4}' "$csv_file" > "$cnv_dir/list.txt"

input="$cnv_dir/list.txt"
cd "$cnv_dir" || { echo "Failed to change directory to $cnv_dir"; exit 1; }

# Check if there are any TARGET_FIRST samples
if [ ! -s "$input" ]; then
    echo "No TARGET_FIRST samples found. Exiting."
    exit 0
fi

# Loop through each TARGET_FIRST sample
while IFS=',' read -r sample_id project_name; do
    echo "Processing Sample: $sample_id, Project: $project_name"
    
    bam_path="$output_dir/basespace/Projects/${project_name}/AppResults/${sample_id}/Files/${sample_id}.bam"
    bed_file=$(ls "$output_dir/basespace/Projects/${project_name}/AppResults/${sample_id}/Files/"*.bed | awk -F/ '!($NF ~ /'"${sample_id}"'/) { print $0 }')
    echo "bed file: $bed_file"
    echo "BAM path: $bam_path"
   
    mkdir -p "$sample_id"

    echo "########## Starting config preparation #################"
    perl "$cnv_config" "$bam_path" "$bed_file" "$sample_id" "$chrLenFile" "$chrFiles" "$sambamba"
    echo "########## Config file prepared #######################"

    echo "########## Starting CNV Control-FREEC ##################"
    "$FREEC_PATH" -conf "${sample_id}/config_CNV.txt"
    echo "########## Finished CNV Control-FREEC ##################"

    echo "########## Starting annotation #########################"
    cd "$sample_id"

    cp "$python_bam_ratio" .
    python3 "$(basename "$python_bam_ratio")" "$bed_file"

    mkdir -p MS_Cov
    cp "$Ambiliz" .
    echo "Running AmpliZ_cov_V3.py with args: $sample_id $output_dir/basespace/Projects/$project_name"
    python3 "$(basename "$Ambiliz")" "$sample_id" "$output_dir/basespace/Projects/$project_name" "$Ambiliz_folder"

    cd ..

    # Copy final CNV results to main directory
    find "$sample_id" -type f -name "*_stat_cntf_cnv_combined.txt" -exec cp {} ./ \;

    echo "########## Finished annotation for $sample_id ##########"
done < "$input"

echo "################## ALL FILES ARE DONE ###################"

