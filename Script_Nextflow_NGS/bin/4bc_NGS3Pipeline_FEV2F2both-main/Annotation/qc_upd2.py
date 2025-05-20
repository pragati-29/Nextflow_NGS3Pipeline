import os
import pandas as pd
import sys

def qc_metrics_dna_25(location):
    # Create QC folder
    os.makedirs(location + '/QC_Updated', exist_ok=True)
    os.system("chmod 777 " + location + '/QC_Updated')
    # Copy the metrics file to the QC folder
    os.system('cp ' + location + '/metrics.csv' + ' ' + location + '/QC_Updated')
    qcdf = pd.DataFrame(columns=['Sample Name', "Sequence_length", "Total_Sequences"], dtype=object)
    metrics = pd.read_csv(location + '/QC_Updated/metrics.csv', header=0)
    if metrics.columns[0] == 'Sample Name':
        # Change it to Sample ID
        metrics.rename(columns={metrics.columns[0]: 'Sample ID'}, inplace=True)
    qcdf['Sample Name'] = metrics['Sample ID']
    qcdf['Total_Sequences'] = metrics['Total PF read 1']
    qcdf['Sequence_length'] = metrics['Padding size']
    qcdf['Percent duplicate aligned reads'] = metrics['Percent duplicate aligned reads']
    qcdf['Percent Target coverage at 50X'] = metrics['Percent Target coverage at 50X']
    qcdf['Mean target coverage depth'] = metrics['Mean target coverage depth']
    qcdf['Uniformity of coverage (Pct > 0.2*mean)'] = metrics['Uniformity of coverage (Pct > 0.2*mean)']
    qcdf['Unique base enrichment'] = metrics['Unique base enrichment']
    qcdf['Unique read enrichment'] = metrics['Unique read enrichment']
    qcdf['Fragment length median'] = metrics['Fragment length median']
    qcdf['Percent Q30 bases'] = metrics['Percent Q30 bases']
    qcdf['Total_size'] = 2 * qcdf['Sequence_length'] * qcdf['Total_Sequences'].div(1e9)
    qcdf['QC_status'] = "Pass"
    """
    1] Fragment Length Median: < 100 - Low, b/w 100 - 110 - borderline
    2] duplicates: 40-50 - duplicates ~ 40, >= 50 - high duplicates
    3] Percent Target coverage at 50X: 85 - 90 - borderline, < 85 - Low
    4] Mean target coverage depth: for SE8 --- < 50 - Low, For others --- < 100
    """

    comments = []
    for i, j, k, l, m, n in zip(list(qcdf['Fragment length median']), list(qcdf['Percent duplicate aligned reads']),
                             list(qcdf['Sample Name']), list(qcdf['Mean target coverage depth']),
                             list(qcdf['Uniformity of coverage (Pct > 0.2*mean)']), list(qcdf['Percent Target coverage at 50X'])):
        comment = ""
        if i < 100:
            comment += "Low Fragment Length Median, "
        if i in range(100, 111):
            comment += "Fragment Length Median on borderline, "
        if j > 50:
            comment += "High duplicates, "
        if 40 <= j <= 50:
            comment += "duplicates~40, "
        #if k < 60:
            #comment += "Low Unique base enrichment, "
        # differing thresholds for SE8 and others
        if "-SE8-" in k:
            if l < 50:
                comment += "Low Mean target coverage depth, "
        elif l < 100:
            comment += "Low Mean target coverage depth, "
        if m < 85:
            comment += "Low Uniformity of coverage, "
        if n < 85:
            comment += "Low Percent Target coverage at 50X, "
        if n in range(85, 91):
            comment += "Percent Target coverage at 50X on borderline, "
        if comment == "":
            comment = " "
        comments.append(comment.strip())
    qcdf['Comments'] = comments
    header = ["Sample Name", "Total_Sequences", "Percent duplicate aligned reads", "Percent Target coverage at 50X",
              "Mean target coverage depth","Uniformity of coverage (Pct > 0.2*mean)",
              "Unique base enrichment", 'Unique read enrichment', "Fragment length median","Percent Q30 bases", "Total_size",
              "QC_status", "Comments","RNA_Total_input_reads","RNA_PCT_DUP_AR","RNA_Insert_length_median","RNA_TargetCoverage","RNA_Total_size"]
    # add the RNA columns and fill them with NA
    qcdf['RNA_Total_input_reads'] = "NA"
    qcdf['RNA_PCT_DUP_AR'] = "NA"
    qcdf['RNA_Insert_length_median'] = "NA"
    qcdf['RNA_TargetCoverage'] = "NA"
    qcdf['RNA_Total_size'] = "NA"

    qcdf.to_csv(location + '/QC_Updated/output_updated.csv', columns=header)

    return location + 'output_updated.csv'

path = sys.argv[1]

qc_metrics_dna_25(path)