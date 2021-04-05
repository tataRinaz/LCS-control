import tkinter as tk
from statistic_model import statistic_model, write_to_csv


class StatisticEntry(tk.Entry):
    def __init__(self, root, name, is_int: bool, correctness_checker, default_value, row):
        super().__init__(root)
        self.text_label = tk.Label(root, text=name)
        self.text_label.grid(column=0, row=row)
        self.is_int = is_int
        self.correctness_checker = correctness_checker
        self.insert(tk.END, default_value)
        self.grid(column=1, row=row)
        self.focus()

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
    def __init__(self, root, change_frame_cb):
        super().__init__(root)
        self.change_frame_cb = change_frame_cb
        self.change_frame_button = tk.Button(self, text='Перейти к визуальному образцу', command=self._on_clicked)
        self.change_frame_button.grid(column=0, row=0)

        def probability_check(val):
            return 0. <= val < 1.0

        self.generation_probability_entry = StatisticEntry(self, is_int=False, correctness_checker=probability_check,
                                                           name='Генерация', default_value=1/20000, row=1)
        self.denial_probability_entry = StatisticEntry(self, is_int=False, correctness_checker=probability_check,
                                                       name='Отказ', default_value=1/2000, row=2)
        self.failure_probability_entry = StatisticEntry(self, is_int=False, correctness_checker=probability_check,
                                                        name='Ошибка', default_value=1/5000, row=3)
        self.busy_probability_entry = StatisticEntry(self, is_int=False, correctness_checker=probability_check,
                                                     name='Занят', default_value=1/2000, row=4)

        self.messages_count_entry = StatisticEntry(self, is_int=True,
                                                   correctness_checker=lambda messages: messages > 100,
                                                   name='Сообщения', default_value=20000, row=5)
        self.message_groups_entry = StatisticEntry(self, is_int=True, correctness_checker=lambda groups: groups > 2,
                                                   name='Группы сообщений', default_value=20, row=6)
        self.terminal_devices_entry = StatisticEntry(self, is_int=True,
                                                     correctness_checker=lambda terminals_counte: terminals_counte > 2,
                                                     name='ОУ', default_value=32, row=7)
        self.start_run = tk.Button(self, text='Запуск',
                                    command=self._on_start_statistic_clicked)
        self.start_run.grid(row=8, column=0)

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

    def _on_clicked(self):
        self.change_frame_cb()
