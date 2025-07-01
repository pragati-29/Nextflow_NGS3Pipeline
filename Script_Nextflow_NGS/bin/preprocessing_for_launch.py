#!/usr/bin/env python3

# Import necessary libraries
import pandas as pd
import csv
import re
import argparse
from datetime import datetime

# Define the main function to process the input CSV and generate an output CSV
def process_file(input_file, output_file):
    # Get the current date in the format dd_MMM_yy
    current_date = datetime.now().strftime("%d_%b_%y")

    # Mapping of capturing kit names to their corresponding bed IDs
    bed_id_mapping = {
        "GE": 32335159063,
        "CE": 25985869859,
        "SE8": 23683257154,
        "FEV2F2both": 34857530934,
        "CDS": 31946210817,
        "CEFu": 32246847276
    }

    # CNV baseline IDs 
    cnv_baseline = (
        "cnv-baseline-id:26595964844,26596768352,26596768352,26597000441,"
        "26596302077,26596768331,26596296009,26596677367,26596984439,"
        "26596440110,26596089873,26596890400,26596199853,26595963870,"
        "26597226773,26596302095,26597235779,26596296030,26595984910,"
        "26595972945,26596669273,26596477171,26596089892,26595984889,"
        "26596677388,26596477187,26596861347,26596268048,26596565254,"
        "26596669289,26596247018,26595984929,26596477204,26596302112,"
        "26596199870,26596302128,26596477221,26595972961,26596302145,"
        "26595984953,26595991950,26595972980,26596199887,26596049977,"
        "26596565272,26596669311,26609829389,26596565288,26596302164"
    )
    baseline_noise = "baseline-noise-bed:26693875133"

    # CNV baseline and noise bed IDs for SE8 
    cnv_baseline_se8 = (
        "cnv-baseline-id:25791243964,25791291016,25791291033,25791291050,"
        "25791406163,25791440084,25791528878,25791528895,25791582119,"
        "25791582931,25791595964,25791595981,25791598767,25791637964,"
        "25791670919,25791679146,25791679164,25791681916,25791681933"
    )
    baseline_noise_se8 = "baseline-noise-bed:25849773923"

    # Read the input CSV into a DataFrame
    df = pd.read_csv(input_file)

    # Compile regex patterns to identify "-B", "-BB", "-F", "-FF" sample ID suffixes
    pattern_B = re.compile(r"-B[0-9]+|-BB[0-9]+|-B[0-9]+|-B", re.IGNORECASE)
    pattern_F = re.compile(r"-F[0-9]+|-FF[0-9]+|-F[0-9]+|-F", re.IGNORECASE)

    # Map capturing kit to bed ID
    df["bed_id"] = df["Capturing_Kit"].map(bed_id_mapping)

    # Identify liquid tumor samples based on presence of "-cf-" in the sample ID
    df["liquid_tumor"] = df["Sample_ID"].apply(lambda x: 1 if "-cf-" in x.lower() else 0)

    # Determine variant calling type: 0 for germline, 1 for somatic
    df["vc_type"] = df["Sample_ID"].apply(lambda x: 0 if pattern_B.search(x) and "cf" not in x else 1)

    # Classify as somatic, germline, or unknown based on patterns in Sample_ID
    df["Somatic_Germline"] = df["Sample_ID"].apply(
        lambda x: "germline" if pattern_B.search(x) and "cf" not in x else (
            "somatic" if pattern_F.search(x) or "cf" in x else "unknown"
        )
    )

    # Create a descriptive appsession name with date and metadata
    df["appsession_name"] = df.apply(
        lambda row: f"{current_date}_{row['Test_Name']}_{row['Sample_Type']}_{row['Capturing_Kit']}_{row['Somatic_Germline']}",
        axis=1
    )

    # Set AF call threshold: 1% for cfDNA, 5% otherwise
    df["vc-af-call-threshold"] = df["Sample_ID"].apply(lambda x: 1 if "-cf-" in x else 5)

    # Set AF filter threshold: 5% for cfDNA, 10% otherwise
    df["vc-af-filter-threshold"] = df["Sample_ID"].apply(lambda x: 5 if "-cf-" in x else 10)

    # Assign CNV baseline ID conditionally based on test name, kit, and somatic/germline type
    df["cnv_baseline_Id"] = df.apply(
        lambda row: cnv_baseline if (
            "INDIEGENE" in row["Test_Name"].upper() and
            row["Capturing_Kit"] in ["CE", "CEFu"] and
            row["Somatic_Germline"] in ["somatic", "germline"]
        ) else (
            cnv_baseline_se8 if (
                "ABSOLUTE" in row["Test_Name"].upper() and
                row["Capturing_Kit"] == "SE8" and
                row["Somatic_Germline"] in ["somatic", "germline"]
            ) else None
        ),
        axis=1
    )

    # Assign baseline noise bed similarly, but only for somatic cases
    df["baseline-noise-bed"] = df.apply(
        lambda row: baseline_noise if (
            "INDIEGENE" in row["Test_Name"].upper() and
            row["Capturing_Kit"] in ["CE", "CEFu"] and
            row["Somatic_Germline"] == "somatic"
        ) else (
            baseline_noise_se8 if (
                "ABSOLUTE" in row["Test_Name"].upper() and
                row["Capturing_Kit"] == "SE8" and
                row["Somatic_Germline"] == "somatic"
            ) else None
        ),
        axis=1
    )

    # Save the processed DataFrame to the output CSV
    df.to_csv(output_file, index=False)

# Define argument parsing for CLI usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process input CSV file and generate output CSV file.")
    parser.add_argument("input_file", help="Path to input CSV file")
    parser.add_argument("output_file", help="Path to output CSV file")
    args = parser.parse_args()

    # Run the processing function with user-provided arguments
    process_file(args.input_file, args.output_file)
