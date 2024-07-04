# Interface for data processors

from abc import ABC, abstractmethod
from typing import List

from model.call_log import CallLog

class ChatProcessor(ABC):
    @abstractmethod
    def __init__(self, model_callback):
        pass

    @abstractmethod
    def process_chat(self, chat_log: List[CallLog]) -> List[str]:
        pass

    @abstractmethod
    def get_callback(self):
        pass