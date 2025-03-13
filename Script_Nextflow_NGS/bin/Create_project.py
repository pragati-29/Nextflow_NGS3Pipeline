#!/usr/bin/env python3
import pandas as pd
import subprocess
import argparse
from datetime import datetime

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Create a project and update CSV file.")
parser.add_argument("--sample_file", required=True, help="Path to the input CSV file.")
parser.add_argument("--project_name", required=True, help="Project name to assign.")
parser.add_argument("--output_file", default="created_proj.csv", help="Path to save the updated CSV (default: created_proj.csv).")

args = parser.parse_args()

# Load CSV file
file = pd.read_csv(args.sample_file)

# Assign project name
project_names = args.project_name

if file["Project_name"].isna().any() or (file["Project_name"] == "").any():
    subprocess.run(["bs", "create", "project", "-n", project_names], check=True)
    file["Project_name"] = project_names
    file.to_csv(args.output_file, index=False)
