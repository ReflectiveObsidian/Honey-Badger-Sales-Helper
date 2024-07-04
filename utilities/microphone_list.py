# Generates a list of microphones

import speech_recognition as sr

def get_microphone_list():
    microphones = sr.Microphone.list_microphone_names()
    return microphones