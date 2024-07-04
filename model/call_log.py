# Class for storing call log data
# Each call log represents a line of text in a call
# A call log contains the following information: Timestamp, Speaker, Content

from datetime import datetime

class CallLog:
    # Timestamp: datetime object
    # Speaker: string
    # Content: string
    def __init__(self, timestamp, speaker, content):
        self.timestamp = timestamp
        self.speaker = speaker
        self.content = content

    def __str__(self):
        formatted_timestamp = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"{formatted_timestamp} - {self.speaker}:\n{self.content}"