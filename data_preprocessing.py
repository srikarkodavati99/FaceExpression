from moviepy.editor import *
import subprocess
import os
import cv2
import pandas as pd
import wave
import json
import pandas as pd

import subprocess
import os 
import pandas as pd

import contextlib
from google.cloud.speech import *

import emotion_det as te
import pandas as pd
import nltk

client = SpeechClient()


config = RecognitionConfig(
   
    encoding = 'LINEAR16',
    
    sample_rate_hertz = 44100,
    audio_channel_count = 2,
    language_code="en-US",
    enable_word_time_offsets=True,
)

def standardise_au(stand_csv):
    df_au=pd.read_csv(stand_csv)
    df_au_temp=df_au.filter(regex='_r$', axis=1)
    print(df_au_temp)
    df_au_final=df_au.filter(regex='_r$', axis=1)/5
    print(df_au_final)
def con_wav_files(rootdir, suffix = 'mp4'):
    """"Convert all files found in rootdir to wav files and store The output is stored in outputdir."""
    list_of_files = []
    subdirs = []
    print(rootdir)
    df_1=pd.read_csv('output_final.csv',index_col=False)
    df_1['File']=df_1['File'].str.replace('.csv','.mp4')
    # walk through files and subdirectories in root
    for file in os.listdir(rootdir):
        #     # if suffix is specified: search for files with suffix
            if suffix != '':
                if file.endswith(suffix):
                    list_of_files.append(file)
    print("Found "  + str(len(list_of_files)) + " files to analyze.")
    print("Starting analyzing process...")
    df_final=pd.DataFrame()
    if(len(list_of_files) > 0):
        i = 0
 
        video_name=[]
        framerate=[]
        for file in list_of_files:
        	if file in df_1['File'].values:
	       		video_name=[]
	       		framerate=[]
	       		print("\nStarted analyzing file " + str(i+1) + "\n...")
	       		print(file)
	       		out_file=file.replace('.mp4','.wav')
	       		mp4_file = rootdir+'/'+file
	       		wav_file = rootdir+'/'+out_file
	       		videoclip = VideoFileClip(mp4_file)
	       		millis = cv2.VideoCapture(mp4_file).get(cv2.CAP_PROP_FPS)
	       		audioclip = videoclip.audio
	       		video_name.append(file)
	       		framerate.append(millis)
	       		audioclip.write_audiofile(wav_file)
	       		audioclip.close()
	       		videoclip.close()
	       		print('@@@@@@@@@@@@@@@@@@@@@')
	       		df = pd.DataFrame(list(zip(video_name,framerate)),columns =['Video','FPS'])
	       		if len(df_final)==0:
	       			df_final=df
	       		else:
	       			df_final=df_final.append(df)
        df_final.to_csv('framerate.csv')
        print(df_final)

def speech_rec_files(rootdir, suffix = 'wav'):
    """"Analyzes all files found in rootdir to find the words and their time frame the output is stored in output csv."""
    list_of_files = []
    subdirs = []
    print(rootdir)
    # walk through files and subdirectories in root
    for file in os.listdir(rootdir):
        
            if suffix != '':
                if file.endswith(suffix):
                    list_of_files.append(file)
    print("Found "  + str(len(list_of_files)) + " files to analyze.")
    print("Starting analyzing process...")
    df_final=pd.DataFrame()
    frame_rate=pd.read_csv('framerate.csv')
    i=0
    if(len(list_of_files) > 0):
        for file in list_of_files:
            i = i+1
            print("\nStarted analyzing file " + str(i) + "\n...")
            
            print(file)
            audio_filename = file
            
            with open(rootdir+'/'+audio_filename, "rb") as audio_file:
              content = audio_file.read()
            audio = RecognitionAudio(content=content)

            audio_filename_out=audio_filename.replace('.wav','.mp4')
            operation = client.long_running_recognize(config=config, audio=audio)

            print("Waiting for operation to complete...")
            result = operation.result(timeout=90)
            
            # convert list of JSON dictionaries to list of 'Word' objects
            list_of_Words = []
            videoname=[]
            wordname=[]
            starttime=[]
            endtime=[]
            frameRate=[]
            for result in result.results:
                alternative = result.alternatives[0]
                print("Transcript: {}".format(alternative.transcript))
                print("Confidence: {}".format(alternative.confidence))

                for word_info in alternative.words:
                    word = word_info.word
                    start_time = word_info.start_time
                    end_time = word_info.end_time

                    audio_filename=audio_filename.replace('.wav','.mp4')
                    videoname.append(audio_filename)
                    endtime.append(int(end_time.seconds)+end_time.nanos/1000000000)
                    starttime.append(int(start_time.seconds)+start_time.nanos/1000000000)
                    wordname.append(word)
                    mp_file=file.replace('.wav','.mp4')
                    print(float(frame_rate[frame_rate['Video']==mp_file]['FPS']))
                    frameRate.append(float(frame_rate[frame_rate['Video']==mp_file]['FPS']))
                    df = pd.DataFrame(list(zip(videoname,starttime,endtime,wordname,frameRate)),columns =['Video', 'Start','End','Word','FPS'])

                    
            print(df)
            if len(df_final)==0:
                df_final=df
            else:
                df_final=df_final.append(df)
        df_final.to_csv('speech_word1.csv')
        print(df_final)
        

