import os
path = os.getcwd()
filenames = os.listdir(path)
for filename in filenames:
    old_filename = filename
    
    new_filename = filename.replace("_001","")
    new_filename = new_filename.replace("_","-")
    new_filename = new_filename.replace("-R1.","_S1_L001_R1_001.")
    new_filename = new_filename.replace("-R2.","_S1_L001_R2_001.")
    os.rename(old_filename, new_filename)
    
print(new_filename)   
