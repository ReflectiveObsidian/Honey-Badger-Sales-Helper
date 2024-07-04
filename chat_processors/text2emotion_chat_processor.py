import text2emotion as te

from chat_processors.chat_processor import ChatProcessor

class Text2EmotionChatProcessor(ChatProcessor):
    
    def __init__(self, model_callback):
        self.model_callback = model_callback
        from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
        # Load the model and tokenizer from the local directory
        tokenizer = AutoTokenizer.from_pretrained("SamLowe/roberta-base-go_emotions")
        model = AutoModelForSequenceClassification.from_pretrained("SamLowe/roberta-base-go_emotions")
        self.classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, top_k=None)

    def process_chat(self, chat_logs):
        # Select last 3 chat logs
        chat_logs = chat_logs[-3:]
        # Get the text from the chat logs
        text = " ".join([chat_log.content for chat_log in chat_logs])
        # Get the emotions from the text
        emotions = self.classifier(text)
        # Get the emotion with the highest score
        emotion = max(emotions[0], key=lambda x: x['score'])
        # Call the model callback with the emotion
        self.model_callback([emotion['label']])

    def get_callback(self):
        return lambda chat_logs: self.process_chat(chat_logs)