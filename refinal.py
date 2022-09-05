
#Import necessary modules

import speech_recognition as sr
import pyttsx3
import pywhatkit 
import datetime
import wikipedia
import pyjokes
import requests, json , sys
import sounddevice as sd
from tkinter import *
import queue
import soundfile as sf
import threading
from tkinter import messagebox
import os 
import shutil
import time
import speedtest
import spotipy
import webbrowser
import transformers
from transformers import pipeline

from summarizer import Summarizer

from pydub import AudioSegment
from pydub.silence import split_on_silence
from bs4 import BeautifulSoup


listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice',voices[0].id)
engine. setProperty("rate", 165)

def talk(text):
    engine.say(text)
    engine.runAndWait() 


# Function For Recording and summarizing the speech  
def combined():
    #Define the user interface
    voice_rec = Tk()
    voice_rec.geometry("360x200")
    voice_rec.title("Personal Voice Assistant")
    voice_rec.config(bg="#107dc2")

    #Create a queue to contain the audio data
    q = queue.Queue()
    #Declare variables and initialise them
    recording = False
    file_exists = False    

    #Fit data into queue
    def callback(indata, frames, time, status):
        q.put(indata.copy())

    #Functions to play, stop and record audio
    #The recording is done as a thread to prevent it being the main process
    def threading_rec(x):
        if x == 1:
            #If recording is selected, then the thread is activated
            t1=threading.Thread(target= record_audio)
            t1.start()
        elif x == 2:
            #To stop, set the flag to false
            global recording
            recording = False
            messagebox.showinfo(message="Recording finished")
        elif x == 3:
            #To play a recording, it must exist.
            if file_exists:
                #Read the recording if it exists and play it
                data, fs = sf.read("trial.wav", dtype='float32') 
                sd.play(data,fs)
                sd.wait()
            else:
                #Display and error if none is found
                messagebox.showerror(message="Record something to play")

    #Recording function
    def record_audio():
        #Declare global variables    
        global recording 
        #Set to True to record
        recording= True   
        global file_exists 
        #Create a file to save the audio
        messagebox.showinfo(message="Recording Audio. Speak into the mic")
        with sf.SoundFile("trial.wav", mode='w', samplerate=44100,
                            channels=2) as file:
        #Create an input stream to record audio without a preset time
                with sd.InputStream(samplerate=44100, channels=2, callback=callback):
                    while recording == True:
                        #Set the variable to True to allow playing the audio later
                        file_exists =True
                        #write into file
                        file.write(q.get())

        
    #Label to display app title
    title_lbl  = Label(voice_rec, text="Personal Voice Assistant", bg="#107dc2").grid(row=0, column=0, columnspan=3)

    #Button to record audio
    record_btn = Button(voice_rec, text="Record Audio", command=lambda m=1:threading_rec(m))
    #Stop button
    stop_btn = Button(voice_rec, text="Stop Recording", command=lambda m=2:threading_rec(m))
    #Play button
    play_btn = Button(voice_rec, text="Play Recording", command=lambda m=3:threading_rec(m))

    #Position buttons
    record_btn.grid(row=1,column=1)
    stop_btn.grid(row=1,column=0)
    play_btn.grid(row=1,column=2)
    voice_rec.mainloop()



    # create a speech recognition object
    r = sr.Recognizer()
    path = "trial.wav"
    # a function that splits the audio file into chunks
    # and applies speech recognition
    def get_large_audio_transcription(path):
        """
        Splitting the large audio file into chunks
        and apply speech recognition on each of these chunks            
        """
        # open the audio file using pydub
        sound = AudioSegment.from_wav(path)  
        # split audio sound where silence is 700 miliseconds or more and get chunks
        chunks = split_on_silence(sound,
            # experiment with this value for your target audio file
            min_silence_len = 500,
            # adjust this per requirement
            silence_thresh = sound.dBFS-14,
            # keep the silence for 1 second, adjustable as well
            keep_silence=500,
        )
        folder_name = "audio-chunks"
        # create a directory to store the audio chunks
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        whole_text = ""
        # process each chunk 
        for i, audio_chunk in enumerate(chunks, start=1):
            # export audio chunk and save it in
            # the `folder_name` directory.
            chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
            audio_chunk.export(chunk_filename, format="wav")
            # recognize the chunk
            with sr.AudioFile(chunk_filename) as source:
                audio_listened = r.record(source)
                # try converting it to text
                try:
                    text = r.recognize_google(audio_listened)
                except sr.UnknownValueError as e:
                    print("Error:", str(e))
                else:
                    text = f"{text.capitalize()}. "
                    print(chunk_filename, ":", text)
                    whole_text += text
        
       
        # remove old account directory
        shutil.rmtree(r'audio-chunks', ignore_errors=True)
        # return the text for all chunks detected
        return whole_text

    #print("\nFull text:", get_large_audio_transcription(path))    
    f = open("sairam.txt", "w")
    f.write(get_large_audio_transcription(path))
    f.close()  
    
def take_commandf():
    with sr.Microphone() as source:
        time.sleep(1)
        talk("how can i assist you")
        print("Speak out the command...")
        voice=listener.listen(source)
        commandx=listener.recognize_google(voice)
        commandx = commandx.lower()    
        return commandx    
    return commandx    