def map_word_toFrames():
     """"Map all words found in speech csv to frames according to time of frame then stored in output csv."""
    list_of_files = []

    word_df=pd.read_csv('speech_word1.csv')
    AU_df=pd.read_csv('data_final.csv')
    AU_df['File']=AU_df['File'].str.replace('.csv','.mp4')
    
    print(AU_df)
    
    i=0
    for index, row in AU_df.iterrows():
        if row['File'] in word_df['Video'].values:
                word1_df=word_df[word_df['Video']==row['File']]
                millis=100/word1_df['FPS'].iloc[0]
                seconds=(millis/100)%60
                time_frame=seconds*row['Unnamed: 0']
                print(time_frame)
                word2_df=word1_df[(word1_df['Start']<=time_frame) & (word1_df['End']>=time_frame)]
                if len(word2_df) != 0:
                        work_str=word2_df.iloc[0]['Word']
                        print(work_str)
                        AU_df.at[index,'Word']=work_str
        else:
                AU_df.drop(index, inplace=True)
                i=+1
                print(i,'@@@@@@@@@@@@')

    print(AU_df)
    AU_df.to_csv('data_word_final1.csv')
def det_emotion():
    """"Analyzes all texts found in the transcript file to find the emotion of the sentence and store in output csv."""
    nltk.download('omw-1.4')
    with open('transcript.txt') as f:
        line = f.readlines()
    
    video_name=[]
    sent_list=[]
    for i in str(line).split("\':"):
        
        trans_temp=[]
        for j in range(0,len(i.split('\''))):
            if j == len(i.split('\''))-1:
                
                print(i.split('\'')[j].replace('\\',''))
                video_name.append(i.split('\'')[j].replace('\\',''))
            else:
                
                trans_temp.append(i.split('\'')[j].replace('\\',''))
        sent=''.join(trans_temp)
        sent_list.append(sent)


    sent_list.pop(0)
    happy_i=[]
    angry_i=[]
    surprise_i=[]
    sad_i=[]
    fear_i=[]
    for i in sent_list: 
        t=te.get_emotion(i)
        print(t)
        happy_i.append(t['Happy'])
        angry_i.append(t['Angry'])
        surprise_i.append(t['Surprise'])
        sad_i.append(t['Sad'])
        fear_i.append(t['Fear'])
        
    df = pd.DataFrame(list(zip(video_name,happy_i,
    angry_i,
    surprise_i,
    sad_i,
    fear_i)),columns =['Video', 'Happy','Angry','Surprise','Sad','Fear'])
    print(df)


    AU_df=pd.read_csv('data_word_final.csv')
    AU_df['File']=AU_df['File'].str.replace('.csv','.mp4')
    for index,row in df.iterrows():
        
        AU_df.loc[AU_df["File"] == row['Video'], "Happy"] = row['Happy']
        AU_df.loc[AU_df["File"] == row['Video'], "Angry"] = row['Angry']
        AU_df.loc[AU_df["File"] == row['Video'], "Surprise"] = row['Surprise']
        AU_df.loc[AU_df["File"] == row['Video'], "Sad"] = row['Sad']
        AU_df.loc[AU_df["File"] == row['Video'], "Fear"] = row['Fear']
    print(AU_df)

    AU_df.to_csv('data_emotion_final.csv')























standardise_au('video.csv')
con_wav_files('train_videos')
speech_rec_files('wav_files')
map_word_toFrames()
det_emotion()
