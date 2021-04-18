import time as t

from states import *
from time_counter import TimeCounter


# TODO: refactor ideas: 1. Add function wait_for(sleep coef) 2. Add function append_time_series
class ControlDevice:
    def __init__(self, terminals_callback, line_state_change_callback, lcs_type, sleep_time_ms):
        self.type = lcs_type
        self.sleep_time_ms = sleep_time_ms

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
        for index in range(terminals_count):
            self.time_counter.append_time(Timestamp.BLOCK)
            self.time_counter.append_time(Timestamp.WAIT_FOR_ANSWER)
            self.time_counter.append_time(Timestamp.ANSWER)

            terminals[index].start_messaging("Terminal device: block")
            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms * 0.5 / 1000)
            terminals[index].change_state(DeviceState.BLOCKED)
            terminals[index].end_messaging("")

            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms * 0.5 / 1000)

        generator_index = None
        for index in range(terminals_count):
            self.time_counter.append_time(Timestamp.UNBLOCK)
            self.time_counter.append_time(Timestamp.WAIT_FOR_ANSWER)
            self.time_counter.append_time(Timestamp.ANSWER)

            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms / 1000)
            terminals[index].start_messaging("Terminal device: unblocking")
            terminals[index].change_state(DeviceState.UNBLOCKING)

            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms / 1000)

            if terminals[index].state == DeviceState.DENIAL:
                self.process_denial(terminals[index])
                continue

            terminals[index].end_messaging("")

            self.time_counter.append_time(Timestamp.COMMAND)
            self.time_counter.append_time(Timestamp.WAIT_FOR_ANSWER)

            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms * 0.5 / 1000)

            terminals[index].start_messaging("Terminal device: questioning")
            self.line_state_change_callback(LineState.WORKING_LINE_A)
            if terminals[index].state != DeviceState.GENERATOR:
                if self.type == LCSType.Standalone:
                    t.sleep(self.sleep_time_ms / 1000)

                self.time_counter.append_time(Timestamp.ANSWER)
                terminals[index].end_messaging("Terminal device: not a generator")
                if self.type == LCSType.Standalone:
                    t.sleep(self.sleep_time_ms * 0.5 / 1000)
                continue

            self.time_counter.append_time(Timestamp.COMMAND)
            self.time_counter.append_time(Timestamp.WAIT_FOR_ANSWER)

            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms / 1000)

            self.line_state_change_callback(LineState.WORKING_LINE_B)

            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms * 0.5 / 1000)

            self.time_counter.append_time(Timestamp.BLOCK)
            self.time_counter.append_time(Timestamp.WAIT_FOR_ANSWER)
            self.time_counter.append_time(Timestamp.ANSWER)

            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms / 1000)

            terminals[index].change_state(DeviceState.DENIAL)

            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms * 0.5 / 1000)

            terminals[index].end_messaging("Terminal device: generator denial")
            generator_index = index
            break

        for index in range(generator_index + 1, terminals_count):
            self.time_counter.append_time(Timestamp.UNBLOCK)
            self.time_counter.append_time(Timestamp.WAIT_FOR_ANSWER)
            self.time_counter.append_time(Timestamp.ANSWER)

            terminals[index].start_messaging("Terminal device: unblocking")

            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms * 0.5 / 1000)
            terminals[index].change_state(DeviceState.UNBLOCKING)

            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms * 0.5 / 1000)
            terminals[index].end_messaging("")

        self.line_state_change_callback(LineState.WORKING_LINE_A)

    def _process_prepare_time(self):
        self.time_counter.append_time(Timestamp.WORD)
        self.time_counter.append_time(Timestamp.COMMAND)
        self.time_counter.append_time(Timestamp.WAIT_FOR_ANSWER)

    def process_busy(self, client):
        if self.type == LCSType.Standalone:
            t.sleep(self.sleep_time_ms / 1000)
        self._process_prepare_time()
        self.time_counter.append_time(Timestamp.ANSWER)
        self.time_counter.append_time(Timestamp.WAIT_IF_BUSY)
        client.end_messaging("Terminal device: Busy")

    def process_failure(self, client):
        if self.type == LCSType.Standalone:
            t.sleep(self.sleep_time_ms / 1000)
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
        if self.type == LCSType.Standalone:
            t.sleep(self.sleep_time_ms / 1000)
        handler = self.state_handler_dict[client.state] if client.state in self.state_handler_dict else self.process_ok
        handler(client)
        self.process_work()

        if self.type == LCSType.Standalone:
            t.sleep(self.sleep_time_ms / 1000)