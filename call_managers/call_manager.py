# Interface for the call manager

from abc import ABC, abstractmethod

class CallManager:
    @abstractmethod
    def __init__(self, add_call_log, salesperson_device_id_callback, customer_device_id_callback):
        pass

    @abstractmethod
    def start_call(self):
        pass

    @abstractmethod
    def end_call(self):
        pass