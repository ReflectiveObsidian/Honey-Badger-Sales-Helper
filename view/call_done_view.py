import pandas as pd
import random
from datetime import datetime

import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk

import matplotlib
matplotlib.use('Agg')
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
        self.customer_personality = None
        
        tk.Label(self.frame.master, text='End-of-call summary', font=("Helvetica", 16), bg=Colours.THEMED_BACKGROUND).grid(padx=10, pady=10)

        self.emotion_graph_title = tk.Label(self.frame.master, text="Emotion Timeline", font=("Helvetica", 12), bg=Colours.THEMED_BACKGROUND)
        self.emotion_graph_title.grid(padx=10, pady=10)

        # Solution adapted from https://stackoverflow.com/questions/76375015/how-to-create-a-timeline-chart

        emotion_data = pd.DataFrame({
            "start": [pd.Timestamp("2021-01-01 09:00:00")],
            "end": [pd.Timestamp("2021-01-01 09:00:05")],
            "y": [0.5],
            "duration": [0.15],
            "status": ["None"],
        })
        emotion_legend = {"None": "#ff0000"}
        self.emotion_graph_figure, self.emotion_ax = plt.subplots(figsize=(7, 2))
        self.emotion_graph_figure.set_facecolor(Colours.THEMED_BACKGROUND)
        self.emotion_ax.set_facecolor(Colours.THEMED_BACKGROUND)
        emotion_graph_figure = self.update_emotion_timeline(emotion_data, emotion_legend, self.emotion_graph_figure, self.emotion_ax)
        self.emotion_graph = FigureCanvasTkAgg(emotion_graph_figure, master=self.frame.master)
        self.emotion_graph.draw()
        self.emotion_graph.get_tk_widget().grid(padx=10, pady=10, sticky="ew")

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

        self.notify_button = ttk.Button(self.button_frame, text='Email Summary', command=self.controller.notify)
        self.notify_button.grid(padx=10, pady=10, row=0, column=2)

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

        if model.get_personalities():
            self.customer_personality = model.get_personalities()[0]
        else:
            self.customer_personality = None

        emotion_graph_title_text = None
        if self.customer_personality is not None:
            emotion_graph_title_text = f"Emotion Timeline of Customer with Personality {self.customer_personality}"
        else:
            emotion_graph_title_text = "Emotion Timeline of Customer"
        self.emotion_graph_title.config(text=emotion_graph_title_text)
        

    def draw_emotion_timeline(self, model):
        emotion_model_data = model.get_emotion_timeline()
        print("Emotion Model Data: " + str(emotion_model_data))
        emotion_data = pd.DataFrame(emotion_model_data, columns=["status", "timestamp"])
        emotion_data["start"] = pd.to_datetime(emotion_data["timestamp"])
        emotion_data["end"] = pd.to_datetime(emotion_data["timestamp"]).shift(-1).fillna(pd.to_datetime(datetime.now()))
        emotion_data["y"] = 0.5
        emotion_data["duration"] = emotion_data["end"] - emotion_data["start"]
        emotion_legend = {emotion: f"#{random.randint(0, 0xFFFFFF):06x}" for emotion in emotion_data["status"].unique()}
        self.update_emotion_timeline(emotion_data, emotion_legend, self.emotion_graph_figure, self.emotion_ax)
        self.emotion_graph.draw()

    def formatted_call_logs(self, call_logs):
        return "\n\n".join([str(call_log) for call_log in call_logs])
    
    def update_emotion_timeline(self, df, d, emotion_graph_figure, ax):
        if df.empty:
            print("No emotions to render yet, skipping")
            return

        ax.set_ylim(0.25, 0.75)
        ax.set_yticklabels([])
        ax.yaxis.set_ticks_position("none")

        ax.set_xticks(df[["start", "end"]].stack().unique())
        ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
        ax.set_xlim(df["start"].min(), df["end"].max())
        for label in ax.get_xticklabels():
            label.set_weight("bold")
            label.set_fontname("serif")

        for s, c in d.items():
            tmp = df[df["status"] == s]
            ax.barh(tmp["y"], tmp["duration"], left=tmp["start"], height=0.2, color=d[s])

        rects = [plt.Rectangle((0, 0), 0, 0, color=c) for c in d.values()]

        ax.legend(
            rects, d.keys(), ncol=len(d.keys()), #bbox_to_anchor=(0.463, 1.25),
            frameon=False, handleheight=2, handlelength=3, handletextpad=0.5,
            prop={"weight": "bold", "family": "serif"},
        )

        return self.emotion_graph_figure
    

