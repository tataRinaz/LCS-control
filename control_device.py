import time as t

from states import *
from terminal_device import TerminalDevice


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
    # Algorithm to process generator device:
    # 1. Block all devices
    # 2. Search the first generator
    # 3. Unblock all devices after generator

    def process_generator_device(self):
        terminals = self.terminals_callback()

        terminals_count = len(terminals)

        # Blocking all devices before searching a generator
        self.line_state_change_callback(LineState.WORKING_LINE_B)
        for index in range(terminals_count):
            terminals[index].start_messaging("Блокировка")
            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms * 0.5 / 1000)
            terminals[index].change_state(DeviceState.BLOCKED)
            terminals[index].end_messaging("")

            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms * 0.5 / 1000)

        generator_index = None
        self.line_state_change_callback(LineState.WORKING_LINE_A)
        for index in range(terminals_count):
            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms / 1000)
            terminals[index].start_messaging("Разблокировка")
            terminals[index].change_state(DeviceState.UNBLOCKING)

            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms / 1000)

            if terminals[index].state == DeviceState.DENIAL:
                self.process_denial(terminals[index])
                continue

            terminals[index].end_messaging("")
            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms * 0.5 / 1000)

            terminals[index].start_messaging("Опрос")
            if terminals[index].state != DeviceState.GENERATOR:
                if self.type == LCSType.Standalone:
                    t.sleep(self.sleep_time_ms / 1000)

                terminals[index].end_messaging("Не генератор")
                if self.type == LCSType.Standalone:
                    t.sleep(self.sleep_time_ms * 0.5 / 1000)
                continue

            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms / 1000)

            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms * 0.5 / 1000)

            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms / 1000)

            terminals[index].end_messaging("Отказ генератора")
            terminals[index].change_state(DeviceState.DENIAL)

            self.line_state_change_callback(LineState.WORKING_LINE_B)

            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms * 0.5 / 1000)

            generator_index = index
            break

        for index in range(generator_index + 1, terminals_count):

            terminals[index].start_messaging("Разблокировка")

            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms * 0.5 / 1000)
            terminals[index].change_state(DeviceState.UNBLOCKING)

            if self.type == LCSType.Standalone:
                t.sleep(self.sleep_time_ms * 0.5 / 1000)
            terminals[index].end_messaging("")

        self.line_state_change_callback(LineState.WORKING_LINE_A)

    def process_busy(self, client: TerminalDevice):
        if self.type == LCSType.Standalone:
            t.sleep(self.sleep_time_ms / 1000)
        client.end_messaging("Абонент занят")
        if self.type == LCSType.Standalone:
            t.sleep(self.sleep_time_ms * 2 / 1000)
        client.start_messaging("Занят. Повторное сообщение")
        client.change_state(DeviceState.WORKING)

        if self.type == LCSType.Standalone:
            t.sleep(self.sleep_time_ms / 1000)
        self.process_ok(client)

    def process_failure(self, client: TerminalDevice):
        if self.type == LCSType.Standalone:
            t.sleep(self.sleep_time_ms / 1000)
        client.end_messaging("Сбой")
        if self.type == LCSType.Standalone:
            t.sleep(self.sleep_time_ms / 1000)
        client.start_messaging("Сбой. Повторное сообщение")
        client.change_state(DeviceState.WORKING)

        if self.type == LCSType.Standalone:
            t.sleep(self.sleep_time_ms / 1000)
        self.process_ok(client)

    def process_blocked(self, client: TerminalDevice):
        client.end_messaging("Заблокирован")

    def process_denial(self, client: TerminalDevice):
        if self.type == LCSType.Standalone:
            t.sleep(self.sleep_time_ms / 1000)
        client.end_messaging("Отказ")
        if self.type == LCSType.Standalone:
            t.sleep(self.sleep_time_ms / 1000)
        client.start_messaging("Отказ. Повторное сообщение")
        if self.type == LCSType.Standalone:
            t.sleep(self.sleep_time_ms / 1000)
        client.end_messaging("Отсутствие ответного слова")
        self.line_state_change_callback(LineState.WORKING_LINE_B)
        client.start_messaging("Отказ")
        if self.type == LCSType.Standalone:
            t.sleep(self.sleep_time_ms / 1000)
        client.end_messaging("Отсутствие ответного слова")
        self.line_state_change_callback(LineState.WORKING_LINE_A)

    def process_ok(self, client: TerminalDevice):
        client.end_messaging("Ок")

    def process_client_device(self, client: TerminalDevice):
        client.start_messaging("Опрос")
        if self.type == LCSType.Standalone:
            t.sleep(self.sleep_time_ms / 1000)
        handler = self.state_handler_dict[client.state] if client.state in self.state_handler_dict else self.process_ok
        handler(client)

        if self.type == LCSType.Standalone:
            t.sleep(self.sleep_time_ms / 1000)
