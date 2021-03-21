import enum


class DeviceState(enum.Enum):
    INITIAL = 1
    WORKING = 2
    BLOCKED = 3
    UNBLOCKING = 4
    BUSY = 5
    FAILURE = 6
    DENIAL = 7
    GENERATOR = 8


class LineState(enum.Enum):
    GENERATION = 1,
    WORKING_LINE_A = 2,
    WORKING_LINE_B = 3
