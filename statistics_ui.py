import tkinter as tk
from threading import Thread
from statistic_model import statistic_model, write_single_statistic_to_csv, write_sessions_statistic_to_csv, \
    StatisticRunner


class LCSRunThread(Thread):
    def __init__(self, task):
        Thread.__init__(self)
        self.task = task

    def run(self):
        try:
            self.task()
        except Exception as e:
            print(e)


class StatisticEntry(tk.Entry):
    def __init__(self, root, name, is_int: bool, correctness_checker, default_value, row):
        super().__init__(root)
        self.text_label = tk.Label(root, text=name, bg="white")
        self.text_label.grid(column=0, row=row)
        self.is_int = is_int
        self.correctness_checker = correctness_checker
        self.insert(tk.END, default_value)
        self.grid(column=1, row=row)
        self.focus()
        self.configure(highlightbackground="black", highlightcolor="black", highlightthickness=1)

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


class RunTaskBar(tk.Frame):
    _session_count: int

    def __init__(self, root):
        super().__init__(root)

        self._sessions_count = None
        self._frames_count = 100
        self._frames = [tk.Frame(self, bg='white', width=2, height=15) for _ in range(self._frames_count)]
        for index in range(self._frames_count):
            self._frames[index].grid(row=0, column=index + 1)

        self._current_frame_index = 0
        self.configure(bg="white", highlightbackground="black", highlightcolor="black", highlightthickness=1)

    def set_session_count(self, session_count):
        self._sessions_count = session_count

    def update_bar(self, sessions_passed):
        if self._sessions_count is None or self._sessions_count <= 0:
            raise RuntimeError('Session count is invalid')

        frames_to_update = int(sessions_passed / self._sessions_count * self._frames_count)
        last_frame = self._current_frame_index + frames_to_update
        if last_frame > self._frames_count:
            last_frame = self._frames_count

        for index in range(self._current_frame_index, last_frame):
            self._frames[index].configure(bg='blue')

        self._current_frame_index = last_frame

    def flush(self):
        self._current_frame_index = 0
        for index in range(len(self._frames)):
            self._frames[index].configure(bg='white')


class StatisticsUI(tk.Frame):
    def __init__(self, root, change_frame_cb):
        super().__init__(root, width=2000, height=1000)
        self.change_frame_cb = change_frame_cb
        self.change_frame_button = tk.Button(self, text='Перейти к визуальному образцу', command=self._on_clicked)
        self.change_frame_button.grid(column=0, row=0)

        def probability_check(val):
            return 0. <= val < 1.0

        self.generation_probability_entry = StatisticEntry(self, is_int=False, correctness_checker=probability_check,
                                                           name='Генерация', default_value=1 / 20000, row=1)
        self.denial_probability_entry = StatisticEntry(self, is_int=False, correctness_checker=probability_check,
                                                       name='Отказ', default_value=1 / 5000, row=2)
        self.failure_probability_entry = StatisticEntry(self, is_int=False, correctness_checker=probability_check,
                                                        name='Сбой', default_value=1 / 2000, row=3)
        self.busy_probability_entry = StatisticEntry(self, is_int=False, correctness_checker=probability_check,
                                                     name='Занят', default_value=1 / 2000, row=4)

        self.messages_count_entry = StatisticEntry(self, is_int=True,
                                                   correctness_checker=lambda messages: messages > 100,
                                                   name='Сообщения', default_value=20000, row=5)
        self.message_groups_entry = StatisticEntry(self, is_int=True, correctness_checker=lambda groups: groups > 2,
                                                   name='Группы сообщений', default_value=20, row=6)
        self.terminal_devices_entry = StatisticEntry(self, is_int=True,
                                                     correctness_checker=lambda terminals_counte: terminals_counte > 2,
                                                     name='ОУ', default_value=18, row=7)
        self.sessions_count_entry = StatisticEntry(self, is_int=True,
                                                   correctness_checker=lambda sessions_count: sessions_count > 0,
                                                   name='Количество сеансов', default_value=50, row=8)
        self.start_run = tk.Button(self, text='Запуск',
                                   command=self._on_start_statistic_clicked)
        self.start_run.grid(row=9, column=0)

        self._text_label = tk.Label(self, text="Прогресс", bg="white")
        self._text_label.grid(row=10, column=0)

        self.task_run_bar = RunTaskBar(self)
        self.task_run_bar.grid(row=10, column=1)
        self.configure(bg="white")
        self.count = 1

    def _process_statistics(self, messages_count, groups_count, terminal_device_count, gen_prob, den_prob, fail_prob,
                            busy_prob, sessions_count):
        if messages_count and \
                groups_count and \
                terminal_device_count and \
                gen_prob and \
                den_prob and \
                fail_prob and \
                busy_prob:
            if sessions_count is None:
                statistic = statistic_model(groups_count, messages_count, terminal_device_count,
                                            [gen_prob, den_prob, fail_prob, busy_prob])

                write_single_statistic_to_csv(f'output{self.count}.csv', statistic)
                self.count += 1
            else:
                runner = StatisticRunner(sessions_count, groups_count, messages_count, terminal_device_count,
                                         [gen_prob, den_prob, fail_prob, busy_prob], self.task_run_bar.update_bar)
                LCSRunThread(runner.run).start()
                while not runner.is_ready():
                    pass

                write_sessions_statistic_to_csv('sessions_output.csv', runner.results())

    def _on_start_statistic_clicked(self):
        messages_count = self.messages_count_entry.get()
        groups_count = self.message_groups_entry.get()
        terminal_device_count = self.terminal_devices_entry.get()
        sessions_count = self.sessions_count_entry.get()

        gen_prob = self.generation_probability_entry.get()
        den_prob = self.denial_probability_entry.get()
        fail_prob = self.failure_probability_entry.get()
        busy_prob = self.busy_probability_entry.get()

        self.task_run_bar.flush()
        self.task_run_bar.set_session_count(sessions_count)

        LCSRunThread(
            lambda: self._process_statistics(messages_count, groups_count, terminal_device_count, gen_prob, den_prob,
                                             fail_prob, busy_prob, sessions_count)).start()

    def _on_clicked(self):
        self.change_frame_cb()
