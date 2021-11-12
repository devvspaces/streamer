import speech_recognition as sr
from pydub import AudioSegment

"""Recognizes the audio and sends it for display to displayText."""
r = sr.Recognizer()
with sr.Microphone() as source:
    audio = r.listen(source)
try:
    put=r.recognize_google(audio)
    print(put)
except sr.UnknownValueError:
    print("Could not understand audio")
except sr.RequestError as e:
    print("Could not request results; {0}".format(e))