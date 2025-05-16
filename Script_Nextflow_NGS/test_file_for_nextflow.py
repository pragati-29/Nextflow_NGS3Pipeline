import pandas as pd
import os
import re

columns = [
    "Test_Name", "Sample_Type", "Capturing_Kit", "Project_name", "file_name", 
    "Project_ID", "Biosample_ID", "appsession_name", "bed_id", "liquid_tumor", 
    "vc-af-call-threshold", "vc-af-filter-threshold", "cnv_baseline_Id", "baseline-noise-bed"
]

current_directory = os.path.dirname(os.path.abspath(__file__))
print(current_directory)
files = [f for f in os.listdir(current_directory) if f.endswith('.fastq.gz')]

df = pd.DataFrame(columns=columns)
df["file_name"] = [i.split("_")[0] if "-" in i else re.split(r"_R[12]", i)[0] for i in files]
df.loc[df["file_name"].str.contains(r"(?i)([_-]|^)GE([_-]|$)", na=False), "Capturing_Kit"] = "GE"
df.loc[df["file_name"].str.contains(r"(?i)([_-]|^)FEV2F2both([_-]|$)", na=False), "Capturing_Kit"] = "FEV2F2both"
df.loc[df["file_name"].str.contains(r"(?i)([_-]|^)SE8([_-]|$)", na=False), "Capturing_Kit"] = "SE8"
df.loc[df["file_name"].str.contains(r"(?i)([_-]|^)CE([_-]|$)", na=False), "Capturing_Kit"] = "CE"
df.loc[~df["file_name"].str.contains(r"(?i)[_-]CT[_-]|[_-]ST8[_-]", na=False), "Sample_Type"] = "DNA"

# Fill Test_Name
df.loc[df["Capturing_Kit"] == "GE", "Test_Name"] = "163panel"
df.loc[df["Capturing_Kit"] == "FEV2F2both", "Test_Name"] = "TARGET_FIRST"
df.loc[df["Capturing_Kit"].isin(["CE"]), "Test_Name"] = "INDIEGENE"
df.loc[df["Capturing_Kit"].isin(["SE8"]), "Test_Name"] = "ABSOLUTE"
df.drop_duplicates(subset=["file_name"], keep="first", inplace=True)
output_file_path = os.path.join(current_directory, "test_ngs3_nextflow_Copy_try.csv")
df.to_csv(output_file_path,index=False)
