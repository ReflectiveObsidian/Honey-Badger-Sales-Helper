# When started, periodically calls the add_call_log_callback with a CallLog object

from datetime import datetime
from time import sleep
import audioop
import speech_recognition as sr
from queue import Queue
import threading

from call_managers.call_manager import CallManager
from model.call_log import CallLog

class WhisperCallManager2(CallManager):
    def __init__(self, add_call_log_callback, salesperson_device_id_callback, customer_device_id_callback):
        # add_call_log_callback is a function that takes a CallLog object as an argument
        # This updates the model with the new call log
        self.add_call_log_callback = add_call_log_callback
        self.salesperson_device_id_callback = salesperson_device_id_callback
        self.customer_device_id_callback = customer_device_id_callback

        self.salesperson_data_queue = Queue()
        self.customer_data_queue = Queue()
        self.unified_queue = Queue()

        def callback_salesperson(recognizer, audio): 
            raw_data = audio.get_raw_data()
            energy = audioop.rms(raw_data, audio.sample_width)
            if energy > self.salesperson_recognizer.energy_threshold:
                print("salesperson energy is: ", energy)
                print("salesperson energy threshold is ", self.salesperson_recognizer.energy_threshold)
                self.unified_queue.put(["Salesperson", audio])

        self.speech_recognition_callback_salesperson = callback_salesperson

        def callback_customer(recognizer, audio):
            raw_data = audio.get_raw_data()
            energy = audioop.rms(raw_data, audio.sample_width)
            if energy > self.customer_recognizer.energy_threshold:
                print("customer energy is: ", energy)
                print("customer energy threshold is ", self.customer_recognizer.energy_threshold)
                self.unified_queue.put(["Customer", audio])

        self.speech_recognition_callback_customer = callback_customer

        self.salesperson_recognizer = sr.Recognizer()
        self.customer_recognizer = sr.Recognizer()
        self.salesperson_recognizer.dynamic_energy_threshold = False
        self.customer_recognizer.dynamic_energy_threshold = False
        self.salesperson_recognizer.pause_threshold = 2
        self.customer_recognizer.pause_threshold = 2

    def salesperson_transcriber(self, recognizer):
        while self.call:
            if not self.salesperson_data_queue.empty(): 
                audio = self.salesperson_data_queue.get()
                print("transcribing salesperson")
                start = datetime.now()
                result = self.recognize_faster_whisper(audio)
                #result = self.salesperson_recognizer.recognize_whisper(audio, language = "english")
                end = datetime.now()
                time_completion = end-start
                print(f"finish transcribing salesperson {time_completion}")
                self.add_call_log_callback(CallLog(datetime.now(), "Salesperson", result))
                sleep(0.1)

    def customer_transcriber(self, recognizer):
        while self.call: 
            if not self.customer_data_queue.empty():
                audio = self.customer_data_queue.get()
                print("transcribing customer")
                start = datetime.now()
                result = self.recognize_faster_whisper(audio)
                #result = self.customer_recognizer.recognize_whisper(audio, language = "english")
                end = datetime.now()
                time_completion = end-start
                print(f"finish transcribing customer {time_completion}")
                self.add_call_log_callback(CallLog(datetime.now(), "Customer", result))
                sleep(0.1)

    def unified_transcriber(self):
        while self.call: 
            if not self.unified_queue.empty():
                cust_audio = None
                sales_audio = None
                while not self.unified_queue.empty():
                    who, audio = self.unified_queue.get()
                    raw_audio = audio.get_raw_data()
                    print("Unified Transcribe: ", who)
                    if who == "Customer":
                        cust_raw_audio = cust_raw_audio + raw_audio
                    elif who == "Salesperson":
                        sales_raw_audio = sales_raw_audio + raw_audio
                start = datetime.now()
                if cust_raw_audio:
                    cust_audio = sr.AudioData(cust_raw_audio, audio.sample_rate, audio.sample_width)
                    result = self.recognize_faster_whisper(cust_audio)
                    self.add_call_log_callback(CallLog(datetime.now(), "Customer", result))
                if sales_raw_audio:
                    sales_audio = sr.AudioData(sales_raw_audio, audio.sample_rate, audio.sample_width)
                    result = self.recognize_faster_whisper(sales_audio)
                    self.add_call_log_callback(CallLog(datetime.now(), "Salesperson", result))
                #result = self.recognize_faster_whisper(audio)
                #result = self.customer_recognizer.recognize_whisper(audio, language = "english")
                end = datetime.now()
                time_completion = end-start
                print(f"unified transcribe {time_completion}")
                #self.add_call_log_callback(CallLog(datetime.now(), who, result))


    def start_call(self):

        self.call = True

        print("[WCM2] call start fn")

        device_index_salesperson = self.salesperson_device_id_callback()
        self.salesperson_microphone = sr.Microphone(device_index= device_index_salesperson)
        print("[WCM2] salesperson device index: ", device_index_salesperson)

        device_index_customer = self.customer_device_id_callback()
        self.customer_microphone = sr.Microphone(device_index= device_index_customer)
        print("[WCM2] customer device index: ", device_index_customer)
        
        print("calibrating devices... please do not speak during this time")
        print("[WCM2] 1")
        with self.salesperson_microphone as source:
            self.salesperson_recognizer.adjust_for_ambient_noise(source, duration = 3)
        print("[WCM2] 1.1")
        with self.customer_microphone as source:
            self.customer_recognizer.adjust_for_ambient_noise(source, duration = 3)

        print("finish calibrating devices")

        self.salesperson_recognizer.energy_threshold += 100
        self.customer_recognizer.energy_threshold += 100

        print(f"salesperson energy threshold is{self.salesperson_recognizer.energy_threshold}")
        print(f"customer energy threshold is{self.customer_recognizer.energy_threshold}")

        print("[WCM2] 2")
        # Starts listening and reutrns a function to stop listening
        print("starting salesperson mic")
        self.stop_listening_salesperson = self.salesperson_recognizer.listen_in_background(self.salesperson_microphone, self.speech_recognition_callback_salesperson)
        sleep(1)
        print("starting customer mic")
        self.stop_listening_customer = self.customer_recognizer.listen_in_background(self.customer_microphone, self.speech_recognition_callback_customer)

        #salesperson_transcriber_thread = threading.Thread(target=self.salesperson_transcriber, args=(self.salesperson_recognizer,))
        #salesperson_transcriber_thread.start()
        #sleep(0.1)
        #customer_transcriber_thread = threading.Thread(target=self.customer_transcriber, args=(self.customer_recognizer,))
        #customer_transcriber_thread.start()

        unified_transcriber_thread = threading.Thread(target=self.unified_transcriber)
        unified_transcriber_thread.start()

        print("[WCM2] Call started")


    def end_call(self):
        self.stop_listening_salesperson(wait_for_stop=False)
        sleep(1)
        self.stop_listening_customer(wait_for_stop=False)
        

    def recognize_faster_whisper(self, audio_data, model="large-v3", device="gpu", compute_type ="auto", cpu_threads=0):
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
                    
        segments, info = audio_model.transcribe(temp_file, language = "en")
        for segment in segments:
            text += segment.text

        return text