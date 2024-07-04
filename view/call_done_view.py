import tkinter as tk

from tkinter import scrolledtext
from tkinter import ttk

from view.colours import Colours

class CallDoneView:
    def __init__(self, master=None, back_view=None, controller=None):
        self.master = master
        self.back_view = back_view
        self.controller = controller
        #self.frame = tk.Frame(self.master, bg=Colours.THEMED_BACKGROUND)
        self.style = ttk.Style()
        self.style.configure("Themed.TFrame", background=Colours.THEMED_BACKGROUND)
        self.frame = self.back_view.controller.addFrame(
            "Main Frame",
            widgetkwargs={"style": "Themed.TFrame"})
        self.frame.master.grid_forget()
        
        tk.Label(self.frame.master, text='End-of-call summary', font=("Helvetica", 16), bg=Colours.THEMED_BACKGROUND).grid(padx=10, pady=10)

        self.call_logs = scrolledtext.ScrolledText(self.frame.master, bg=Colours.NEUTRAL_BACKGROUND, height = 15)
        self.call_logs.grid(padx=10, pady=10, sticky="ew")

        self.summary = scrolledtext.ScrolledText(self.frame.master, bg=Colours.NEUTRAL_BACKGROUND, height = 10)
        self.summary.grid(padx=10, pady=10, sticky="ew")

        self.todo_list = scrolledtext.ScrolledText(self.frame.master, bg=Colours.NEUTRAL_BACKGROUND, height = 10)
        self.todo_list.grid(padx=10, pady=10, sticky="ew")

        self.button_frame = tk.Frame(self.frame.master, bg=Colours.NEUTRAL_BACKGROUND)
        self.button_frame.grid(padx=10, pady=10, sticky="ew")

        self.back_button = ttk.Button(self.button_frame, text='Go back', command=self.go_back)
        self.back_button.grid(padx=10, pady=10, row=0, column=0)

        self.save_button = ttk.Button(self.button_frame, text='Save Conversation', command=self.save_conversation)
        self.save_button.grid(padx=10, pady=10, row=0, column=1)

    def start_page(self):
        self.frame.master.grid(sticky="nsew")

    def go_back(self):
        self.frame.master.grid_forget()
        self.back_view.start_page()

    def save_conversation(self):
        self.controller.save_conversation()

    def update(self, model):
        self.call_logs.delete('1.0', tk.END)
        self.call_logs.insert('insert', self.formatted_call_logs(model.get_call_logs()))
        self.call_logs.see("end")

        self.todo_list.delete('1.0', tk.END)
        self.todo_list.insert('insert', model.get_todo_list())

        self.summary.delete('1.0', tk.END)
        self.summary.insert('insert', model.get_summary())

    def formatted_call_logs(self, call_logs):
        return "\n\n".join([str(call_log) for call_log in call_logs])
