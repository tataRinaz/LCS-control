from states import *
from randoms import get_random_state


class TerminalDevice:
    def __init__(self, probabilities, line_state_callback, line_state_change_callback, terminals_callback):
        self.state = DeviceState.INITIAL
        self.prev_state = DeviceState.WORKING
        self.probabilities = probabilities
        self.line_state_callback = line_state_callback
        self.line_state_change_callback = line_state_change_callback
        self.terminal_callback = terminals_callback
        self.last_message = None
        self.active = False

    def _on_message_received(self, message):
        self.last_message = message

    def _on_state_change(self, new_state):
        old_state = self.state
        self.state = new_state
        if new_state == DeviceState.GENERATOR and self.line_state_callback() == LineState.WORKING_LINE_A:
            self.line_state_change_callback(LineState.GENERATION)
        if old_state == LineState.GENERATION:
            terminals = self.terminal_callback()
            if any(map(lambda terminal: terminal.state == DeviceState.GENERATOR, terminals)):
                return
            if self.line_state_callback() == LineState.GENERATION:
                self.line_state_change_callback(LineState.WORKING_LINE_A)

    def start_messaging(self, message):
        self._on_message_received(message)
        self.active = True

    def end_messaging(self, message):
        self._on_message_received(message)
        self.active = False

    def change_state(self, new_state):
        if self.state == DeviceState.BLOCKED and new_state == DeviceState.UNBLOCKING:
            self._on_state_change(self.prev_state)
            return
        if self.state != DeviceState.BLOCKED and self.state != DeviceState.DENIAL:
            self.prev_state = self.state
            self._on_state_change(new_state)

    def process(self):
        if self.state == DeviceState.INITIAL:
            self.change_state(DeviceState.WORKING)

        self.prev_state = self.state

        random_state = get_random_state(self.probabilities)
        self.change_state(random_state)

        return random_state
