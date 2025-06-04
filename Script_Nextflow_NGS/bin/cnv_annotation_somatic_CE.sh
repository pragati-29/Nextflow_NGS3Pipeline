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
csv_file=$2

#basemount-cmd refresh "${output_dir}/basespace"

# Load setup
source "$output_dir/setup.sh"

cnv_dir="$output_dir/CNV"
mkdir -p "$cnv_dir"
cd "$cnv_dir" || { echo "Failed to change directory to $cnv_dir"; exit 1; }

# Extract Sample ID (15th column) and Project Name (5th column)
awk -F',' 'BEGIN {OFS=","} NR>1 {print $(NF-2), $4}' "$csv_file" > list.txt

input="list.txt"

while IFS=',' read -r sample_id project_name; do
    echo "Processing Sample: $sample_id, Project: $project_name"

    bam_path="$output_dir/basespace/Projects/$project_name/AppResults/$sample_id/Files/${sample_id}.bam"
    bed_file=$(ls $output_dir/basespace/Projects/${project_name}/AppResults/${sample_id}/Files/*.bed | awk -F/ '!($NF ~ /'${sample_id}'/) { print $0 }')  # Use static BED unless dynamically needed

    echo "BAM path: $bam_path"
    echo "BED file: $bed_file"

    mkdir -p "$sample_id"

    echo "########## Starting config preparation #################"
    perl "$cnv_config" "$bam_path" "$bed_file" $sample_id $chrLenFile $chrFiles $sambamba
    echo "########## Config file prepared #######################"

    echo "########## Starting CNV Control-FREEC ##################"
    "$FREEC_PATH" -conf "${sample_id}/config_CNV.txt"
    echo "########## Finished CNV Control-FREEC ##################"

    echo "########## Starting annotation #########################"
    cd "$sample_id"
    
    cp "$bam_ratio_CE" .
    python3 "$(basename "$bam_ratio_CE")" $bed_file $CE_gene_list

    cd ..

    find "$sample_id" -type f -name "*_R_cnv_combined.txt" -exec mv {} ./ \;

    echo "########## Finished annotation for $sample_id ##########"

done < "$input"

echo "################## ALL FILES ARE DONE ###################"
