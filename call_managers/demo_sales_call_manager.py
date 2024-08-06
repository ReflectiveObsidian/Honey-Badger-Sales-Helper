# When started, periodically calls the add_call_log_callback with a CallLog object

from datetime import datetime
from time import sleep

from call_managers.call_manager import CallManager
from call_managers.call_manager_state import CallManagerState
from model.call_log import CallLog


class DemoSalesCallManager(CallManager):
    def __init__(self, add_call_log_callback, salesperson_device_id_callback, customer_device_id_callback, call_state_callback):
        # add_call_log_callback is a function that takes a CallLog object as an argument
        # This updates the model with the new call log
        self.add_call_log_callback = add_call_log_callback
        self.salesperson_device_id_callback = salesperson_device_id_callback
        self.customer_device_id_callback = customer_device_id_callback
        self.call_state_callback = call_state_callback

        self.inCall = False
        self.set_state(CallManagerState.IDLE)

    def start_call(self):
        self.state = self.set_state(CallManagerState.STARTING_CALL)
        self.inCall = True
        # Generated with ChatGPT
        sales_agent_quotes = [
            "Good day! This is Honey Badger Corp, and I’m thrilled to introduce you to our exquisite range of honey products to use in your restaurant.",
            "Our honey is sourced from local, happy bees in pristine wildflower meadows. They collect nectar from sun-kissed blossoms, creating the best symphony of flavours you have ever tasted!",
            "We have a range of honey flavours. From the golden ambrosia of our Wildflower Blend to the robust intensity of our Buckwheat Reserve, there’s a jar for every dish. Plus, our Creamed Honey—a velvety, spreadable delight—is perfect for adding a touch of natural sweetness to your gourmet dishes.",
            "Of course, what is your address?",
            "Absolutely, see you in 2 days!",
        ]
        # Generated with ChatGPT
        badger_quotes = [
            "Oh, really? What sets your honey apart?",
            "Hmm, I'll need to think it over. What kinds of honey do you have?",
            "Sure, could you come down to our restaurant to introduce us to your honey selection?",
            "Our restaurant is at 42 Honeycomb Lane. I'm available on Saturday. Would that be a good time?",
        ]

        speaker = 'Customer'
        badger_content_id = 0
        mink_content_id = 0

        self.state = self.set_state(CallManagerState.ON_CALL)
    
        while self.inCall == True:
            if speaker == 'Customer':
                content = sales_agent_quotes[mink_content_id]
            else:
                content = badger_quotes[badger_content_id]
            timestamp = datetime.now()
            call_log = CallLog(timestamp, speaker, content)
            self.add_call_log_callback(call_log)

            if speaker == 'Customer':
                speaker = 'Salesperson'
                mink_content_id += 1
                if badger_content_id == len(badger_quotes):
                    speaker = 'Customer'
                    mink_content_id = 0
                    badger_content_id = 0
                    sleep(10)
            else:
                speaker = 'Customer'
                badger_content_id += 1
                if mink_content_id == len(sales_agent_quotes):
                    speaker = 'Salesperson'
                    badger_content_id = 0
                    mink_content_id = 0
                    sleep(10)

            sleep(5)
        self.state = self.set_state(CallManagerState.IDLE)

    def end_call(self):
        self.state = self.set_state(CallManagerState.ENDING_CALL)
        self.inCall = False

    def get_state(self):
        return self.state
    
    def set_state(self, state):
        self.state = state
        self.call_state_callback(self.state)