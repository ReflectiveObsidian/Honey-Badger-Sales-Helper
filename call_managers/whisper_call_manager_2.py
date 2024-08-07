# When started, periodically calls the add_call_log_callback with a CallLog object

from datetime import datetime
from time import sleep
import audioop
import speech_recognition as sr
from queue import Queue
import threading

from call_managers.call_manager_state import CallManagerState
from call_managers.call_manager import CallManager
from model.call_log import CallLog

class WhisperCallManager2(CallManager):
    def __init__(self, add_call_log_callback, salesperson_device_id_callback, customer_device_id_callback, call_state_callback):
        # add_call_log_callback is a function that takes a CallLog object as an argument
        # This updates the model with the new call log
        self.add_call_log_callback = add_call_log_callback
        self.salesperson_device_id_callback = salesperson_device_id_callback
        self.customer_device_id_callback = customer_device_id_callback
        self.call_state_callback = call_state_callback

        self.file_count = 1
        self.set_state(CallManagerState.IDLE)

        self.salesperson_data_queue = Queue()
        self.customer_data_queue = Queue()
        
        def callback_salesperson(recognizer, audio): 
            raw_data = audio.get_raw_data()
            energy = audioop.rms(raw_data, audio.sample_width)
            if energy > self.salesperson_recognizer.energy_threshold:
                print("salesperson energy is: ", energy)
                print("salesperson energy threshold is ", self.salesperson_recognizer.energy_threshold)
                self.salesperson_data_queue.put([datetime.now(), audio])

        self.speech_recognition_callback_salesperson = callback_salesperson

        def callback_customer(recognizer, audio):
            raw_data = audio.get_raw_data()
            energy = audioop.rms(raw_data, audio.sample_width)
            if energy > self.customer_recognizer.energy_threshold:
                print("customer energy is: ", energy)
                print("customer energy threshold is ", self.customer_recognizer.energy_threshold)
                self.customer_data_queue.put([datetime.now(), audio])

        self.speech_recognition_callback_customer = callback_customer

        self.salesperson_recognizer = sr.Recognizer()
        self.customer_recognizer = sr.Recognizer()
        self.salesperson_recognizer.dynamic_energy_threshold = False
        self.customer_recognizer.dynamic_energy_threshold = False

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
            priority = self.determine_priority()
            who = None
            raw_audio = None
            count = None
            sample_rate = None
            sample_width = None
            if priority == "Salesperson":
                who = "Salesperson"
                count = self.salesperson_data_queue.qsize()
                time, audio = self.salesperson_data_queue.get()
                raw_audio = audio.get_raw_data()
                sample_rate = audio.sample_rate
                sample_width = audio.sample_width
                while self.salesperson_data_queue.qsize() > 0:
                    time, audio = self.salesperson_data_queue.get()
                    raw_audio += audio.get_raw_data()
            elif priority == "Customer":
                who = "Customer"
                count = self.customer_data_queue.qsize()
                time, audio = self.customer_data_queue.get()
                raw_audio = audio.get_raw_data()
                sample_rate = audio.sample_rate
                sample_width = audio.sample_width
                while self.customer_data_queue.qsize() > 0:
                    time, audio = self.customer_data_queue.get()
                    raw_audio += audio.get_raw_data()
            else:
                sleep(0.1)
                continue
            batched_audio = sr.AudioData(raw_audio, sample_rate, sample_width)
            print("Unified Transcribe: ", who, " has ", count, " in queue, transcribing...")
            start = datetime.now()

            wav_data = batched_audio.get_wav_data(convert_rate=16000)
            with open(f"audio_files/{who}_audio_{self.file_count}.wav", "wb") as f:
                f.write(wav_data)
            self.file_count += 1

            result = self.recognize_faster_whisper(batched_audio)
            #result = self.customer_recognizer.recognize_whisper(batched_audio, language = "english")
            end = datetime.now()
            time_completion = end-start
            print(f"finish transcribing " + who + f" {time_completion}")
            self.add_call_log_callback(CallLog(datetime.now(), who, result))

    def determine_priority(self):
        if self.salesperson_data_queue.empty() and not self.customer_data_queue.empty():
            return "Customer"
        elif not self.salesperson_data_queue.empty() and self.customer_data_queue.empty():
            return "Salesperson"
        elif not self.salesperson_data_queue.empty() and not self.customer_data_queue.empty():
            cust_time, cust_audio = self.customer_data_queue.queue[0]
            sales_time, sales_audio = self.salesperson_data_queue.queue[0]
            if cust_time < sales_time:
                return "Customer"
            else:
                return "Salesperson"
        else:
            return None

    def start_call(self):
        self.state = self.set_state(CallManagerState.STARTING_CALL)
        self.call = True

        print("[WCM2] call start fn")

        device_index_salesperson = self.salesperson_device_id_callback()
        self.salesperson_microphone = sr.Microphone(device_index= device_index_salesperson)
        print("[WCM2] salesperson device index: ", device_index_salesperson)

        device_index_customer = self.customer_device_id_callback()
        self.customer_microphone = sr.Microphone(device_index= device_index_customer)
        print("[WCM2] customer device index: ", device_index_customer)

        self.state = self.set_state(CallManagerState.CALIBRATING)
        
        print("calibrating devices... please do not speak during this time")
        print("[WCM2] 1")
        with self.salesperson_microphone as source:
            self.salesperson_recognizer.adjust_for_ambient_noise(source, duration = 3)
        print("[WCM2] 1.1")
        with self.customer_microphone as source:
            self.customer_recognizer.adjust_for_ambient_noise(source, duration = 3)

        print("finish calibrating devices")

        self.state = self.set_state(CallManagerState.STARTING_CALL)

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

        self.state = self.set_state(CallManagerState.ON_CALL)


    def end_call(self):
        self.state = self.set_state(CallManagerState.ENDING_CALL)

        self.stop_listening_salesperson(wait_for_stop=False)
        sleep(1)
        self.stop_listening_customer(wait_for_stop=False)

        while not self.salesperson_data_queue.empty() or not self.customer_data_queue.empty():
            sleep(0.1)

        self.state = self.set_state(CallManagerState.IDLE)
        

    def recognize_faster_whisper(self, audio_data, model="medium.en", device="cpu", compute_type ="auto", cpu_threads=4):
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
    
    def get_state(self):
        return self.state
    
    def set_state(self, state):
        self.state = state
        self.call_state_callback(self.state)