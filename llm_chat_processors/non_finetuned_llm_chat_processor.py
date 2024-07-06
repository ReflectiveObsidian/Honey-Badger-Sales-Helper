from llama_cpp import Llama
from time import sleep
from typing import List

from llm_chat_processors.llm_chat_processor import LLMChatProcessor
from llm_chat_processors.prompt_type import PromptType
from model.call_log import CallLog

# Runs on calling set_prompt, and whenever the chat log is updated, until stop is called
class NonFinetunedLLMChatProcessor(LLMChatProcessor):
    
    def __init__(self):
        self.active = False
        self.enabled = False
        # Load LLM into memory here -----------------------------------
        model_path = "llm_chat_processors/llm_models/Phi-3-mini-4k-instruct-q4.gguf"
        model_kwargs = {
                "n_ctx":4096,    # Context length to use
                "n_threads":4,   # Number of CPU threads to use
                "n_gpu_layers": 33, # Number of model layers to offload to GPU. Set to 0 if only using CPU
        }
        self.llm = Llama(model_path = model_path, **model_kwargs)
        self.mode = 3
        
        # -------------------------------------------------------------

    def set_prompt(self, type: PromptType, chatlog, model_callback, enabled):
        print("Setting prompt")
        self.model_callback = model_callback # Call this function to update the model with your response
        self.type = type # Use this in run() to determine what prompt to give to the llm
        self.chat_log = chatlog # List of ChatLog
        self.enabled = enabled # If enabled, llm will be prompted on chatlog update
        if type == PromptType.WARNINGS:
            generation_kwargs = {
                "max_tokens":100,
                "stop": "<|assistant|>",
                "echo":False,
                "top_k":1
            }
            
            if self.mode == 1:
                self.prompt_method = lambda chatlog_string: self.llm(self.generate_prompt(
                        "You are a salesperson.",
                        "Based on this chat history, do you think you have exaggerated or given empty promises? Respond only with EXAGGERATION and/or EMPTY PROMISE, separated by commas. Do not include anything else.\n" + chatlog_string),
                    **generation_kwargs
                )
            elif self.mode == 2:
                self.prompt_method = lambda chatlog_string: self.llm(self.generate_prompt(
                    "You are a salesperson.",
                    "Based on this chat history, do you think you have exaggerated or given empty promises? Respond only with EXAGGERATION and/or EMPTY PROMISE, separated by commas. Use the format <warning type> # <explanation>.\n" + chatlog_string),
                **generation_kwargs
                )
            elif self.mode == 3:
                self.prompt_method = lambda chatlog_string: self.llm(self.generate_prompt(
                    "You are a salesperson's supervisor.",
                    chatlog_string + "\nDid the salesperon exaggerate or give an empty promise? Respond with NONE, EXAGGERATION or EMPTY PROMISE. Use the format <warning type>: <relevant quote>. For example: EXAGGERATION: \"these pills will comeletely cure your pain\"\n"),
                **generation_kwargs
                )
            self.min_chat_history = 3
            self.max_chat_history = 5
            print("prompting warnings")
        elif type == PromptType.TODO:
            generation_kwargs = {
                "max_tokens":100000,
                "stop": "<|assistant|>",
                "echo":False,
                "top_k":1
            }
            self.prompt_method = lambda chatlog_string: self.llm(self.generate_prompt(
                    "You are a salesperson.",
                    "Create a short to-do list for following up with the customer based on your conversation, stated below. Each item should be a sentence long. Respond only with the todo list, one item per line. Do not include anything else.\n" + chatlog_string),
                **generation_kwargs
            )
            self.min_chat_history = None
            self.max_chat_history = None
        elif type == PromptType.SUMMARY:
            generation_kwargs = {
                "max_tokens":100000,
                "stop": "<|assistant|>",
                "echo":False,
                "top_k":1
            }
            self.prompt_method = lambda chatlog_string: self.llm(self.generate_prompt(
                    "You are a salesperson.",
                    "Create a short summary of your conversation with the customer.\n" + chatlog_string),
                **generation_kwargs
            )
            self.min_chat_history = None
            self.max_chat_history = None


    def generate_prompt(self, role: str, question: str) -> str:
        return f"<|system|>\n{role}<|end|>\n{question}<|end|>\n<|assistant|>"

    def chatlog_update_listener(self, chatlog):
        while self.active:
            return
        self.chat_log = chatlog
        if self.enabled:
            self.run()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def run(self):
        model_callback = self.model_callback
        type = self.type
        chat_log = self.chat_log
        min_chat_history = self.min_chat_history
        max_chat_history = self.max_chat_history
        prompt_method = self.prompt_method

        if self.active:
            print ("LLM is already active")
        while self.active:
            sleep(0.1)
        print ("LLM not active, going ahead")
        self.active = True

        # PROMPT LLM HERE -----------------------------------
        if min_chat_history is not None and len(chat_log) <= min_chat_history:
            self.active = False
            return
        if max_chat_history is not None and len(chat_log) > max_chat_history:
            chat_log = chat_log[-max_chat_history:]
        chatlog_string = ""
        for chat in chat_log:
            chatlog_string += chat.speaker + ": " + chat.content + "\n"
        if type == PromptType.WARNINGS:
            output = prompt_method(chatlog_string)["choices"][0]["text"]
            if self.mode == 1:
                model_callback(output)
            if self.mode == 2:
                warnings = ""
                for line in output.split("\n"):
                    if line == "":
                        continue
                    warning, explanation = line.split("#")
                    if warnings != "":
                        warnings += ", "
                    warnings += warning.strip()
                model_callback(warnings)
            if self.mode == 3:
                if "NONE" in output.capitalize():
                     model_callback("Good Job!")
                else:
                    model_callback(output)
        elif type == PromptType.TODO:
            model_callback("Creating to-do list...")
            output = prompt_method(chatlog_string)["choices"][0]["text"]
            model_callback(output)
        elif type == PromptType.SUMMARY:
            model_callback("Creating summary...")
            output = prompt_method(chatlog_string)["choices"][0]["text"]
            model_callback(output)
        # --------------------------------------------------
        self.active = False

