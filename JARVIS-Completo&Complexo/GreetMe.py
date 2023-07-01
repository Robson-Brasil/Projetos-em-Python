import pyttsx3
import datetime

engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[3].id)
engine.setProperty("rate",180)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def greetMe():
    hour  = int(datetime.datetime.now().hour)
    if hour>=0 and hour<=12:
        speak("Bom dia Senhor")
        
    elif hour >12 and hour<=18:
        speak("Boa tarde senhor")

    else:
        speak("Boa noite senhor")

    speak("Por favor, diga-me Como posso ajduar o senhor ?")