import text2emotion as te

from chat_processors.chat_processor import ChatProcessor

class Text2EmotionChatProcessor(ChatProcessor):
    
    def __init__(self, model_callback):
        self.model_callback = model_callback

    def process_chat(self, chat_logs):
        # Select last 3 chat logs
        chat_logs = chat_logs[-3:]
        # Get the text from the chat logs
        text = " ".join([chat_log.content for chat_log in chat_logs])
        # Get the emotions from the text
        emotions = te.get_emotion(text)
        # Get the emotion with the highest score
        emotion = max(emotions, key=emotions.get)
        # Call the model callback with the emotion
        self.model_callback([emotion])

    def get_callback(self):
        return lambda chat_logs: self.process_chat(chat_logs)