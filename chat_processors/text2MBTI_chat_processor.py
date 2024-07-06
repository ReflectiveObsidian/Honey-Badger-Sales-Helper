import text2emotion as te
import pickle
import re
from sklearn.feature_extraction.text import TfidfVectorizer

from chat_processors.chat_processor import ChatProcessor

class Text2MBTIChatProcessor(ChatProcessor):
    
    def __init__(self, model_callback):
        self.model_callback = model_callback

        with open('./chat_processors/resources/MBTI/model_EI.pkl', 'rb') as file:
            self.model_EI = pickle.load(file)
        with open('./chat_processors/resources/MBTI/model_FT.pkl', 'rb') as file:
            self.model_FT = pickle.load(file)
        with open('./chat_processors/resources/MBTI/model_JP.pkl', 'rb') as file:
            self.model_JP = pickle.load(file)
        with open('./chat_processors/resources/MBTI/model_NS.pkl', 'rb') as file:
            self.model_NS = pickle.load(file)
        with open('./chat_processors/resources/MBTI/vectorizer.pkl', 'rb') as file:
            self.loaded_vectorizer = pickle.load(file)

    def process_chat(self, chat_logs):
        # Select chat logs with speaker as customer
        chat_logs = [chat_log for chat_log in chat_logs if chat_log.speaker == "Customer"]
        # Select last 3 chat logs
        chat_logs = chat_logs[-10:]
        # Get the text from the chat logs
        text = " ".join([chat_log.content for chat_log in chat_logs])
        # Get the emotions from the text
        
        replacements = [
            (r"(http.*?\s)", " "),
            (r"[^\w\s]", " "),
            (r"\_", " "),
            (r"\d+", " ")]

        for old, new in replacements:
            text = re.sub(old,new, text)

        userInput = [text]

        userInput_Vectorized = self.loaded_vectorizer.transform(userInput)

        # Product the result for four axes
        prediction_EI = self.model_EI.predict(userInput_Vectorized)
        prediction_NS = self.model_NS.predict(userInput_Vectorized)
        prediction_FT = self.model_FT.predict(userInput_Vectorized)
        prediction_JP = self.model_JP.predict(userInput_Vectorized)

        # convert the prediction result from 1 and 0 to letters
        output_EI = 'E' if prediction_EI == 0 else "I"
        output_NS = 'N' if prediction_NS == 0 else "S"
        output_FT = 'F' if prediction_FT == 0 else "T"
        output_JP = 'J' if prediction_JP == 0 else "P"

        prediction_text=f'{output_EI}{output_NS}{output_FT}{output_JP}'

        self.model_callback([prediction_text])

    def get_callback(self):
        return lambda chat_logs: self.process_chat(chat_logs)