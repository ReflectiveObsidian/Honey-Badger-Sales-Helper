import pyaudio
import wave
import threading
from faster_whisper import WhisperModel
import os
from datetime import datetime
from call_managers.call_manager import CallManager
from model.call_log import CallLog

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 10
TEMP_FILENAME1 = "temp_output1.wav"
TEMP_FILENAME2 = "temp_output2.wav"

class WhisperCallManager(CallManager):
    def __init__(self, add_call_log_callback, salesperson_device_id_callback, customer_device_id_callback):
        self.add_call_log_callback = add_call_log_callback
        self.salesperson_device_id_callback = salesperson_device_id_callback
        self.customer_device_id_callback = customer_device_id_callback
        self.audio = pyaudio.PyAudio()
        self.audio_model = WhisperModel("medium.en", device="cuda", compute_type="auto", cpu_threads=0)
        
        self.in_call = False
        
        self.record_event1 = threading.Event()
        self.transcribe_event1 = threading.Event()
        self.record_event2 = threading.Event()
        self.transcribe_event2 = threading.Event()

    def record_audio(self, stream, frames, filename):
        print(f"Recording to {filename}...")
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        self.save_audio(frames, filename)
        print(f"Finished recording to {filename}.")

    def save_audio(self, frames, filename):
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

    def transcribe_audio(self, filename):
        if os.path.exists(filename):
            print(f"Transcribing {filename}...")
            text = ""
            segments, info = self.audio_model.transcribe(filename)
            for segment in segments:
                text += segment.text
            print(f"Transcription for {filename}: {text}")
            self.add_call_log_callback(CallLog(datetime.now(), "Whisper", text))
            os.remove(filename)  # Delete the file after transcribing

    def record_and_transcribe(self, stream, filename, record_event, transcribe_event):
        while self.in_call:
            record_event.wait()
            frames = []
            self.record_audio(stream, frames, filename)
            transcribe_event.set()
            record_event.clear()

    def start_call(self):
        self.in_call = True

        self.device_index1 = self.salesperson_device_id_callback()
        self.device_index2 = self.customer_device_id_callback()

        print("self.device_index1 is ", self.device_index1)
        print("self.device_index2 is ",self.device_index2)

        self.stream1 = self.audio.open(format=FORMAT, channels=CHANNELS,
                                       rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=self.device_index1)
        self.stream2 = self.audio.open(format=FORMAT, channels=CHANNELS,
                                       rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=self.device_index2)

        # Create threads for parallel recording and transcribing
        self.thread1 = threading.Thread(target=self.record_and_transcribe, args=(self.stream1, TEMP_FILENAME1, self.record_event1, self.transcribe_event1))
        self.thread2 = threading.Thread(target=self.record_and_transcribe, args=(self.stream2, TEMP_FILENAME2, self.record_event2, self.transcribe_event2))

        # Start threads
        self.thread1.start()
        self.thread2.start()

        # Set the initial recording events
        self.record_event1.set()
        self.record_event2.set()

        try:
            while self.in_call:
                # Wait for transcription events
                self.transcribe_event1.wait()
                self.transcribe_audio(TEMP_FILENAME1)
                self.transcribe_event1.clear()
                self.record_event1.set()

                self.transcribe_event2.wait()
                self.transcribe_audio(TEMP_FILENAME2)
                self.transcribe_event2.clear()
                self.record_event2.set()
        except KeyboardInterrupt:
            print("Stopping recording and transcription.")
            self.end_call()
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.end_call()

    def end_call(self):
        thread = threading.Thread(target=self.handle_end_call)
        thread.start()

    def handle_end_call(self):
        self.in_call = False
        print("Ending call...") 
        self.thread1.join()
        self.thread2.join()
        print("Threads joined.")
        self.stream1.stop_stream()
        self.stream1.close()
        self.stream2.stop_stream()
        self.stream2.close()
        self.audio.terminate()
        print("All streams closed and audio interface terminated.")

