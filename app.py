import queue
import threading
import TKinterModernThemes as TKMT
from urllib.parse import quote
import webbrowser

from llm_chat_processors.prompt_type import PromptType
from model.model import Model
from view.view import View
from utilities.save_data import SaveData

# LLM Chat Processors
from llm_chat_processors.stub.llm_chat_processor_stub import LLMChatProcessorStub
from llm_chat_processors.non_finetuned_llm_chat_processor import NonFinetunedLLMChatProcessor

# Call Managers
from call_managers.stub.call_stub import CallStub
from call_managers.whisper_call_manager import WhisperCallManager
from call_managers.whisper_call_manager_2 import WhisperCallManager2
from call_managers.demo_sales_call_manager import DemoSalesCallManager

# Chat Processors
from chat_processors.stub.emotion_stub import EmotionStub
from chat_processors.text2emotion_chat_processor import Text2EmotionChatProcessor
from chat_processors.text2MBTI_chat_processor import Text2MBTIChatProcessor

class Controller(TKMT.ThemedTKinterFrame):
    def __init__(self):
        super().__init__("Honey Badger Sales Helper", "sun-valley", "light")
        self.root.resizable(width=False, height=False)
        self.view = View(self.root, self)
        self.model = Model(self.view)
        self.call_manager = None

        #self.llm_chat_processor = LLMChatProcessorStub() # Comment out and change stub to actual
        self.llm_chat_processor = NonFinetunedLLMChatProcessor()
        llm_chat_processor_callback = lambda calllog: threading.Thread(target=self.llm_chat_processor.chatlog_update_listener, args=[calllog]).start()
        self.model.set_call_log_observer(llm_chat_processor_callback)

        #self.emotion_processor = EmotionStub(lambda emotion: self.model.set_emotion(emotion)) # Stub
        self.emotion_processor = Text2EmotionChatProcessor(lambda emotion: self.model.set_emotion(emotion))
        emotion_processor_callback = self.emotion_processor.get_callback()
        self.model.set_call_log_observer(emotion_processor_callback)

        #self.personalities_processor = EmotionStub(lambda personalities: self.model.set_personalities(personalities))
        self.personalities_processor = Text2MBTIChatProcessor(lambda personalities: self.model.set_personalities(personalities))
        personalities_processor_callback = self.personalities_processor.get_callback()
        self.model.set_call_log_observer(personalities_processor_callback)        

        salesperson_device_id_callback = lambda: self.model.get_salesperson_sound_device_id()
        customer_device_id_callback = lambda: self.model.get_customer_sound_device_id()
        '''self.call_manager = CallStub(
            lambda call_log: self.model.add_call_log(call_log),
            salesperson_device_id_callback,
            customer_device_id_callback) # To Replace'''
        ''' self.call_manager = WhisperCallManager(
            lambda call_log: self.model.add_call_log(call_log),
            salesperson_device_id_callback,
            customer_device_id_callback)'''
        self.call_manager = WhisperCallManager2(
            lambda call_log: self.model.add_call_log(call_log),
            salesperson_device_id_callback,
            customer_device_id_callback)
        '''self.call_manager = DemoSalesCallManager(
            lambda call_log: self.model.add_call_log(call_log),
            salesperson_device_id_callback,
            customer_device_id_callback)'''

    def handle_start_call(self):
        self.model.initialise()

        #self.call_manager.start_call()
        self.call_manager_thread = threading.Thread(target=self.call_manager.start_call)
        self.call_manager_thread.start()

        self.llm_chat_processor.set_prompt(PromptType.WARNINGS, self.model.get_call_logs(), lambda todo: self.model.set_warnings(todo), True)

    def handle_end_call(self):
        if self.call_manager is not None:
            self.call_manager.end_call()
        self.generate_end_call_items()
        self.view.call_done_view.draw_emotion_timeline(self.model)
        

    def generate_end_call_items(self):
        print("calling summary generation")
        self.llm_chat_processor.set_prompt(PromptType.SUMMARY, self.model.get_call_logs(), lambda todo: self.model.set_summary(todo), False)
        self.llm_chat_processor_thread = threading.Thread(target=self.llm_chat_processor.run)
        self.llm_chat_processor_thread.start()
        print("calling todo generation")
        self.llm_chat_processor.set_prompt(PromptType.TODO, self.model.get_call_logs(), lambda todo: self.model.set_todo_list(todo), False)
        self.llm_chat_processor_thread = threading.Thread(target=self.llm_chat_processor.run)
        self.llm_chat_processor_thread.start()

    def save_conversation(self):
        conversation = self.generate_call_summary()
        SaveData.save(conversation)

    def notify(self):
        email = ""
        subject = "Sales call with " + self.model.get_customer_id() + " by " + self.model.get_salesperson_id()
        body = self.generate_call_summary()

        mailto_link = f"mailto:{quote(email)}?subject={quote(subject)}&body={quote(body)}"
        webbrowser.open(mailto_link)

    def generate_call_summary(self):
        customer_id = self.model.get_customer_id()
        customer_phone = self.model.get_customer_phone()
        salesperson_id = self.model.get_salesperson_id()
        todo = self.model.get_todo_list()
        summary = self.model.get_summary()

        summary = f"Customer ID: {customer_id}\nCustomer Phone: {customer_phone}\nSalesperson ID: {salesperson_id}\n\nSummary: \n{summary}\n\nTodo: \n{todo}\n"

        return summary


    def handle_salesperson_device_selected(self, device_id):
        self.model.set_salesperson_sound_device_id(device_id)

    def handle_customer_device_selected(self, device_id):
        self.model.set_customer_sound_device_id(device_id)

    def handle_customer_id(self, customer_id):
        self.model.set_customer_id(customer_id)

    def handle_customer_phone(self, customer_phone):
        self.model.set_customer_phone(customer_phone)

    def handle_salesperson_id(self, salesperson_id):
        self.model.set_salesperson_id(salesperson_id)
        
if __name__ == "__main__":
    app = Controller()
    app.run()