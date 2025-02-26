import speech_recognition as sr
import pyttsx3
import sounddevice as sd
import numpy as np
import wavio

recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    """Matnni ovozga aylantiradi"""
    engine.say(text)
    engine.runAndWait()

def record_audio(duration=5, samplerate=44100):
    """Mikrofondan ovoz yozib olib, faylga saqlaydi"""
    print("Gapiring...")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
    sd.wait()
    wavio.write("recorded.wav", audio_data, samplerate, sampwidth=2)
    return "recorded.wav"

while True:
    # Ovoz yozish
    audio_file = record_audio()

    # Ovozdan matn olish
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio, language="uz-UZ")
        print(f"Siz aytdingiz: {text}")

        if text.lower() == "salom":
            response = "Assalom alaykum"
            print(f"Bot: {response}")
            speak(response)
        if text.lower() == "shoxjaxon":
            response = "Assalom alaykum"
            print(f"Bot: {response}")
            speak(response)
        elif text.lower() == "to‘xta" or text.lower() == "stop":
            print("Bot: Dastur to‘xtatildi.")
            speak("Dastur to‘xtatildi.")
            break  # While loop dan chiqish
        else:
            print("Bot: Kechirasiz, tushunmadim.")
            speak("Kechirasiz, tushunmadim.")

    except sr.UnknownValueError:
        print("Bot: Gapni tushuna olmadim.")
        speak("Gapni tushuna olmadim.")

    except sr.RequestError:
        print("Bot: Internetda muammo bor.")
        speak("Internetda muammo bor.")

