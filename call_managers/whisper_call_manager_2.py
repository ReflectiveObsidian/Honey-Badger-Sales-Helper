# When started, periodically calls the add_call_log_callback with a CallLog object

from datetime import datetime
from time import sleep

import speech_recognition as sr

from call_managers.call_manager import CallManager
from model.call_log import CallLog

class WhisperCallManager2(CallManager):
    def __init__(self, add_call_log_callback, salesperson_device_id_callback, customer_device_id_callback):
        # add_call_log_callback is a function that takes a CallLog object as an argument
        # This updates the model with the new call log
        self.add_call_log_callback = add_call_log_callback
        self.salesperson_device_id_callback = salesperson_device_id_callback
        self.customer_device_id_callback = customer_device_id_callback

        # Called asynchonously by recognizer
        def callback_salesperson(recognizer, audio):
            try:
                #result = self.salesperson_recognizer.recognize_whisper(audio, language = "english")
                result = self.recognize_faster_whisper(audio)
            except sr.UnknownValueError:
                result = "Whisper could not understand audio"
            except sr.RequestError as e:
                result = "Sphinx error; {0}".format(e)
            print("[WCM2] Salesperson: ", result)
            self.add_call_log_callback(CallLog(datetime.now(), "Salesperson", result))

        self.speech_recognition_callback_salesperson = callback_salesperson

        def callback_customer(recognizer, audio):
            try:
                #result = self.salesperson_recognizer.recognize_whisper(audio, language = "english")
                result = self.recognize_faster_whisper(audio)
            except sr.UnknownValueError:
                result = "Whisper could not understand audio"
            except sr.RequestError as e:
                result = f"Could not request results from Whisper; {e}"
            print("[WCM2] Customer: ", result)
            self.add_call_log_callback(CallLog(datetime.now(), "Customer", result))
        self.speech_recognition_callback_customer = callback_customer

        self.salesperson_recognizer = sr.Recognizer()
        self.customer_recognizer = sr.Recognizer()
        self.salesperson_recognizer.energy_threshold = 4000
        self.customer_recognizer.energy_threshold = 4000

    def start_call(self):
        print("[WCM2] call start fn")

        device_index_salesperson = self.salesperson_device_id_callback()
        self.salesperson_microphone = sr.Microphone(device_index= device_index_salesperson)
        print("[WCM2] salesperson device index: ", device_index_salesperson)

        device_index_customer = self.customer_device_id_callback()
        self.customer_microphone = sr.Microphone(device_index= device_index_customer)
        print("[WCM2] customer device index: ", device_index_customer)
        
        print("[WCM2] 1")
        with self.salesperson_microphone as source:
            self.salesperson_recognizer.adjust_for_ambient_noise(source)
        print("[WCM2] 1.1")
        with self.customer_microphone as source:
            self.customer_recognizer.adjust_for_ambient_noise(source)
        print("[WCM2] 2")
        # Starts listening and reutrns a function to stop listening
        print("starting salesperson mic")
        self.stop_listening_salesperson = self.salesperson_recognizer.listen_in_background(self.salesperson_microphone, self.speech_recognition_callback_salesperson)
        sleep(1)
        print("starting customer mic")
        self.stop_listening_customer = self.customer_recognizer.listen_in_background(self.customer_microphone, self.speech_recognition_callback_customer)

        print("[WCM2] Call started")

    def end_call(self):
        self.stop_listening_salesperson(wait_for_stop=False)
        sleep(1)
        self.stop_listening_customer(wait_for_stop=False)
        

    def recognize_faster_whisper(self, audio_data, model="medium.en", device="cuda", compute_type ="auto", cpu_threads=0):
        assert isinstance(audio_data, sr.AudioData)
        import numpy as np
        import soundfile as sf
        import io
        from faster_whisper import WhisperModel
        from tempfile import NamedTemporaryFile

        temp_file = NamedTemporaryFile().name 

        wav_data = io.BytesIO(audio_data.get_wav_data(convert_rate=16000))

        audio_model = WhisperModel(model, device = device, compute_type = compute_type , cpu_threads = cpu_threads)

        with open(temp_file, 'w+b') as f:
            f.write(wav_data.read())

        text = ""
                    
        segments, info = audio_model.transcribe(temp_file)
        for segment in segments:
            text += segment.text

        return text