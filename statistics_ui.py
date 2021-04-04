import tkinter as tk
from statistic_model import statistic_model, write_to_csv


class StatisticEntry(tk.Entry):
    def __init__(self, root, name, is_int: bool, correctness_checker):
        super().__init__(root)
        self.text_label = tk.Label(root, text=name)
        self.text_label.pack()
        self.is_int = is_int
        self.correctness_checker = correctness_checker
        self.pack()

    def get(self):
        val = super().get()

        parser = int if self.is_int else float
        try:
            parsed = parser(val)
            if not self.correctness_checker(parsed):
                raise Exception('Invalid value')
            return parsed
        except Exception as e:
            print(e)


class StatisticsUI(tk.Frame):
    def __init__(self, root, height: int, width: int, change_frame_cb):
        super().__init__(root, height=height, width=width)
        self.change_frame_button = tk.Button(root, height=10, width=10, text='Change frame', command=change_frame_cb)
        self.change_frame_button.pack()

        def probability_check(val):
            return 0. <= val < 1.0

        self.generation_probability_entry = StatisticEntry(root, is_int=False, correctness_checker=probability_check,
                                                           name='Генерация')
        self.denial_probability_entry = StatisticEntry(root, is_int=False, correctness_checker=probability_check,
                                                       name='Отказ')
        self.failure_probability_entry = StatisticEntry(root, is_int=False, correctness_checker=probability_check,
                                                        name='Ошибка')
        self.busy_probability_entry = StatisticEntry(root, is_int=False, correctness_checker=probability_check,
                                                     name='Занят')

        self.messages_count_entry = StatisticEntry(root, is_int=True,
                                                   correctness_checker=lambda messages: messages > 100,
                                                   name='Сообщения')
        self.message_groups_entry = StatisticEntry(root, is_int=True, correctness_checker=lambda groups: groups > 2,
                                                   name='Группы сообщений')
        self.terminal_devices_entry = StatisticEntry(root, is_int=True,
                                                     correctness_checker=lambda terminals_counte: terminals_counte > 2,
                                                     name='ОУ')
        self.start_run = tk.Button(root, height=10, width=10, text='Start test',
                                   command=self._on_start_statistic_clicked)
        self.start_run.pack()

    def _on_start_statistic_clicked(self):
        messages_count = self.messages_count_entry.get()
        groups_count = self.message_groups_entry.get()
        terminal_device_count = self.terminal_devices_entry.get()

        gen_prob = self.generation_probability_entry.get()
        den_prob = self.denial_probability_entry.get()
        fail_prob = self.failure_probability_entry.get()
        busy_prob = self.busy_probability_entry.get()

        if messages_count and groups_count and terminal_device_count and gen_prob and den_prob and fail_prob and busy_prob:
            statistic = statistic_model(groups_count, messages_count, terminal_device_count,
                                        [gen_prob, den_prob, fail_prob, busy_prob])
            write_to_csv('output.csv', statistic)
