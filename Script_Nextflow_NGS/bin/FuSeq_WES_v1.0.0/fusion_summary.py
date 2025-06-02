# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 01:15:35 2023

@author: Bhumika
@Validation & Modification: Naavarasi,Vyomesh,Yukti
"""

import os
import re
import glob
import pandas as pd

# get a list of all files in the pwd
file_list = glob.glob("*")

# loop through the list and read each file that ends with "_SR_fge.txt"
for file in file_list:
    if file.endswith("_SR_fge.txt"):
        SR_fge = pd.read_csv(file, delimiter="\t")
        
#filter genes based on names
fus_genes = ['ALK', 'ROS1', 'RET', 'MET','NTRK1','NTRK2','NTRK3','NRG1','NRG2','FGFR1','FGFR2','FGFR3']
panel_fus_gene_df = SR_fge[SR_fge['fusionName'].str.contains('|'.join(fus_genes))]
print ("Filtered Fusions based on Genes")

#filter genes having read-support >= 1        
rs_1 = panel_fus_gene_df[panel_fus_gene_df['supportRead'] >= 1].copy()
print ("Filtered Fusions with rs>=1")

#read the bedpe file in the current working directory
bedpe = pd.read_csv('splitReadInfo.bedpe', sep='\t')

#read the splitreadinfo fiile in the current working directory
split_read_info = 'splitReadInfo.txt'
split_read = pd.read_csv(split_read_info, sep="\t", header=None, usecols=[0, 4, 9], names=["ReadName", "Gene1", "Gene2"])

#read the backend db csv file in the current working directory
backend_db = pd.read_csv("/home/bioinfo/Nilesh/NGS3_test/Nextflow_Downstream/Script_Nextflow_NGS/bin/FuSeq_WES_v1.0.0/Exon_Intron_all_Region_FuSEQ.csv")

# Split the name column in bedpe file by "--" and put the two parts in separate columns
bedpe[['name_split1', 'name_split2']] = bedpe['name'].str.split('--', n=1, expand=True)

# Loop over the specified fus_genes
filtered_data = pd.DataFrame()  # initialize an empty DataFrame
for fus_gene in fus_genes:
    # filter the rows based on the name_split1 and name_split2 column if the specified fus_genes present and based on read_support >= 3
    filtered_data_fus_genes = bedpe[((bedpe['name_split1'] == fus_gene) | (bedpe['name_split2'] == fus_gene)) & (bedpe['score'] >= 1)]

    # append the filtered data to the new DataFrame
    filtered_data = pd.concat([filtered_data, filtered_data_fus_genes])

# Drop duplicates based on the 'name', 'chr1', 'start1', and 'end1' columns in bedpe
unique_data_bedpe = filtered_data.drop_duplicates(subset=['name', 'chrom1', 'start1', 'end1', 'chrom2', 'start2', 'end2', 'score'])

# Create an empty DataFrame to store only the required results from bedpe
bedpe_updated = pd.DataFrame(columns=['chrom1', 'start1', 'end1', 'gene1', 'chrom2', 'start2', 'end2', 'gene2', 'Fusion', 'Fusion_name','Score/Read support'])

# Iterate over the unique_data_bedpe rows
for index, row in unique_data_bedpe.iterrows():
    # Split the name into two parts
    name_split = row['name'].split('--')
    name_split1 = name_split[0]
    name_split2 = name_split[1] if len(name_split) > 1 else None
    
    # Check if name_split1 has any of the specified fus_genes
    if any(x in name_split1 for x in fus_genes):
        # Add the corresponding chrom, start, and end to the new_df 
        new_row = {'chrom1': row['chrom1'], 'start1': row['start1'], 'end1': row['end1'], 'gene1': name_split1, 'chrom2': row['chrom2'], 'start2': row['start2'], 'end2': row['end2'], 'gene2': name_split2, 'Fusion': "NA", 'Fusion_name': row['name'], 'Score/Read support': row['score']}
        new_row_df = pd.DataFrame([new_row])  # Create a DataFrame from the dictionary
        bedpe_updated = pd.concat([bedpe_updated, new_row_df], ignore_index=True)
    
    # Check if name_split2 has any of the specified fus_genes
    if name_split2 and any(x in name_split2 for x in fus_genes):
        # Add the corresponding chrom, start, and end to the new_df
        new_row = {'chrom1': row['chrom2'], 'start1': row['start2'], 'end1': row['end2'], 'gene1': name_split2, 'chrom2': row['chrom1'], 'start2': row['start1'], 'end2': row['end1'], 'gene2': name_split1, 'Fusion': row['name'], 'Fusion_name': "NA", 'Score/Read support': row['score']}
        new_row_df = pd.DataFrame([new_row])  
        bedpe_updated = pd.concat([bedpe_updated, new_row_df], ignore_index=True)
        
#--------------------------------------------------------------------------------
        
#map filtered_bed.pe file with fge file
map_bedpe_updated_fge = pd.DataFrame()
for index, row in bedpe_updated.iterrows():
    match_count = 0  # Counter variable to track the number of matches
    for index1, row1 in rs_1.iterrows():
        if row["Fusion_name"] == row1["fusionName"]:
            new_column = {"chrom1": row["chrom1"], "start1": row["start1"], "end1": row["end1"], "gene1": row["gene1"], "strand1":row1["strand1"], "chrom2": row["chrom2"], "start2": row["start2"], "end2": row["end2"], "gene2": row["gene2"], "strand2":row1["strand2"], "Fusion_name": row["Fusion_name"], "Fusion": row["Fusion"], "supportRead": row['Score/Read support'], "Read_name": row1['header']}
            new_column_df = pd.DataFrame([new_column])  # Create a DataFrame from the dictionary
            map_bedpe_updated_fge = pd.concat([map_bedpe_updated_fge, new_column_df], ignore_index=True)
            match_count += 1
            
        elif row["Fusion"] == row1["fusionName"]:
            new_column = {"chrom1": row["chrom1"], "start1": row["start1"], "end1": row["end1"], "gene1": row["gene1"], "strand1":row1["strand2"], "chrom2": row["chrom2"], "start2": row["start2"], "end2": row["end2"], "gene2": row["gene2"], "strand2":row1["strand1"], "Fusion_name": row["Fusion_name"], "Fusion": row["Fusion"], "supportRead": row['Score/Read support'], "Read_name": row1['header']}
            new_column_df = pd.DataFrame([new_column])  # Create a DataFrame from the dictionary
            map_bedpe_updated_fge = pd.concat([map_bedpe_updated_fge, new_column_df], ignore_index=True)
            match_count += 1

    # If match count is more than 1, create a new row
    if match_count > 1:
        new_column = {"chrom1": row["chrom1"], "start1": row["start1"], "end1": row["end1"], "gene1": row["gene1"], "chrom2": row["chrom2"], "start2": row["start2"], "end2": row["end2"], "gene2": row["gene2"], "Fusion_name": row["Fusion_name"], "Fusion": row["Fusion"], "supportRead": row['Score/Read support'], "Read_name": row1['header']}
        new_column_df = pd.DataFrame([new_column])  # Create a DataFrame from the dictionary
        map_bedpe_updated_fge = pd.concat([map_bedpe_updated_fge, new_column_df], ignore_index=True)
        
#--------------------------------------------------------------------------------


# Create an empty DataFrame to store the final results
map_with_backend_db = pd.DataFrame(columns=['#FusionGene', 'ReadSupport', 'LeftBreakpoint', 'gene1', 'strand1', 'RightBreakpoint', 'gene2', 'strand2', 'ReadNames', 'Fusion', 'Exon_Num', 'Exon_Cat'])

#mapping with backend-database from mapped bedpe and fge file to backend_db
for index, row in map_bedpe_updated_fge.iterrows():
    for index1, row1 in backend_db.iterrows():
        if row["gene1"] == row1["Gene"]:
            # Check if the chromosome is the same in both the files
            if row['chrom1'] == row1['Chrom']:
                # Check if the start or end location in bedpe file is within the range of locations in backend database
                if (row1['Exon_Start'] >= row['end1'] >= row1['Exon_End']) or (row1['Exon_Start'] <= row['end1'] <= row1['Exon_End']):
                    if row['Fusion'] == "NA":
                        new_row = {'#FusionGene': row['Fusion_name'], 'ReadSupport': row['supportRead'], 'LeftBreakpoint': f"{row['chrom1']}:{row['end1']}", 'gene1': row['gene1'], "strand1":row["strand1"], 'RightBreakpoint': f"{row['chrom2']}:{row['start2']}", 'gene2': row['gene2'] , "strand2":row["strand2"], 'ReadNames': row['Read_name'], 'Fusion': row['Fusion'], 'Exon_Num': row1['Exon_Num'],'Exon_Cat': row1['Exon_Cat']}
                        new_row_df = pd.DataFrame([new_row])  # Create a DataFrame from the dictionary
                        map_with_backend_db = pd.concat([map_with_backend_db, new_row_df], ignore_index=True)
                    else:
                        new_row = {'#FusionGene': row['Fusion'],'ReadSupport': row['supportRead'], 'LeftBreakpoint': f"{row['chrom2']}:{row['end2']}", 'gene1': row['gene2'], "strand1":row["strand2"], 'RightBreakpoint': f"{row['chrom1']}:{row['start1']}", 'gene2': row['gene1'] , "strand2":row["strand1"], 'ReadNames': row['Read_name'], 'Fusion': row['Fusion'], 'Exon_Num': row1['Exon_Num'],'Exon_Cat': row1['Exon_Cat']}
                        new_row_df = pd.DataFrame([new_row])  # Create a DataFrame from the dictionary
                        map_with_backend_db = pd.concat([map_with_backend_db, new_row_df], ignore_index=True)
                else:
                    pass
                
#----------------------------EXONIC FILTER----------------------------------------------------

# Group by the specified columns and concatenate values in Exon_Cat and Exon_Num columns
df_merged = map_with_backend_db.groupby(['#FusionGene', 'ReadSupport', 'LeftBreakpoint', 'gene1', "strand1", 'RightBreakpoint', 'gene2', "strand2", 'ReadNames', 'Fusion']).agg({'Exon_Cat': lambda x: ', '.join(x.astype(str)),'Exon_Num': lambda x: ', '.join(x.astype(str))}).reset_index()

# Create an empty DataFrame to store the filtered exon rows
filtered_exons = pd.DataFrame(columns=df_merged.columns)

# Filter the DataFrame based on the exon conditions
for index, row in df_merged.iterrows():
    fusiongene = row['#FusionGene']
    exon_cat = row['Exon_Cat']
    
    if 'ALK' in fusiongene:
        if any(x in exon_cat for x in ['18', '19', '20', '21']):
            row_df = pd.DataFrame([row])  # Create a DataFrame from the row
            filtered_exons = pd.concat([filtered_exons, row_df], ignore_index=True)
    elif 'RET' in fusiongene:
        if any(x in exon_cat for x in ['2','3','4','5','6','7','8','9','10', '11', '12']):
            row_df = pd.DataFrame([row])  
            filtered_exons = pd.concat([filtered_exons, row_df], ignore_index=True)
    elif 'MET' in fusiongene:
        if any(x in exon_cat for x in ['13','14','15']):
            row_df = pd.DataFrame([row])  
    elif 'ROS1' in fusiongene:
        if any(x in exon_cat for x in ['30', '31', '32', '33', '34', '35','36','37']):
            row_df = pd.DataFrame([row])  
            filtered_exons = pd.concat([filtered_exons, row_df], ignore_index=True)
    elif 'NTRK1' in fusiongene:
        if any(x in exon_cat for x in ['2','3','4','5','6','7','8','9','10', '11', '12', '13']):
            row_df = pd.DataFrame([row])  
            filtered_exons = pd.concat([filtered_exons, row_df], ignore_index=True)
    elif 'NTRK2' in fusiongene:
        if any(x in exon_cat for x in ['9','10','14','15','16']):
            row_df = pd.DataFrame([row])  
            filtered_exons = pd.concat([filtered_exons, row_df], ignore_index=True)
    elif 'NTRK3' in fusiongene:
        if any(x in exon_cat for x in ['3','4','5','12','13','14','15']):
            row_df = pd.DataFrame([row])  
            filtered_exons = pd.concat([filtered_exons, row_df], ignore_index=True)
    elif 'FGFR1' in fusiongene:
        if any(x in exon_cat for x in ['7','14','17']):
            row_df = pd.DataFrame([row])  
            filtered_exons = pd.concat([filtered_exons, row_df], ignore_index=True)
    elif 'FGFR2' in fusiongene:
        if any(x in exon_cat for x in ['15','16','17','18']):
            row_df = pd.DataFrame([row])  # Create a DataFrame from the row
            filtered_exons = pd.concat([filtered_exons, row_df], ignore_index=True)
    elif 'FGFR3' in fusiongene:
        if any(x in exon_cat for x in ['14','15','16','17','18']):
            row_df = pd.DataFrame([row])  
            filtered_exons = pd.concat([filtered_exons, row_df], ignore_index=True)
    elif 'NRG1' in fusiongene:
        if any(x in exon_cat for x in ['1','2','3','4','5','6','7']):
            row_df = pd.DataFrame([row])  
            filtered_exons = pd.concat([filtered_exons, row_df], ignore_index=True)
    elif 'NRG2' in fusiongene:
        if any(x in exon_cat for x in ['1','2','3','4','5','6','7']):
            row_df = pd.DataFrame([row])  
            filtered_exons = pd.concat([filtered_exons, row_df], ignore_index=True)      
    else:
        # Append the other remaining rows except for ALK, RET, and ROS1
        row_df = pd.DataFrame([row])  
        filtered_exons = pd.concat([filtered_exons, row_df], ignore_index=True)
print ("Filtered fusions as per design")

#------------------------------TAGGING ON KNOWN FUSIONS--------------------------------------------------

known_Fusions = pd.read_csv("/home/bioinfo/Nilesh/NGS3_test/Nextflow_Downstream/Script_Nextflow_NGS/bin/FuSeq_WES_v1.0.0/known_Fusions.csv")

# Storing formats to be sent to the reporting team
final_df_exons = pd.DataFrame(columns=['#FusionGene', 'ReadSupport', 'LeftBreakpoint', 'strand1', 'RightBreakpoint', 'strand2', 'ReadNames', 'Exons', 'FusionStatus'])

for index, row in filtered_exons.iterrows():
    fusion_matched = False  # Flag to check if a match is found
    
    for index1, row1 in known_Fusions.iterrows():
        known_fusion_parts = row1["KnownFusions"].split('--')
        known_fusion_reversed = '--'.join(known_fusion_parts[::-1])
        
        if row["#FusionGene"] == row1["KnownFusions"] or row["#FusionGene"] == known_fusion_reversed:
            new_row2 = {'#FusionGene': row['#FusionGene'], 'ReadSupport': row['ReadSupport'], 'LeftBreakpoint': row['LeftBreakpoint'], "strand1":row["strand1"], 'RightBreakpoint': row['RightBreakpoint'], "strand2":row["strand2"], 'ReadNames': row['ReadNames'], 'Exons': row['Exon_Cat'],'FusionStatus': 'KnownFusions'}
            final_df_exons = final_df_exons.append(new_row2, ignore_index=True)
            
            fusion_matched = True  # Setting the flag to True to indicate a match
            break  # Break out of the inner loop
    
    # Adding rows to final_df_exons for the case where no match was found
    if not fusion_matched:
        new_row2 = {'#FusionGene': row['#FusionGene'],'ReadSupport': row['ReadSupport'],'LeftBreakpoint': row['LeftBreakpoint'], "strand1":row["strand1"], 'RightBreakpoint': row['RightBreakpoint'], "strand2":row["strand2"], 'ReadNames': row['ReadNames'], 'Exons':row['Exon_Cat'], 'FusionStatus': 'Unknown'}
        final_df_exons = final_df_exons.append(new_row2, ignore_index=True)
        
#--------------------------------------------------------------------------------

# Function to remove trailing ".0" only if there are more than one trailing zeros
def remove_trailing_zeros(value):
    if value.endswith('.0'):
        value = value.rstrip('0').rstrip('.')
    return value

final_df_exons['LeftBreakpoint'] = final_df_exons['LeftBreakpoint'].apply(remove_trailing_zeros)
final_df_exons['RightBreakpoint'] = final_df_exons['RightBreakpoint'].apply(remove_trailing_zeros)

# Step 1: Filter for fusions with ReadSupport >= 3
updated_final_df_exons = final_df_exons[final_df_exons["ReadSupport"] >= 3].copy()

# Step 2: Combine fusions with both orientations
fusion_dict = {}
for index, row in final_df_exons.iterrows():
    # Normalize fusion name (consistent order of gene1 and gene2)
    gene1, gene2 = row["#FusionGene"].split("--")
    fusion_key = f"{min(gene1, gene2)}--{max(gene1, gene2)}"
    
    if fusion_key in fusion_dict:
        # Merge ReadSupport
        fusion_dict[fusion_key]["ReadSupport"] += row["ReadSupport"]
    else:
        # Add new fusion entry
        fusion_dict[fusion_key] = row.to_dict()
# Step 2: Fetch ReadNames from the split_read file
def retrieve_read_names(fusion_key):
    gene1, gene2 = fusion_key.split("--")
    matching_reads = split_read[
        ((split_read["Gene1"] == gene1) & (split_read["Gene2"] == gene2)) |
        ((split_read["Gene1"] == gene2) & (split_read["Gene2"] == gene1))
    ]
    return ",".join(sorted(matching_reads["ReadName"].astype(str).tolist()))

for fusion_key in fusion_dict:
    fusion_dict[fusion_key]["ReadNames"] = retrieve_read_names(fusion_key)

# Step 3: Convert the merged fusions back to a DataFrame
updated_fusions = pd.DataFrame.from_dict(fusion_dict, orient="index")

# Step 4: Ensure all columns are retained
missing_columns = set(final_df_exons.columns) - set(updated_fusions.columns)
for col in missing_columns:
    updated_fusions[col] = None  # Fill missing columns with None or placeholder values

# Step 5: Remove duplicates in updated_final_df_exons and prepare the final output
updated_final_df_exons = updated_fusions.reset_index(drop=True)

# Filter final_df_exons where FusionStatus is 'KnownFusions'
final_df_known = updated_final_df_exons[updated_final_df_exons['FusionStatus'] == 'KnownFusions'].copy()

# Apply the function to 'LeftBreakpoint' and 'RightBreakpoint'
updated_final_df_exons['LeftBreakpoint'] = updated_final_df_exons['LeftBreakpoint'].apply(remove_trailing_zeros)
updated_final_df_exons['RightBreakpoint'] = updated_final_df_exons['RightBreakpoint'].apply(remove_trailing_zeros)

final_df_known['LeftBreakpoint'] = final_df_known['LeftBreakpoint'].apply(remove_trailing_zeros)
final_df_known['RightBreakpoint'] = final_df_known['RightBreakpoint'].apply(remove_trailing_zeros)   

#--------------------------------------------------------------------------------
#getting current working directory
path = os.getcwd()

# Extract the sample_id from the working directory
file_name = os.path.splitext(os.path.basename(path))[0]

# Extract the desired string using regular expressions
desired_string = re.search(r'(.+?)_fusions', file_name).group(1)

##########################  adding sample_id to the fuseq-output.xlsx file  #################################
#inserting Sample_ID column to the final output
updated_final_df_exons.insert(0, 'Sample_ID', '')

#inserting the sample_ID to the respective fusions
updated_final_df_exons['Sample_ID'] = desired_string

# Adding Sample_ID column to the final output
final_df_known.insert(0, 'Sample_ID', '')

# Inserting the sample_ID to the respective fusions
final_df_known['Sample_ID'] = desired_string

print ("Filtered KnownFusions")
##########################  sample adding done  #################################
#final_df_exons.to_excel(f'{desired_string}_fusion_output.xlsx', index = False)
updated_final_df_exons.to_excel(f'{desired_string}_fge_DNA_FUS_Exons_P.xlsx', index=False)

# Output for reporting team
final_df_known.to_excel(f'{desired_string}_fge_DNA_FUS_Known_P.xlsx', index=False)

#########################FUS_P################
final_df = final_df_known.drop(columns=['Sample_ID', 'strand1', 'strand2', 'Exons', 'FusionStatus'])
final_df.to_excel(f'{desired_string}_FUS_P.xlsx', index=False)
print ("DONE")
##########################DONE############################################
