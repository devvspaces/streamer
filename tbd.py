import speech_recognition as sr
from pydub import AudioSegment

# convert mp3 file to wav  
# src=(r"C:\\Users\\Dell\\Music\\16. Options.mp3")
# sound = AudioSegment.from_mp3(src)
# sound.export("my_result2.wav", format="wav")

# print(dir(AudioSegment))

# exit()
file_audio = sr.AudioFile(r"2021-11-12 04-37-34.wav")

# use the audio file as the audio source                                        
r = sr.Recognizer()
with file_audio as source:
    audio_text = r.record(source)

    print(type(audio_text))
    print(r.recognize_google(audio_text, language='en-US'))