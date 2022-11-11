import subprocess
import os
import pandas as pd
def filter_files(rootdir, suffix = 'csv'):
    """"Analyzes all files found in rootdir that end with suffix using OpenFace located at openface. 
    The output is stored in outputdir."""
    list_of_files = []
    subdirs = []
    print(rootdir)
    # walk through files and subdirectories in root
    for file in os.listdir(rootdir):
        # print('@@')
        # for file in files:
        #     # if suffix is specified: search for files with suffix
            if suffix != '':
                if file.endswith(suffix):
                    list_of_files.append(file)
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
            df_temp=pd.read_csv(str(rootdir)+'/'+str(file))
            df_temp_1=df_temp.filter(regex='_r$', axis=1)
            print(df_temp['frame'].tolist())
            df_temp_1.insert(0, "frame", df_temp['frame'].tolist(), True)
            df_temp_1.insert(1, "face_id", df_temp['face_id'].tolist(), True)
            df_temp_1.insert(2, "timestamp", df_temp['timestamp'].tolist(), True)
            # df_temp_1=df_temp_1.append(df_temp[['frame','face_id','timestamp']])
            df_temp_1.to_csv('outAU/'+str(file))
            i+=1
        # print("\nAll files are analyzed! The output is found in " + outputdir)
filter_files('processed24')