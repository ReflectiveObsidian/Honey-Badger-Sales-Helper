from random import randint

from chat_processors.chat_processor import ChatProcessor

class EmotionStub(ChatProcessor):
    
    def __init__(self, model_callback):
        # Model callback is a function that takes in a list of strings
        # It updates the model with the new emotion
        self.model_callback = model_callback
        self.emotions = {
            0: "Neutral",
            1: "Happy",
            2: "Sad",
            3: "Angry",
            4: "Surprised",
            5: "Disgusted",
            6: "Fearful"
        }

    def process_chat(self, chat_logs):
        # chat_logs is a list of CallLog objects in chronological order
        # Update the emotion using model callback when done processing the text
        self.model_callback([self.emotions[randint(0, 6)]])

    def get_callback(self):
        return lambda chat_logs: self.process_chat(chat_logs)