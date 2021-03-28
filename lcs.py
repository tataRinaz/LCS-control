from collections import Counter

from terminal_device import TerminalDevice
from control_device import ControlDevice
from states import *


class LCS:
    def __init__(self, terminals_count: int, probabilities):
        self.controller = ControlDevice(self.get_terminals, self.line_state_change)
        self.terminals = [TerminalDevice(probabilities, self.get_line_state, self.line_state_change, self.get_terminals)
                          for _ in range(terminals_count)]
        self.line_state = LineState.WORKING_LINE_A

    def process(self):
        begin_time = self.controller.get_time()
        broken_states = Counter(
            filter(lambda state: DeviceState.BUSY.value <= state.value <= DeviceState.GENERATOR.value,
                   map(lambda terminal: terminal.process(), self.terminals)))

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
