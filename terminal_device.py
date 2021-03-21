from states import DeviceState
from randoms import get_random_state


class TerminalDevice:
    def __init__(self, probabilities):
        self.state = DeviceState.INITIAL
        self.prev_state = DeviceState.WORKING
        self.probabilities = probabilities
        self.last_message = None
        self.active = False

    def _on_message_received(self, message):
        self.last_message = message

    def start_messaging(self, message):
        self._on_message_received(message)
        self.active = True

    def end_messaging(self, message):
        self._on_message_received(message)
        self.active = False

    def change_state(self, new_state):
        if self.state == DeviceState.BLOCKED and new_state == DeviceState.UNBLOCKING:
            self.state = self.prev_state
            return
        if self.state != DeviceState.BLOCKED and self.state != DeviceState.DENIAL:
            self.prev_state = self.state
            self.state = new_state

    def process(self):
        if self.state == DeviceState.INITIAL:
            self.change_state(DeviceState.WORKING)

        self.prev_state = self.state

        random_state = get_random_state(self.probabilities)
        self.change_state(random_state)

        return random_state
