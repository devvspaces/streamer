import logging

# Create the logger and set the logging level
logger = logging.getLogger('basic')
err_logger = logging.getLogger('basic.error')

import m3u8
import requests
import datetime
import moviepy.editor as mp
import speech_recognition as sr
from pydub import AudioSegment
import os
from langdetect import detect
from ShazamAPI import Shazam

# Required for channel communication
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



class M3U8:
    def __init__(self, link):
        self.link = link
        self.playlist = m3u8.load(self.link)
        self.base_url = self.get_base_url()

    def get_base_url(self):
        parts = self.link.split('/')
        parts.pop()
        return '/'.join(parts) + '/'

    def get_full_link(self, link):
        return self.base_url + link

    def get_ts_uris(self) -> tuple:
        ts = []
        target_duration = self.playlist.target_duration

        if target_duration is not None:
            for i in self.playlist.segments:

                if self.base_url in i.uri:
                    ts.append(i.uri)
                else:
                    ts.append(self.base_url + i.uri)

        else:
            media = self.playlist.media

            for i in media:
                if i.uri is not None:
                    # Create new m3u8 obj
                    media_link = self.get_full_link(i.uri)
                    media_obj = self.__class__(media_link)
                    ts, target_duration = media_obj.get_ts_uris()

        return ts, target_duration



class MediaLink:
    def __init__(self, stream, language='en-US') -> None:
        self.stream = stream
        self.language = language
        self.is_mp3 = False

        # What type of link are we dealing with
        if self.stream.link.endswith('.mp3'):
            self.is_mp3 = True
        

    def get_ts_links(self) -> tuple:
        obj = M3U8(link=self.stream.link)
        return obj.get_ts_uris()

    def send_channel_message(self, group_name, message, mtype=''):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{group_name}',
            {
                'type': 'channel_message',
                'message': message,
                'mtype': mtype,
            }
        )
    
    def generate_mp3(self, prefix) -> str:
        filename = prefix + '.mp3'
        filev = prefix + '.mpeg'

        try:
            my_clip = mp.VideoFileClip(filev)
            my_clip.audio.write_audiofile(filename)
        except KeyError:
            os.rename(filev, filename)

        return filename
    
    def generate_wav(self, mp3_file) -> str:
        # Get the prefix from the mp3_file_name
        prefix = mp3_file.split('.')[0]

        src=(mp3_file)
        # sound = AudioSegment.from_mp3(src)
        sound = AudioSegment.from_file(src)
        wav_file = f"{prefix}.wav"
        sound.export(wav_file, format="wav")
        logger.debug('Converted to wav')

        return wav_file
    
    def delete_file(self, filename):
        if os.path.exists(filename):
            os.remove(filename)
            logger.debug(f'Delete {filename}')
    
    def write_empty(self, filename):
        with open(filename,'wb') as f:
            data = b''
            f.write(data)
            logger.debug('Deleted filename')
    
    def recognize_speech(self, wav_file) -> str:
        # Get the text from wav
        file_audio = sr.AudioFile(wav_file)
        r = sr.Recognizer()

        with file_audio as source:
            audio_text = r.record(source)

            # Detect the language used
            language = detect(audio_text)

            try:
                return r.recognize_google(audio_text, language=language)
            except sr.UnknownValueError as e:
                pass

        return ''
    
    def recognize_music(self, mp3_file):
        mp3_file_content_to_recognize = open(mp3_file, 'rb').read()

        shazam = Shazam(mp3_file_content_to_recognize)
        recognize_generator = shazam.recognizeSong()
        obj = next(recognize_generator)[1]

        # logger.debug(obj)

        result = {}

        try:
            track = obj['track']

            result = {
                'key' : track['key'],
                'layout' : track['layout'],
                'type' : track['type'],
                'title' : track['title'],
                'subtitle' : track['subtitle'],
                'url' : track['share']['href'],
            }
        except KeyError:
            pass

        return result
    

    def get_song_details(self, text):
        # Recognize song
        url = "https://shazam.p.rapidapi.com/search"

        querystring = {"term":text,"locale":"en-US","offset":"0","limit":"5"}

        headers = {
            'x-rapidapi-host': "shazam.p.rapidapi.com",
            'x-rapidapi-key': ""
            }

        response = requests.request("GET", url, headers=headers, params=querystring)

        return response.json()
    
    def process(self):

        ts_links = []
        sep = 1

        # What type of link are we dealing with
        if self.is_mp3:
            ts_links = [self.stream.link]
            logger.debug(f"Ts links -- {len(ts_links)} and Separator -- {sep}")
        else:
            ts_links, target_duration = self.get_ts_links()
            if target_duration:
                val = float(target_duration)
                if val < 10:
                    sep = int(10 / val)
            
            logger.debug(f"Ts links -- {len(ts_links)} and Separator -- {sep} and target_duration -- {target_duration}")
        
        # Generate a new file name
        name_prefix = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

        if self.is_mp3:
            filename = name_prefix+'.mp3'
        else:
            filename = name_prefix+'.mpeg'

        for i in range(len(ts_links))[::sep]:
            new_set = ts_links[i:i+sep]

            completed = False

            for url in new_set:
                r1 = requests.get(url, stream=True)
                if(r1.status_code == 200 or r1.status_code == 206):
                    # re-open output file to append new video
                    with open(filename,'ab') as f:
                        data = b''
                        for chunk in r1.iter_content(chunk_size=1024):
                            if(chunk):
                                data += chunk
                        f.write(data)

                        logger.debug(f"Wrote to file {filename}")

                        # set completed to true
                        completed = True
                else:
                    logger.debug("Received unexpected status code {}".format(r1.status_code))
            
            if completed:
                if not self.is_mp3:
                    # Read file and convert to audio
                    mp3_file = self.generate_mp3(name_prefix)
                else:
                    mp3_file = filename

                # Recognize with shazam api
                result = self.recognize_music(mp3_file)
                logger.debug(result)

                # Create result object
                if result:
                    self.send_channel_message(self.stream.id, message=result, mtype='stream_result')
                    self.stream.result_set.create(**result)
                
                # break

                # Delete mp3 file
                self.delete_file(mp3_file)

                try:
                    # Delete file
                    self.delete_file(filename)
                except PermissionError as e:
                    err_logger.exception(e)
                    logger.debug(f'Wrote {filename} as empty')
                    self.write_empty(filename)
