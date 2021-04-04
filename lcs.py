import time as t
from collections import Counter

from terminal_device import TerminalDevice
from control_device import ControlDevice
from states import *

default_sleep_time_ms = 100


class LCS:
    def __init__(self, terminals_count: int, probabilities, system_type=LCSType.Standalone,
                 sleep_time=default_sleep_time_ms):
        self.type = system_type
        self.sleep_time_ms = sleep_time
        self.controller = ControlDevice(self.get_terminals, self.line_state_change, self.type, self.sleep_time_ms)
        self.terminals = [TerminalDevice(probabilities, self.get_line_state, self.line_state_change, self.get_terminals)
                          for _ in range(terminals_count)]
        self.line_state = LineState.WORKING_LINE_A

    def process(self):
        begin_time = self.controller.get_time()

        broken_states = None
        if self.type == LCSType.Statistics:
            broken_states = Counter(
                filter(lambda state: DeviceState.BUSY.value <= state.value <= DeviceState.GENERATOR.value,
                       map(lambda terminal: terminal.process(), self.terminals)))
        else:
            t.sleep(self.sleep_time_ms / 1000)

        while self.line_state == LineState.GENERATION:
            self.controller.process_generator_device()

        for terminal in self.terminals:
            self.controller.process_client_device(terminal)

        return broken_states, self.controller.get_time() - begin_time

    def get_terminals(self):
        return self.terminals

    def get_line_state(self):
        return self.line_state

    def line_state_change(self, new_state):
        self.line_state = LineState.GENERATION if any(
            map(lambda terminal: terminal.state == DeviceState.GENERATOR, self.terminals)) else new_state