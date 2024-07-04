# When started, periodically calls the add_call_log_callback with a CallLog object
import io
import os
import speech_recognition as sr
import nltk
from nltk.tokenize import sent_tokenize

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from datetime import datetime, timedelta
from queue import Queue
from tempfile import NamedTemporaryFile
from time import sleep
from sys import platform
from faster_whisper import WhisperModel

from call_managers.call_manager import CallManager
from model.call_log import CallLog


class WhisperCallManager(CallManager):
    def __init__(self, add_call_log_callback):
        self.add_call_log_callback = add_call_log_callback
        self.inCall = False

        model = "medium.en"
        device = "cuda"
        compute_type = "auto"
        threads = 0
        energy_threshold = 1000
        self.record_timeout = 2
        self.phrase_timeout = 2

        self.phrase_time = None
        self.last_sample = bytes()
        self.data_queue = Queue()
        self.recorder = sr.Recognizer()
        self.recorder.energy_treshole = energy_threshold
        self.recorder.dynamic_energy_threshold = False

        self.source = sr.Microphone(sample_rate=16000)
        
        nltk.download('punkt')
        self.audio_model = WhisperModel(model, device = device, compute_type = compute_type , cpu_threads = threads)

        self.temp_file = NamedTemporaryFile().name 
        self.transcription = ['']

        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source, duration=1)

    def record_callback(self, _, audio:sr.AudioData) -> None:
        """
        Threaded callback function to recieve audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        # Grab the raw bytes and push it into the thread safe queue.
        data = audio.get_raw_data()
        self.data_queue.put(data)


    def start_call(self):
        self.inCall = True
        
        self.recorder.listen_in_background(self.source, self.record_callback, phrase_time_limit=self.record_timeout)        
    
        while self.inCall == True:

            now = datetime.utcnow()
            # Pull raw recorded audio from the queue.
            if not self.data_queue.empty():
                phrase_complete = False
                # If enough time has passed between recordings, consider the phrase complete.
                # Clear the current working audio buffer to start over with the new data.
                if self.phrase_time and now - self.phrase_time > timedelta(seconds=self.phrase_timeout):
                    self.last_sample = bytes()
                    phrase_complete = True
                # This is the last time we received new audio data from the queue.
                self.phrase_time = now

                # Concatenate our current audio data with the latest audio data.
                while not self.data_queue.empty():
                    data = self.data_queue.get()
                    self.last_sample += data

                # Use AudioData to convert the raw data to wav data.
                audio_data = sr.AudioData(self.last_sample, self.source.SAMPLE_RATE, self.source.SAMPLE_WIDTH)
                wav_data = io.BytesIO(audio_data.get_wav_data())

                # Write wav data to the temporary file as bytes.
                with open(self.temp_file, 'w+b') as f:
                    f.write(wav_data.read())

                # Read the transcription.
                text = ""
                    
                segments, info = self.audio_model.transcribe(self.temp_file)
                for segment in segments:
                    text += segment.text
                #text = result['text'].strip()

                # If we detected a pause between recordings, add a new item to our transcripion.
                # Otherwise edit the existing one.
                if phrase_complete:
                    self.transcription.append(text)
                else:
                    self.transcription[-1] = text

                call_log = CallLog(now, "speaker", self.transcription[-1])
                self.add_call_log_callback(call_log)

            sleep(2)

            

    def end_call(self):
        self.inCall = False