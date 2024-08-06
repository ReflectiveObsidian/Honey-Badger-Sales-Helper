from enum import Enum

class CallManagerState(Enum):
    IDLE = 1
    STARTING_CALL = 2
    CALIBRATING = 3
    ON_CALL = 4
    ENDING_CALL = 5