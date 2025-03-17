#!/usr/bin/env python3
import pandas as pd
import subprocess
import argparse
import re

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Create projects based on CSV file.")
parser.add_argument("--sample_file", required=True, help="Path to the input CSV file.")
parser.add_argument("--output_file", default="created_proj.csv", help="Path to save the updated CSV.")  # Fix output filename
args = parser.parse_args()

# Load CSV file
file = pd.read_csv(args.sample_file)

# Ensure 'Project_name' column exists
if 'Project_name' not in file.columns:
    print("Error: 'Project_name' column not found in CSV.")
    exit(1)

# Get project names from CSV (drop empty rows, convert to string, and strip spaces)
project_names = set(file["Project_name"].dropna().astype(str).str.strip())

# Get existing projects from 'bs project list'
try:
    result = subprocess.run(["bs", "project", "list"], capture_output=True, text=True, check=True)
    raw_output = result.stdout.splitlines()
    
    # Extract project names using regex (skip table headers)
    existing_projects = set()
    for line in raw_output:
        match = re.match(r"^\|\s*([^\|]+?)\s*\|", line)  # Extract project name from table
        if match:
            existing_projects.add(match.group(1).strip())  # Clean up spaces
            
    print(f"Existing projects: {existing_projects}")  # Debugging output
except subprocess.CalledProcessError as e:
    print(f"Error fetching existing projects: {e}")
    existing_projects = set()

# Track created projects
created_projects = []

# Iterate over project names and create only if missing
for project_name in project_names:
    if project_name in existing_projects:
        print(f"Skipping '{project_name}', already exists.")
    else:
        print(f"Creating project '{project_name}'...")
        try:
            subprocess.run(["bs", "create", "project", "-n", project_name], check=True)
            created_projects.append(project_name)  # Store successfully created projects
            existing_projects.add(project_name)  # Update existing projects
        except subprocess.CalledProcessError as e:
            print(f"Error creating project '{project_name}': {e}")
            continue  # Skip this project and move to the next

# Save updated CSV file
file.to_csv(args.output_file, index=False)
print(f"Updated CSV saved as {args.output_file}")

# Log created projects
if created_projects:
    print(f"Successfully created projects: {', '.join(created_projects)}")
else:
    print("No new projects were created.")
