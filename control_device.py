from states import *
from time_counter import TimeCounter


# TODO: process real work
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
        self.time_counter = TimeCounter()

    def get_time(self):
        return self.time_counter.get_wasted_time()

    # Algorithm to process generator device:
    # 1. Block all devices
    # 2. Search the first generator
    # 3. Unblock all devices after generator

    def process_generator_device(self):
        terminals = self.terminals_callback()

        terminals_count = len(terminals)
        for _ in range(terminals_count):
            self.time_counter.append_time(Timestamp.COMMAND)
            self.time_counter.append_time(Timestamp.WAIT_FOR_ANSWER)

        # Blocking all devices before searching a generator
        self.line_state_change_callback(LineState.WORKING_LINE_B)
        for terminal in terminals:
            self.time_counter.append_time(Timestamp.BLOCK)
            self.time_counter.append_time(Timestamp.WAIT_FOR_ANSWER)
            self.time_counter.append_time(Timestamp.ANSWER)

            terminal.start_messaging("Terminal device: block")
            terminal.change_state(DeviceState.BLOCKED)
            terminal.end_messaging("")

        generator_index = None
        for index in range(terminals_count):
            self.time_counter.append_time(Timestamp.UNBLOCK)
            self.time_counter.append_time(Timestamp.WAIT_FOR_ANSWER)
            self.time_counter.append_time(Timestamp.ANSWER)

            terminals[index].start_messaging("Terminal device: unblocking")
            terminals[index].change_state(DeviceState.UNBLOCKING)

            if terminals[index].state == DeviceState.DENIAL:
                self.process_denial(terminals[index])
                continue

            terminals[index].end_messaging("")

            self.time_counter.append_time(Timestamp.COMMAND)
            self.time_counter.append_time(Timestamp.WAIT_FOR_ANSWER)

            terminals[index].start_messaging("Terminal device: questioning")
            self.line_state_change_callback(LineState.WORKING_LINE_A)
            if terminals[index].state != DeviceState.GENERATOR:
                self.time_counter.append_time(Timestamp.ANSWER)
                terminals[index].end_messaging("Terminal device: not a generator")
                continue


            self.time_counter.append_time(Timestamp.COMMAND)
            self.time_counter.append_time(Timestamp.WAIT_FOR_ANSWER)

            self.line_state_change_callback(LineState.WORKING_LINE_B)

            self.time_counter.append_time(Timestamp.BLOCK)
            self.time_counter.append_time(Timestamp.WAIT_FOR_ANSWER)
            self.time_counter.append_time(Timestamp.ANSWER)

            terminals[index].change_state(DeviceState.DENIAL)
            terminals[index].end_messaging("Terminal device: generator denial")
            generator_index = index

        for index in range(generator_index + 1, terminals_count):
            self.time_counter.append_time(Timestamp.UNBLOCK)
            self.time_counter.append_time(Timestamp.WAIT_FOR_ANSWER)
            self.time_counter.append_time(Timestamp.ANSWER)

            terminals[index].start_messaging("Terminal device: unblocking")
            terminals[index].change_state(DeviceState.UNBLOCKING)
            terminals[index].end_messaging("")

        self.line_state_change_callback(LineState.WORKING_LINE_A)

    def _process_prepare_time(self):
        self.time_counter.append_time(Timestamp.WORD)
        self.time_counter.append_time(Timestamp.COMMAND)
        self.time_counter.append_time(Timestamp.WAIT_FOR_ANSWER)

    def process_busy(self, client):
        self._process_prepare_time()
        self.time_counter.append_time(Timestamp.ANSWER)
        self.time_counter.append_time(Timestamp.WAIT_IF_BUSY)
        client.end_messaging("Terminal device: Busy")

    def process_failure(self, client):
        self._process_prepare_time()
        client.end_messaging("Terminal device: Failure")

    def process_blocked(self, client):
        self._process_prepare_time()
        self._process_prepare_time()
        client.end_messaging("Terminal device: Blocked")

    def process_denial(self, client):
        self._process_prepare_time()
        self._process_prepare_time()
        client.end_messaging("Terminal device: Denial")

    def process_ok(self, client):
        client.end_messaging("Terminal device: OK")

    def process_work(self):
        self._process_prepare_time()
        self.time_counter.append_time(Timestamp.ANSWER)

    def process_client_device(self, client):
        client.start_messaging("Terminal device: questioning")
        handler = self.state_handler_dict[client.state] if client.state in self.state_handler_dict else self.process_ok
        handler(client)
        self.process_work()