def take_input():
    with sr.Microphone() as source:
        time.sleep(1)
        print("Say play or break")
        voice=listener.listen(source)
        commandx=listener.recognize_google(voice)
        commandx = commandx.lower()    
        return commandx    
    return commandx

def take_weather():
    with sr.Microphone() as source:
        time.sleep(1)
        talk("Speak the name of the city")
        print("Speak the name of the city")
        voice=listener.listen(source)
        commandx=listener.recognize_google(voice)
        commandx = commandx.lower()    
        return commandx    
    return commandx   

def take_song():
    with sr.Microphone() as source:
        talk('say the song')
        time.sleep(1)
        print("Say the song")
        voice=listener.listen(source)
        commandx=listener.recognize_google(voice)
        commandx = commandx.lower()    
        return commandx    
    return commandx   

def abstract():
    summarizer = pipeline("summarization")
    fa = open("sairam.txt", "r" ,encoding='utf-8')
    text = fa.read()
    fa.close()
    summary_text = summarizer(text, max_length=100, do_sample=False)[0]['summary_text']
    print(summary_text)
    print("\n")
    talk(summary_text)
    return 

def extract():
    model = Summarizer()
    text = open("sairam.txt", "r" ,encoding='utf-8')
    summary = text.read()
    f = open("summary.txt", "w")
    f.write(model(summary))
    f.close()  

    fh = open("summary.txt", "r" ,encoding='utf-8')
    robber = fh.read()
    fh.close()
    print(robber)
    print("\n")   
    talk(robber) 
    return    

                   
def run_mitra():
    commandf = take_commandf()    
    print(commandf)
    
    if 'summary' in commandf:
        abstract()
        return(0)   
    if 'extract' in commandf:
        extract()
        return(0)      
    if 'record' in commandf:
        combined()
        return(0)    
    if 'sleep' in commandf:
        talk("Bye i miss you")
        return(-1)
    if 'thanks' in commandf:
        talk("you are welcome")
        return(0)    
    if 'about' in commandf:
        talk("I am mythrraa personal voice Assistant developed by sricharan and lalith born on april 25th")
        return(0)    
    if 'time' in commandf:
        time = datetime.datetime.now().strftime('%H:%M')        
        talk('Current time is ' + time)    
        return 0
    if 'find' in commandf:
        person = commandf.replace('find','')
        info = wikipedia.summary(person,1)
        talk(info)
        return 0        
    if 'joke' in commandf:
        talk(pyjokes.get_joke())
        return 0
    if 'india' in commandf:
        url = 'https://zeenews.india.com/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find('body').find_all('h3',limit=3)#for zeenews        
        for x in headlines:
            talk(x.text.strip())
        return 0
    if 'world' in commandf:
        url = 'https://www.thehindu.com/news/international/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find('body').find_all('h2',limit=3)#hindu
        for x in headlines:
            talk(x.text.strip())
        return 0
    if 'music' in commandf:
        username = 'myself buddy'
        clientID = '8995cab642b3481c87332799868c8b2a'
        clientSecret = '97cab51e85f141f68ffb72dbdad6a47a'
        redirectURI = 'http://google.com/' 
         
        oauth_object = spotipy.SpotifyOAuth(clientID,clientSecret,redirectURI)
        token_dict = oauth_object.get_access_token()
        token = token_dict['access_token']
        spotifyObject = spotipy.Spotify(auth=token)
        user = spotifyObject.current_user()
        print(json.dumps(user,sort_keys=True, indent=4))
        while True:
            print("Welcome, "+ user['display_name'])
            print("break - Exit")
            print("play - Search for a Song")
            talk('Speak play to find a song')
            talk('Speak break to exit')
            choice = take_input()
            if choice == 'play':
                # Get the Song Name.
                searchQuery = take_song()
                # Search for the Song.
                searchResults = spotifyObject.search(searchQuery,1,0,"track")
                # Get required data from JSON response.
                tracks_dict = searchResults['tracks']
                tracks_items = tracks_dict['items']
                song = tracks_items[0]['external_urls']['spotify']
                # Open the Song in Web Browser
                webbrowser.open(song)
                print('Song has opened in your browser.')
            elif choice == 'break':
                break
            else:
                print("Speak out a valid choice.")
        return 0   
    if 'weather' in commandf:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'} 
        def weather(city):
            city = city.replace(" ", "+")
            res = requests.get(
                f'https://www.google.com/search?q={city}&oq={city}&aqs=chrome.0.35i39l2j0l4j46j69i60.6128j1j7&sourceid=chrome&ie=UTF-8', headers=headers)
            print("Searching...\n")
            soup = BeautifulSoup(res.text, 'html.parser')
            location = soup.select('#wob_loc')[0].getText().strip()
            time = soup.select('#wob_dts')[0].getText().strip()
            info = soup.select('#wob_dc')[0].getText().strip()
            weather = soup.select('#wob_tm')[0].getText().strip()
            print(location)
            print(time)
            print(info)
            print(weather+"°C")
            talk(location)
            talk(time)
            talk(info)
            talk(weather+"degrees celcius")
         
         
        city = take_weather()
        city = city+" weather"
        weather(city)
        return 0           
    else:
        talk('Sorry could you repeat')
        run_mitra()                     

talk('Sairam mythrraa here')    

while True:
    i=0
    i=run_mitra()
    if(i!=0):
        break
    else:
        continue