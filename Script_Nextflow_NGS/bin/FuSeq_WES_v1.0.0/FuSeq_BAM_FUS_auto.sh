#!/usr/bin/env bash

# Check for correct number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <output_dir> <csv_file>"
    exit 1
fi

output_dir=$1
csv_file=$2
fusion_dir="$output_dir/fusion"
source "$output_dir/setup.sh"
# Create working directory
mkdir -p "$fusion_dir"

# Extract Sample IDs into a list
#awk -F',' 'BEGIN {OFS=","} {if (NR>1) print $(NF-2)}' "$csv_file" > "$fusion_dir/list.txt"
#awk -F',' 'NR>1 {print $15","$4}' "$csv_file" > "$fusion_dir/list.txt"
cp "$fuseq/list_test.txt" $fusion_dir
input="$fusion_dir/list_test.txt"
cd "$fusion_dir" || exit 1
echo "$output_dir"
# Loop over each sample
while IFS=',' read -r line project; do
    echo ">------BEDTOOLS INTERSECTION STARTING FOR SAMPLE ${line}------->"
    echo "$output_dir"
    bam_path="$output_dir/basespace/Projects/${project}/AppResults/${line}/Files/${line}.bam"
    intersected_bam="${line}_intersected.bam"

    # Intersect BAM with known fusions
    intersectBed -abam "$bam_path" \
        -b "$fuseq/knowngeneFusions.bed" -f 1 > "$intersected_bam"

    samtools index "$intersected_bam"
    echo ">-----${intersected_bam} CREATED------<"

    echo "Starting ${line}"

    bamfile="$fusion_dir/${intersected_bam}"
    ref_json="$fuseq/UCSC_hg19_wes_contigSize3000_bigLen130000_r100/UCSC_hg19_wes_contigSize3000_bigLen130000_r100.json"
    gtfSqlite="$fuseq/UCSC_hg19_wes_contigSize3000_bigLen130000_r100/UCSC_hg19_wes_contigSize3000_bigLen130000_r100.sqlite"

    sample_output_dir="${line}_fusions"
    mkdir "$sample_output_dir"

    # Step 1: Extract mapped and split reads
    python3 "$fuseq/fuseq_wes.py" --bam "$bamfile" --gtf "$ref_json" --mapq-filter --outdir "$sample_output_dir"

    # Step 2: Process reads with R
    fusiondbFn="$fuseq/Data/Mitelman_fusiondb.RData"
    paralogdbFn="$fuseq/Data/ensmbl_paralogs_grch37.RData"

    Rscript "$fuseq/process_fuseq_wes.R" "$fuseq" in="$sample_output_dir" sqlite="$gtfSqlite" fusiondb="$fusiondbFn" paralogdb="$paralogdbFn" out="$sample_output_dir"

    Rscript "$fuseq/bedpeconvert.R" "$sample_output_dir"

    # Rename output files
    for f in FuSeq_WES_FusionFinal.txt FuSeq_WES_SR_fge_fdb.txt FuSeq_WES_SR_fge.txt \
             FuSeq_WES_MR_fge.txt FuSeq_WES_MR_fge_fdb.txt feq_ALL.txt; do
        mv "$sample_output_dir/$f" "$sample_output_dir/${line}-${f}" 2>/dev/null
    done

    # Step 3: Generate .fus summary
    Fusion_FUS="$fuseq/"
    Fusion_Folder="$fusion_dir/$sample_output_dir"

    cp "$Fusion_FUS/fusion_summary.py" "$Fusion_Folder"
    cp "$Fusion_FUS/Exon_Intron_all_Region_FuSEQ.csv" "$Fusion_Folder"
    chmod 777 "$Fusion_Folder/fusion_summary.py"

    echo "########### Generating FUS file ##########"
    (cd "$Fusion_Folder" && python3 fusion_summary.py --fuseq "$fuseq")
    echo "########### Fus file generated ###########"

    echo "Ending ${line}"
done < "$input"

echo "########## ALL FILES DONE ############"
