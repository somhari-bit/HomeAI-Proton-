import requests
import pyttsx3
import speech_recognition as sr
from datetime import date
import datetime
import webbrowser
import os
from os import listdir
from os.path import isfile, join
import sys
from pynput.keyboard import Key, Controller
import pyautogui
from threading import Thread
import cv2
from deepface import DeepFace
import app  # Import your app module
import Gesture_Controller
import wikipedia
# Initialize Flask server
FLASK_SERVER_URL = 'http://127.0.0.1:5000'

# Initialize text-to-speech
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# Initialize speech recognizer
r = sr.Recognizer()
keyboard = Controller()

# Variables
file_exp_status = False
files = []
path = ''
is_awake = True


def reply(audio):
    app.ChatBot.addAppMsg(audio)
    print(audio)
    engine.say(audio)
    engine.runAndWait()


def wish():
    hour = int(datetime.datetime.now().hour)
    if hour < 12:
        reply("Good Morning!")
    elif hour < 18:
        reply("Good Afternoon!")
    else:
        reply("Good Evening!")
    reply("I am Proton, how may I help you?")


def record_audio():
    with sr.Microphone() as source:
        r.energy_threshold = 500
        r.dynamic_energy_threshold = False
        r.pause_threshold = 0.8
        audio = r.listen(source, phrase_time_limit=5)
        try:
            return r.recognize_google(audio).lower()
        except sr.RequestError:
            reply('Sorry, my service is down. Please check your internet connection.')
        except sr.UnknownValueError:
            print('Cannot recognize.')
            return ''
        return ''


def respond(voice_data):
    global file_exp_status, files, is_awake, path
    voice_data = voice_data.replace('proton', '')
    app.eel.addUserMsg(voice_data)

    if not is_awake:
        if 'wake up' in voice_data:
            is_awake = True
            wish()

    elif 'hello' in voice_data:
        wish()

    elif 'what is your name' in voice_data:
        reply('My name is Proton!')

    elif 'date' in voice_data:
        reply(date.today().strftime("%B %d, %Y"))

    elif 'time' in voice_data:
        reply(str(datetime.datetime.now()).split(" ")[1].split('.')[0])

    elif 'search' in voice_data:
        query = voice_data.split('search', 1)[1].strip()
        reply(f'Searching for {query}')
        url = f'https://google.com/search?q={query}'
        try:
            webbrowser.get().open(url)
            reply('This is what I found.')
        except:
            reply('Please check your internet connection.')

    elif 'location' in voice_data:
        reply('Which place are you looking for?')
        temp_audio = record_audio()
        app.eel.addUserMsg(temp_audio)
        reply('Locating...')
        url = f'https://google.nl/maps/place/{temp_audio}/'
        try:
            webbrowser.get().open(url)
            reply('This is what I found.')
        except:
            reply('Please check your internet connection.')

    elif 'news' in voice_data:
        query = voice_data.split('news', 1)[1].strip()
        reply(f'Fetching news about {query}')
        news_summary = get_news(query)
        reply(news_summary)

    elif 'wikipedia' in voice_data:
        query = voice_data.split('wikipedia', 1)[1].strip()
        reply(f'Fetching information from Wikipedia about {query}')
        wiki_summary = get_wikipedia_summary(query)
        reply(wiki_summary)

    elif 'bye' in voice_data or 'by' in voice_data:
        reply("Goodbye! Have a nice day.")
        is_awake = False

    elif 'exit' in voice_data or 'terminate' in voice_data:
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
        app.ChatBot.close()
        sys.exit()

    elif 'launch gesture recognition' in voice_data:
        if Gesture_Controller.GestureController.gc_mode:
            reply('Gesture recognition is already active.')
        else:
            gc = Gesture_Controller.GestureController()
            t = Thread(target=gc.start)
            t.start()
            reply('Launched successfully.')

    elif 'stop gesture recognition' in voice_data:
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
            reply('Gesture recognition stopped.')
        else:
            reply('Gesture recognition is already inactive.')

    elif 'copy' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('c')
            keyboard.release('c')
        reply('Copied.')

    elif 'paste' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('v')
            keyboard.release('v')
        reply('Pasted.')

    elif 'list' in voice_data:
        path = 'C://'
        files = listdir(path)
        filestr = ''.join(f'{i + 1}:  {f}<br>' for i, f in enumerate(files))
        file_exp_status = True
        reply('These are the files in your root directory.')
        app.ChatBot.addAppMsg(filestr)

    elif file_exp_status:
        if 'open' in voice_data:
            try:
                index = int(voice_data.split(' ')[-1]) - 1
                if isfile(join(path, files[index])):
                    os.startfile(join(path, files[index]))
                    file_exp_status = False
                else:
                    path = join(path, files[index] + '//')
                    files = listdir(path)
                    filestr = ''.join(f'{i + 1}:  {f}<br>' for i, f in enumerate(files))
                    reply('Opened successfully.')
                    app.ChatBot.addAppMsg(filestr)
            except (IndexError, ValueError, FileNotFoundError):
                reply('File or folder not found or permission issue.')

        elif 'back' in voice_data:
            if path == 'C://':
                reply('This is the root directory.')
            else:
                path = join('/'.join(path.split('/')[:-2]), '')
                files = listdir(path)
                filestr = ''.join(f'{i + 1}:  {f}<br>' for i, f in enumerate(files))
                reply('Back to previous directory.')
                app.ChatBot.addAppMsg(filestr)
    else:
        reply('I am not programmed to do this!')


def adjust_environment(user_name):
    profile = user_profiles.get(user_name, {})
    fan_speed = profile.get("fan_speed", "medium")
    ac_temperature = profile.get("ac_temperature", 24)

    try:
        response = requests.post(f'{FLASK_SERVER_URL}/update', json={
            'fan_speed': fan_speed,
            'ac_temperature': ac_temperature
        })
        if response.status_code == 200:
            reply(f"Fan speed set to {fan_speed} and AC temperature set to {ac_temperature} degrees Celsius.")
        else:
            reply("Failed to update values.")
    except Exception as e:
        reply(f"Error updating values: {e}")


def get_news(query):
    # Use your preferred news API or scraping method here
    return f"News about {query}"


def get_wikipedia_summary(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Disambiguation error: {e.options}"
    except wikipedia.exceptions.PageError:
        return "Page not found."
    except Exception as e:
        return f"Error fetching Wikipedia summary: {e}"


# Main driver code
if __name__ == '__main__':
    t1 = Thread(target=app.ChatBot.start)
    t1.start()

    while not app.ChatBot.started:
        time.sleep(0.5)

    wish()
    while True:
        if app.ChatBot.isUserInput():
            voice_data = app.ChatBot.popUserInput()
        else:
            voice_data = record_audio()

        if 'proton' in voice_data:
            try:
                respond(voice_data)
            except SystemExit:
                reply("Exit successful.")
                break
            except Exception as e:
                print(f"Exception: {e}")
                break
