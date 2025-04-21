#!/usr/bin/env bash

# Check for correct number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <location> <csv_file>"
    exit 1
fi

location=$1
csv_file=$2
fusion_dir="$location/fusion"

# Create working directory
mkdir -p "$fusion_dir"

# Extract Sample IDs into a list
awk -F',' 'BEGIN {OFS=","} {if (NR>1) print $(NF-2)}' "$csv_file" > "$fusion_dir/list.txt"

input="$fusion_dir/list.txt"
cd "$fusion_dir" || exit 1

# Loop over each sample
while IFS= read -r line; do
    echo ">------BEDTOOLS INTERSECTION STARTING FOR SAMPLE ${line}------->"

    bam_path="$location/basespace/Projects/create_project_test1/AppResults/${line}/Files/${line}.bam"
    intersected_bam="${line}_intersected.bam"

    # Intersect BAM with known fusions
    intersectBed -abam "$bam_path" \
        -b "/home/bioinfoa/Pragati/FuSeq_WES_v1.0.0/knowngeneFusions.bed" -f 1 > "$intersected_bam"

    samtools index "$intersected_bam"
    echo ">-----${intersected_bam} CREATED------<"

    echo "Starting ${line}"

    bamfile="$fusion_dir/${intersected_bam}"
    ref_json="/home/bioinfoa/Pragati/FuSeq_WES_v1.0.0/UCSC_hg19_wes_contigSize3000_bigLen130000_r100/UCSC_hg19_wes_contigSize3000_bigLen130000_r100.json"
    gtfSqlite="/home/bioinfoa/Pragati/FuSeq_WES_v1.0.0/UCSC_hg19_wes_contigSize3000_bigLen130000_r100/UCSC_hg19_wes_contigSize3000_bigLen130000_r100.sqlite"

    output_dir="${line}_fusions"
    mkdir "$output_dir"

    # Step 1: Extract mapped and split reads
    python3 "/home/bioinfoa/Pragati/FuSeq_WES_v1.0.0/fuseq_wes.py" \
        --bam "$bamfile" --gtf "$ref_json" --mapq-filter --outdir "$output_dir"

    # Step 2: Process reads with R
    fusiondbFn="/home/bioinfoa/Pragati/FuSeq_WES_v1.0.0/Data/Mitelman_fusiondb.RData"
    paralogdbFn="/home/bioinfoa/Pragati/FuSeq_WES_v1.0.0/Data/ensmbl_paralogs_grch37.RData"

    Rscript "/home/bioinfoa/Pragati/FuSeq_WES_v1.0.0/process_fuseq_wes.R" \
        in="$output_dir" sqlite="$gtfSqlite" fusiondb="$fusiondbFn" paralogdb="$paralogdbFn" out="$output_dir"

    Rscript "/home/bioinfoa/Pragati/FuSeq_WES_v1.0.0/bedpeconvert.R" "$output_dir"

    # Rename output files
    for f in FuSeq_WES_FusionFinal.txt FuSeq_WES_SR_fge_fdb.txt FuSeq_WES_SR_fge.txt \
             FuSeq_WES_MR_fge.txt FuSeq_WES_MR_fge_fdb.txt feq_ALL.txt; do
        mv "$output_dir/$f" "$output_dir/${line}-${f}" 2>/dev/null
    done

    # Step 3: Generate .fus summary
    Fusion_FUS="/home/bioinfoa/Pragati/FuSeq_WES_v1.0.0/"
    Fusion_Folder="$fusion_dir/$output_dir"

    cp "$Fusion_FUS/fusion_summary.py" "$Fusion_Folder"
    cp "$Fusion_FUS/Exon_Intron_all_Region_FuSEQ.csv" "$Fusion_Folder"
    chmod 777 "$Fusion_Folder/fusion_summary.py"

    echo "########### Generating FUS file ##########"
    (cd "$Fusion_Folder" && python3 fusion_summary.py)
    echo "########### Fus file generated ###########"

    echo "Ending ${line}"
done < "$input"

echo "########## ALL FILES DONE ############"

