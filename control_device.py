from states import *


# TODO: add time counter
# TODO: update handlers
class ControlDevice:
    def __init__(self, terminals_callback, line_state_change_callback):
        self.terminals_callback = terminals_callback
        self.line_state_change_callback = line_state_change_callback
        self.state_handler_dict = {
            DeviceState.BUSY: self.process_busy,
            DeviceState.FAILURE: self.process_failure,
            DeviceState.DENIAL: self.process_denial,
            DeviceState.BLOCKED: self.process_blocked
        }

    # Algorithm to process generator device:
    # 1. Block all devices
    # 2. Search the first generator
    # 3. Unblock all devices after generator

    def process_generator_device(self):
        terminals = self.terminals_callback()

        # Blocking all devices before searching a generator
        self.line_state_change_callback(LineState.WORKING_LINE_B)
        for terminal in terminals:
            terminal.start_messaging("Terminal device: block")
            terminal.change_state(DeviceState.BLOCKED)
            terminal.end_messaging("")

        generator_index = None
        for index in range(len(terminals)):
            terminals[index].start_messaging("Terminal device: unblocking")
            terminals[index].change_state(DeviceState.UNBLOCKING)

            if terminals[index].state == DeviceState.DENIAL:
                terminals[index].end_messaging("Terminal device: denial")
                continue

            terminals[index].end_messaging("")

            terminals[index].start_messaging("Terminal device: questioning")
            self.line_state_change_callback(LineState.WORKING_LINE_A)
            if terminals[index].state != DeviceState.GENERATOR:
                terminals[index].end_messaging("Terminal device: not a generator")
                continue

            self.line_state_change_callback(LineState.WORKING_LINE_B)
            terminals[index].change_state(DeviceState.DENIAL)
            terminals[index].end_messaging("Terminal device: generator denial")
            generator_index = index

        for index in range(generator_index + 1, len(terminals)):
            terminals[index].start_messaging("Terminal device: unblocking")
            terminals[index].change_state(DeviceState.UNBLOCKING)
            terminals[index].end_messaging("")

        self.line_state_change_callback(LineState.WORKING_LINE_A)

    def process_busy(self, client):
        pass

    def process_failure(self, client):
        pass

    def process_blocked(self, client):
        pass

    def process_denial(self, client):
        pass

    def process_ok(self, client):
        pass

    def process_client_device(self, client):
        client.start_messaging("Terminal device: questioning")
        handler = self.state_handler_dict[client.state] if client.state in self.state_handler_dict else self.process_ok
        handler(client)