from time import sleep
from typing import List

from llm_chat_processors.llm_chat_processor import LLMChatProcessor
from llm_chat_processors.prompt_type import PromptType
from model.call_log import CallLog

# Runs on calling set_prompt, and whenever the chat log is updated, until stop is called
class LLMChatProcessorStub(LLMChatProcessor):
    
    def __init__(self):
        self.active = False
        self.enabled = False
        # Load LLM into memory here -----------------------------------

        # -------------------------------------------------------------

    def set_prompt(self, type: PromptType, chatlog, model_callback, enabled):
        self.model_callback = model_callback # Call this function to update the model with your response
        self.type = type # Use this in run() to determine what prompt to give to the llm
        self.chat_log = chatlog # List of ChatLog
        self.enabled = enabled # If enabled, llm will be prompted on chatlog update

        if type == PromptType.WARNINGS:
            self.min_chat_history = 3
            self.max_chat_history = 5
            self.prompt_method = lambda chatlog_string: None
        elif type == PromptType.TODO:
            self.min_chat_history = None
            self.max_chat_history = None
            self.prompt_method = lambda chatlog_string: None

    def chatlog_update_listener(self, chatlog):
        while self.active:
            sleep(0.1)
        self.chat_log = chatlog
        if self.enabled:
            self.run()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def run(self):
        if self.active:
            print ("LLM is already active")
        while self.active:
            sleep(0.1)
        print ("LLM not active, going ahead")
        self.active = True

        model_callback = self.model_callback
        type = self.type
        chat_log = self.chat_log
        min_chat_history = self.min_chat_history
        max_chat_history = self.max_chat_history

        if min_chat_history is not None and len(chat_log) <= min_chat_history:
            self.active = False
            return
        if max_chat_history is not None and len(chat_log) > max_chat_history:
            chat_log = chat_log[-max_chat_history:]
        chatlog_string = ""
        for chat in chat_log:
            chatlog_string += chat.speaker + ": " + chat.content + "\n"
        chatlog_string = ""
        # Run prompt_method here -----------------------------------
        sleep(5)
        if type == PromptType.WARNINGS:
            pass
        elif type == PromptType.TODO:
            model_callback("Creating to-do list...")
        # --------------------------------------------------
        self.active = False

