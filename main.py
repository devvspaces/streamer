import moviepy.editor as mp
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from browsermobproxy import Server
import datetime
import sys
import speech_recognition as sr
from pydub import AudioSegment

import os


url = "https://www.twitch.tv/videos/958188968"

#start proxy server
server = Server("C:\\browsermob-proxy-2.1.4\\bin\\browsermob-proxy.bat")
server.start()
proxy = server.create_proxy()

# selenium arguments
options = webdriver.ChromeOptions()
# options.add_argument('headless')
options.add_argument("--window-size=1920,1080")
options.add_argument("--proxy-server={0}".format(proxy.proxy))

caps = DesiredCapabilities.CHROME.copy()
caps['acceptSslCerts'] = True
caps['acceptInsecureCerts'] = True

proxy.new_har("twitch",options={'captureHeaders': True,'captureContent':True,'captureBinaryContent': True}) # tag network logs 
              
driver = webdriver.Chrome('chromedriver',options=options,desired_capabilities=caps)
driver.get(url)

filesynx = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")+'.mpeg'
filename = filesynx+'.mpeg'

fetched = []


while True:
    for ent in proxy.har['log']['entries']:
        _url = ent['request']['url']
        _response = ent['response']
        
        #make sure havent already downloaded this piece
        if _url in fetched:
            continue
            
        if _url.endswith('.ts'):
            #check if this url had a valid response, if not, ignore it
            if 'text' not in _response['content'].keys() or not _response['content']['text']:
                continue
                
            print(_url+'\n')
            r1 = requests.get(_url, stream=True)
            if(r1.status_code == 200 or r1.status_code == 206):

                # re-open output file to append new video
                with open(filename,'ab') as f:
                    data = b''
                    for chunk in r1.iter_content(chunk_size=1024):
                        if(chunk):
                            data += chunk
                    f.write(data)
                    fetched.append(_url)

                # Read file and convert to audio
                my_clip = mp.VideoFileClip(filename)
                mp3_name = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                my_clip.audio.write_audiofile(mp3_name+'.mp3')


                # Convert mp3 to wav
                src=(mp3_name+'.mp3')
                sound = AudioSegment.from_mp3(src)
                sound.export(f"{mp3_name}.wav", format="wav")
                print('Converted to wav')

                # Delete mp3 file
                if os.path.exists(mp3_name+'.mp3'):
                    os.remove(mp3_name+'.mp3')
                    print('Delete mp3')

                # Get the text from wav
                file_audio = sr.AudioFile(f"{mp3_name}.wav")
                r = sr.Recognizer()
                with file_audio as source:
                    audio_text = r.record(source)

                    try:
                        print('\n\n')
                        text = r.recognize_google(audio_text, language='en-US')
                        print(text)
                        print('\n\n')

                        # Recognize song
                        url = "https://shazam.p.rapidapi.com/search"

                        querystring = {"term":text,"locale":"en-US","offset":"0","limit":"5"}

                        headers = {
                            'x-rapidapi-host': "shazam.p.rapidapi.com",
                            'x-rapidapi-key': "ab45e898d7msh2fb0506a5c7035ap1b6989jsnd9ef42c71396"
                            }

                        response = requests.request("GET", url, headers=headers, params=querystring)

                        print(response.text)
                    except sr.UnknownValueError as e:
                        print('\n\nCould not understand\n\n')

                # Delete wav file
                if os.path.exists(f"{mp3_name}.wav"):
                    os.remove(f"{mp3_name}.wav")
                    print('Deleted wav')

                # Send text to shazam api


                # Delete file
                with open(filename,'wb') as f:
                    data = b''
                    f.write(data)
                    print('Deleted filename')
            else:
                print("Received unexpected status code {}".format(r1.status_code))

server.stop()
driver.quit()
