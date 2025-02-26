import speech_recognition as sr
import pyttsx3

recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

with sr.Microphone() as source:
    print("Gapiring...")
    recognizer.adjust_for_ambient_noise(source)
    audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language="uz-UZ")
        print(f"Siz aytdingiz: {text}")

        if text.lower() == "salom":
            response = "Assalom alaykum"
            print(f"Bot: {response}")
            speak(response)
        else:
            print("Bot: Kechirasiz, tushunmadim.")
            speak("Kechirasiz, tushunmadim.")

    except sr.UnknownValueError:
        print("Bot: Gapni tushuna olmadim.")
        speak("Gapni tushuna olmadim.")

    except sr.RequestError:
        print("Bot: Internetda muammo bor.")
        speak("Internetda muammo bor.")
