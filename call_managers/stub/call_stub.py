# When started, periodically calls the add_call_log_callback with a CallLog object

from datetime import datetime
from time import sleep

from call_managers.call_manager import CallManager
from model.call_log import CallLog


class CallStub(CallManager):
    def __init__(self, add_call_log_callback, salesperson_device_id_callback, customer_device_id_callback):
        # add_call_log_callback is a function that takes a CallLog object as an argument
        # This updates the model with the new call log
        self.add_call_log_callback = add_call_log_callback
        self.salesperson_device_id_callback = salesperson_device_id_callback
        self.customer_device_id_callback = customer_device_id_callback
        self.inCall = False

    def start_call(self):
        self.inCall = True
        # Generated with ChatGPT
        sales_agent_quotes = [
            "Good morning! I've got the most exquisite wildflower honey that you're going to love.",
            "Our honey comes straight from the happiest bees in the valley, producing the sweetest nectar you've ever tasted.",
            "Imagine drizzling this golden goodness on fresh berries or warm toast—it's a taste of pure bliss!",
            "Oh, I understand. Perhaps you'd like to try a sample first?",
            "Thank you so much! I'll get that order processed right away. You won't regret it!",
            "Absolutely, we have wildflower, clover, and even lavender-infused honey. Take your pick!",
            "Fantastic choice! You're going to love it. Thank you for choosing us!",
            "Haha, I promise it's worth the buzz! I'll make sure it's the best honey you've ever had."
        ]
        # Generated with ChatGPT
        badger_quotes = [
            "Hmm, honey, you say? What makes your honey so special?",
            "I'm not sure if honey is my thing, but tell me more.",
            "I'll consider it, but I'll need to think it over. Can you send me more information?",
            "Alright, you've piqued my interest. How do I place an order?",
            "Wait, does your honey come in different flavors? I'm not sure what to choose.",
            "I'll take a jar of the clover honey. Looking forward to tasting it!",
            "If this honey isn't as good as you say, I might just come looking for those happy bees!",
        ]

        speaker = 'Mink'
        badger_content_id = 0
        mink_content_id = 0
    
        while self.inCall == True:
            if speaker == 'Mink':
                content = sales_agent_quotes[mink_content_id]
            else:
                content = badger_quotes[badger_content_id]
            timestamp = datetime.now()
            new_speaker = ""
            if speaker == "Mink":
                new_speaker = "Customer"
            else:
                new_speaker = "Salesperson"
            call_log = CallLog(timestamp, new_speaker, content)
            self.add_call_log_callback(call_log)

            if speaker == 'Mink':
                speaker = 'Badger'
                mink_content_id += 1
                if badger_content_id == len(badger_quotes):
                    speaker = 'Mink'
                    mink_content_id = 0
                    badger_content_id = 0
                    sleep(10)
            else:
                speaker = 'Mink'
                badger_content_id += 1
                if mink_content_id == len(sales_agent_quotes):
                    speaker = 'Badger'
                    badger_content_id = 0
                    mink_content_id = 0
                    sleep(10)

            sleep(1.5)

            

    def end_call(self):
        self.inCall = False