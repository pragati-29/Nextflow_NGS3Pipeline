import os
import pandas as pd
import subprocess
import time

start_time = time.time()

# open list.txt
filelist = pd.read_csv('list.txt', header=None)
filelist = filelist[0].tolist()

# ncores = os.cpu_count()
# usable cores
# noinspection SpellCheckingInspection
ncores = 4

# split list.txt into ncores parts
filelist = [filelist[i::ncores] for i in range(ncores)]

# write each part into a file
for i in range(ncores):
    with open('list' + str(i) + '.txt', 'w') as f:
        for item in filelist[i]:
            f.write("%s\n" % item)

# run all commands simultaneously
processes = []

for i in range(ncores):
    process = subprocess.Popen(["./annotation_args.sh", str(i)])
    processes.append(process)

# wait for all processes to finish
for process in processes:
    process.wait()

# check if all processes finished
for process in processes:
    if process.returncode != 0:
        print("Error: Process " + str(process.pid) + " failed!")
        exit(1)

rerun = []
# check output folders
for file in filelist[0]:
    if not os.path.exists('annotation/' + file):
        print("Error: Output folder for " + file + " not found!")
        exit(1)
    fnumber = os.listdir('annotation/' + file)
    if len(fnumber) != 7:
        print("Error: Wrong number of output files for " + file + "!")
        rerun.append(file)
        # remove output folder
        os.system("rm -rf annotation/" + file)
        # print files that need to be rerun to a txt file
        with open('list' + str(ncores + 1) + '.txt', 'w') as f:
            for item in rerun:
                f.write("%s\n" % item)
        process2 = subprocess.Popen(["./annotation_args.sh", str(ncores + 1)])
        # wait for final process to finish
        process2.wait()


# remove temporary files
for i in range(ncores):
    os.remove('list' + str(i) + '.txt')


end_time = time.time()

print("Time elapsed: " + str(end_time - start_time) + " seconds")
