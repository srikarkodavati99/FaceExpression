import subprocess
import os
import argparse
import sys

class cd:
    """Context manager for changing the current working directory."""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def analyze_files(openface, rootdir, outputdir, suffix = ''):
    """"Analyzes all files found in rootdir that end with suffix using OpenFace located at openface. 
    The output is stored in outputdir."""
    list_of_files = []
    subdirs = []
    
    # walk through files and subdirectories in root
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            # if suffix is specified: search for files with suffix
            if suffix != '':
                if file.endswith(suffix):
                    list_of_files.append(file)
                    subdirs.append(subdir)
            # else: use every file found
            else:
                list_of_files.append(file)
                subdirs.append(subdir)
                
    print("Found "  + str(len(list_of_files)) + " files to analyze.")
    print("Starting analyzing process...")

    if(len(list_of_files) > 0):
        i = 0
        for file in list_of_files:
            print("\nStarted analyzing file " + str(i+1) + "\n...")
            # subprocess.run(['mkdir', os.path.join(outputdir, file)], shell=True) # create an output dir for each analyzed video
            # change current directory (needed for performing openface command)
            # with cd(subdirs[i]):
                # subprocess.run(openface + ' -f ' + file + ' -out_dir ' + os.path.join(outputdir, file), shell=True)
            print(file)
            subprocess.run(openface + ' -f ' + str(subdirs[i])+'/'+str(file) + ' -out_dir ' + 'processed', shell=True)
            print("Finished analyzing file " + str(i+1))
            i += 1
        print("\nAll files are analyzed! The output is found in " + outputdir)  
    else:
        print("No files to analyze.")
open_dir='./OpenFace/build/bin/FaceLandmarkVidMulti'
root_dir='/content/drive/MyDrive/train-1'
output_dir='processed'
analyze_files(open_dir, root_dir, output_dir)