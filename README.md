<img src="images/HoneyBadgerIcon.png" alt="drawing" width="200"/>

# Honey-Badger-Sales-Helper
Honey Badger Sales Helper is a client app for sales agents that helps them maintain efficiency during calls.

# Features
- Recording of customer information
- Live transcription of salesperson and customer
- Realtime analysis of customer emotion and personality
- Realtime alerts for inappropriate statements
- Summarises the sales call and creates a to-do list
- Option to save or email a record of the sales call

# Installation steps
- Download and install python 3.12 from https://www.python.org/downloads/
    - When installing, select "Add python.exe to PATH" and "Disable path length limit"
- Download the source code and extract the contents.
- Download visual studio installer (Community Version) from https://visualstudio.microsoft.com/downloads/
    - Install the components:
        - C++ CMake tools for Windows
            - This includes MSVC v143
        - C++ core features
        - Windows 10/11 SDK
- Download and install CUDA 12.5 from https://developer.nvidia.com/cuda-downloads using the default settings
- Download cuDNN 8.9.7 from https://developer.nvidia.com/downloads/compute/cudnn/secure/8.9.7/local_installers/12.x/cudnn-windows-x86_64-8.9.7.29_cuda12-archive.zip/
    - Extract the zip file, and copy the contents into "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.5", replacing existing files.
- Open a terminal in the project folder and run:
    - $Env:CMAKE_ARGS = "-DGGML_CUDA=ON -DGGML_CUDA_F16=ON -DBUILD_SHARED_LIBS=ON"
    - $Env:FORCE_CMAKE=1
    - pip install llama-cpp-python --force-reinstall --upgrade --no-cache-dir
    - pip install -r requirements.txt"
    - pip install SpeechRecognition[whisper-local]
    - pip install numpy==1.26.4
- Download https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf?download=true and move the file into Honey-Badger-Sales-Helper/llm_chat_processors/llm_models/Phi-3-mini-4k-instruct-q4.gguf
- Restart your computer



# Requirements
See requirements.txt for python libraries used.
Other requirements:
- cuda toolkit archive 12.5
https://developer.nvidia.com/cuda-downloads
- cuddn for cuda 12.1.0
https://developer.nvidia.com/downloads/compute/cudnn/secure/8.9.7/local_installers/12.x/cudnn-windows-x86_64-8.9.7.29_cuda12-archive.zip/

# Credits
- Created with the help of Github Copilot
- Badger Icon generated with Copilot Designer
