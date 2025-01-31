import tkinter as tk
import TKinterModernThemes as TKMT
from PIL import ImageTk, Image

from tkinter import PhotoImage
from tkinter import scrolledtext
from tkinter import ttk

from call_managers.call_manager_state import CallManagerState

import utilities.microphone_list as microphone_list
from utilities.recommendations import get_recommendation

from view.call_done_view import CallDoneView
from view.colours import Colours

class View:
    def __init__(self, master, controller):
        #master.geometry("800x1000")
        master.configure(bg=Colours.THEMED_BACKGROUND)
        self.controller = controller
        self.call_done_view = CallDoneView(master, back_view=self, controller=self.controller)

        icon=PhotoImage(file="images\\HoneyBadgerIcon.png")
        master.iconphoto(True,icon)

        self.style = ttk.Style()
        self.style.configure("Themed.TFrame", background=Colours.THEMED_BACKGROUND)
        self.style.configure("Neutral.TFrame", background=Colours.NEUTRAL_BACKGROUND)
        self.style.configure("Themed.TLabel", background=Colours.THEMED_BACKGROUND)
        self.style.configure("Neutral.TLabel", background=Colours.NEUTRAL_BACKGROUND)

        self.frame = self.controller.addFrame(
            "Main Frame",
            widgetkwargs={"style": "Themed.TFrame"})
        
        logo = Image.open("images\\HoneyBadgerIcon.png")
        logo = logo.resize((50, 50))
        logo = ImageTk.PhotoImage(logo)
        
        self.title_logo_frame = ttk.Frame(self.frame.master, style="Themed.TFrame")
        self.title_logo_frame.grid(padx=0, pady=0)

        self.logo = ttk.Label(self.title_logo_frame, image=logo, style="Themed.TLabel")
        self.logo.image = logo
        self.logo.grid(row=0, column=0, padx=10, pady=10)

        self.title = ttk.Label(self.title_logo_frame, text='Call Dashboard', style="Themed.TLabel", font=(16))
        self.title.grid(row=0, column=1, padx=10, pady=10)

        self.call_logs_frame = ttk.Frame(self.frame.master, style="Themed.TFrame")
        self.call_logs_frame.grid(padx=10, pady=10, sticky="ew")

        self.call_logs = scrolledtext.ScrolledText(self.call_logs_frame.master, bg=Colours.NEUTRAL_BACKGROUND, height = 20)
        self.call_logs.grid(padx=10, pady=10, sticky="ew")

        self.emotion_personality_recommendation_frame = tk.Frame(self.frame.master, bg=Colours.NEUTRAL_BACKGROUND)
        self.emotion_personality_recommendation_frame.grid(padx=10, pady=10, sticky="ew")

        self.emotion_personality_frame = tk.Frame(self.emotion_personality_recommendation_frame, bg=Colours.NEUTRAL_BACKGROUND)
        self.emotion_personality_frame.grid(row = 0, column = 0, padx=10, pady=10)

        self.emotion_label = tk.Label(self.emotion_personality_frame, text="Emotion:", bg=Colours.NEUTRAL_HIGHLIGHT)
        self.emotion_label.grid(row = 0, column = 0, padx=10, pady=10, sticky="ew")

        self.emotion = tk.Label(self.emotion_personality_frame, text="waiting...", bg=Colours.NEUTRAL_BACKGROUND)
        self.emotion.grid(row = 0, column = 1, padx=10, pady=10)

        self.personalities_label = tk.Label(self.emotion_personality_frame, text="Personalities:", bg=Colours.NEUTRAL_HIGHLIGHT)
        self.personalities_label.grid(row = 1, column = 0, padx=10, pady=10, sticky="ew")

        self.personalities = tk.Label(self.emotion_personality_frame, bg=Colours.NEUTRAL_BACKGROUND, text="waiting...")
        self.personalities.grid(row = 1, column = 1, padx=10, pady=10)

        self.recommendation_frame = tk.Frame(self.emotion_personality_recommendation_frame, bg=Colours.NEUTRAL_BACKGROUND)
        self.recommendation_frame.grid(row = 0, column = 1, padx=10, pady=10, sticky="ew")

        self.recommendation_label = tk.Label(self.recommendation_frame, text="Recommendation: ", bg=Colours.NEUTRAL_HIGHLIGHT)
        self.recommendation_label.grid(padx=10, pady=10)

        self.recommendation = tk.Label(self.recommendation_frame, bg=Colours.NEUTRAL_BACKGROUND, text="waiting...", wraplength=425)
        self.recommendation.grid(padx=10, pady=10, sticky="ew")

        self.warnings_frame = tk.Frame(self.frame.master, bg=Colours.NEUTRAL_BACKGROUND)
        self.warnings_frame.grid(padx=10, pady=10, sticky="ew")

        self.warnings_label = tk.Label(self.warnings_frame, text="Warnings:", bg=Colours.NEUTRAL_HIGHLIGHT)
        self.warnings_label.grid(padx=10, pady=10)

        self.warnings = tk.Label(self.warnings_frame, bg=Colours.NEUTRAL_BACKGROUND, text="waiting...", wraplength=600)
        self.warnings.grid(padx=10, pady=10, sticky="nsew")

        self.call_management_frame = tk.Frame(self.frame.master, bg=Colours.NEUTRAL_BACKGROUND)
        self.call_management_frame.grid(padx=10, pady=10, sticky="ew")

        self.device_frame = tk.Frame(self.call_management_frame, bg=Colours.NEUTRAL_BACKGROUND)
        self.device_frame.grid(row = 0, column = 0, padx=10, pady=10)

        self.salesperson_device_label = tk.Label(self.device_frame, text="Salesperson Source:", bg=Colours.NEUTRAL_BACKGROUND)
        self.salesperson_device_label.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        options = microphone_list.get_microphone_list()
        self.salesperson_device_entry = ttk.Combobox(self.device_frame, values=options, width=35)
        self.salesperson_device_entry.grid(row=1, column=1, padx=10, pady=10)
        self.salesperson_device_entry.bind("<<ComboboxSelected>>", self.handle_salesperson_device_selected)

        self.customer_device_label = tk.Label(self.device_frame, text="Customer Source:", bg=Colours.NEUTRAL_BACKGROUND)
        self.customer_device_label.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.customer_device_entry = ttk.Combobox(self.device_frame, values=options, width=35)
        self.customer_device_entry.grid(row=2, column=1, padx=10, pady=10)
        self.customer_device_entry.bind("<<ComboboxSelected>>", self.handle_customer_device_selected)

        self.call_info_frame = tk.Frame(self.device_frame, bg=Colours.NEUTRAL_BACKGROUND)
        self.call_info_frame.grid(row = 3, column = 0, padx=10, pady=10, columnspan=2, sticky="ew")

        self.salesperson_name_text = tk.StringVar(value='Salesperson Name')
        self.salesperson_name_text.trace_add('write', self.handle_salesperson_id)
        self.salesperson_name = ttk.Entry(self.call_info_frame, textvariable=self.salesperson_name_text, width=15)
        self.salesperson_name.grid(row=0, column=0, padx=10, pady=10)

        self.customer_name_text = tk.StringVar(value='Customer Name')
        self.customer_name_text.trace_add('write', self.handle_customer_id)
        self.customer_name = ttk.Entry(self.call_info_frame, textvariable=self.customer_name_text, width=15)
        self.customer_name.grid(row=0, column=1, padx=10, pady=10)

        self.customer_phone_text = tk.StringVar(value='Customer Phone')
        self.customer_phone_text.trace_add('write', self.handle_customer_phone)
        self.customer_phone = ttk.Entry(self.call_info_frame, textvariable=self.customer_phone_text, width=15)
        self.customer_phone.grid(row=0, column=2, padx=10, pady=10)

        
        
        self.button_frame = tk.Frame(self.call_management_frame, bg=Colours.NEUTRAL_BACKGROUND)
        self.button_frame.grid(row = 0, column = 1, padx=10, pady=10)

        self.call_status = ttk.Label(self.button_frame, text="Ready to begin call", style="Neutral.TLabel")
        self.call_status.grid(row=0, column=0, padx=10, pady=10)

        self.start_button = ttk.Button(self.button_frame, text="Start New Call", command=self.handle_start_call)
        self.start_button.grid(row=1, column=0, padx=10, pady=10)

        self.end_button = ttk.Button(self.button_frame, text="End Call and show To-Do", state="disabled", command=self.handle_end_call)
        self.end_button.grid(row=2, column=0, padx=10, pady=10)

    def handle_customer_id(self, _var, _indx, _mode):
        self.controller.handle_customer_id(self.customer_name_text.get())

    def handle_customer_phone(self, _var, _indx, _mode):
        self.controller.handle_customer_phone(self.customer_phone_text.get())

    def handle_salesperson_id(self, _var, _indx, _mode):
        self.controller.handle_salesperson_id(self.salesperson_name_text.get())

    def handle_salesperson_device_selected(self, event):
        selected_device = self.salesperson_device_entry.current()
        print(f"Salesperson device selected: {selected_device}")
        self.controller.handle_salesperson_device_selected(selected_device)
        

    def handle_customer_device_selected(self, event):
        selected_device = self.customer_device_entry.current()
        print(f"Customer device selected: {selected_device}")
        self.controller.handle_customer_device_selected(selected_device)
        

    def handle_start_call(self):
        self.start_button.config(state="disabled")
        self.controller.handle_start_call()
        
    def handle_end_call(self):
        self.end_button.config(state="disabled")
        self.controller.handle_end_call()

    def update(self, model):
        self.call_logs.delete('1.0', tk.END)
        self.call_logs.insert('insert', self.formatted_call_logs(model.get_call_logs()))
        self.call_logs.see("end")
        self.emotion.config(text=model.get_emotion())
        self.personalities.config(text=model.get_personalities())
        self.warnings.config(text=model.get_warnings())
        self.salesperson_device_entry.current(model.get_salesperson_sound_device_id())
        self.customer_device_entry.current(model.get_customer_sound_device_id())
        emotion = model.get_emotion()
        personalities = None
        if model.get_personalities():
            personalities = model.get_personalities()[0]
        else:
            personalities = "waiting..."
        self.recommendation.config(text=get_recommendation(emotion, personalities))

        call_status = model.get_call_state()
        if call_status is not None:
            if call_status == CallManagerState.IDLE:
                self.call_status.config(text="Ready to begin call")
            elif call_status == CallManagerState.STARTING_CALL:
                self.call_status.config(text="Starting call")
            elif call_status == CallManagerState.CALIBRATING:
                self.call_status.config(text="Calibrating, please be quiet")
            elif call_status == CallManagerState.ON_CALL:
                self.call_status.config(text="On call")
            elif call_status == CallManagerState.ENDING_CALL:
                self.call_status.config(text="Ending call")

        if call_status == CallManagerState.IDLE:
            self.start_button.config(state="normal")
            self.salesperson_device_entry.config(state="normal")
            self.customer_device_entry.config(state="normal")

        if call_status != CallManagerState.IDLE:
            self.start_button.config(state="disabled")
            self.salesperson_device_entry.config(state="disabled")
            self.customer_device_entry.config(state="disabled")

        if call_status == CallManagerState.ON_CALL:
            self.end_button.config(state="normal")

        self.call_done_view.update(model)

    def formatted_call_logs(self, call_logs):
        return "\n\n".join([str(call_log) for call_log in call_logs])
    
    def start_page(self):
        self.frame.master.grid()
    
    def go_to_call_done_view(self):
        self.frame.master.grid_forget()
        self.call_done_view.start_page()