from enum import Enum

class PromptType(Enum):
    TODO = "todo"
    WARNINGS = "warnings"
    SUMMARY = "summary"

type: PromptType
