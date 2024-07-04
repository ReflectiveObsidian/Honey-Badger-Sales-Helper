# Interface for llm chat processors

from abc import ABC, abstractmethod
from typing import List

from llm_chat_processors.prompt_type import PromptType
from model.call_log import CallLog

class LLMChatProcessor(ABC):
    @abstractmethod
    def __init__(self):
        pass

    # Passes a string into the model callback
    @abstractmethod
    def set_prompt(self, type: PromptType, model, model_callback, enabled):
        pass

    @abstractmethod
    def chatlog_update_listener(self, model):
        pass

    @abstractmethod
    def enable(self):
        pass

    @abstractmethod
    def disable(self):
        pass

    @abstractmethod
    def run(self):
        pass