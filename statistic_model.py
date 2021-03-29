from collections import Counter
import csv

import lcs
from states import LCSType, DeviceState


class Statistics:
    run_index: int
    math_expectation: float
    standard_deviation: float
    denials_count: int
    failures_count: int
    generators_count: int
    busy_count: int

    def __init__(self):
        self.run_index = 0
        self.math_expectation = 0.
        self.standard_deviation = 0.
        self.elapsed_time = 0
        self.denials_count = 0
        self.failures_count = 0
        self.generators_count = 0
        self.busy_count = 0

    def as_list(self):
        return [self.run_index, self.math_expectation, self.standard_deviation, self.elapsed_time, self.denials_count,
                self.failures_count,
                self.generators_count, self.busy_count]


def statistic_model(group_count, total_messages_count, terminals_count, probabilities):
    system = lcs.LCS(terminals_count, probabilities, LCSType.Statistics)
    statistics = []

    unprocessed_messages = total_messages_count
    for group_num in range(group_count):
        stats = Statistics()
        stats.run_index = group_num

        lcs_runs_count = int(unprocessed_messages / (terminals_count * (group_count - group_num)))
        messages_per_run = terminals_count * lcs_runs_count

        time_intervals = []

        device_states_counter = Counter()
        total_wasted_time = 0
        for _ in range(lcs_runs_count):
            statistics_result, wasted_time = system.process()
            total_wasted_time += wasted_time
            device_states_counter += statistics_result

            time_intervals.append(total_wasted_time / terminals_count)

        stats.math_expectation = total_wasted_time / messages_per_run
        stats.standard_deviation = sum((val - stats.math_expectation) ** 2 for val in time_intervals)
        stats.elapsed_time = total_wasted_time
        stats.denials_count = device_states_counter[DeviceState.DENIAL]
        stats.busy_count = device_states_counter[DeviceState.BUSY]
        stats.failures_count = device_states_counter[DeviceState.FAILURE]
        stats.generators_count = device_states_counter[DeviceState.GENERATOR]

        unprocessed_messages -= messages_per_run
        statistics.append(stats)

    return statistics


def write_to_csv(output_filename, statistics):
    field_names = ['Номер прогона', 'МО', 'СКО', 'Затраченное время', 'Отказов', 'Сбоев', 'Занятых', 'Генераторов']
    with open(output_filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(field_names)
        for statistic in statistics:
            writer.writerow(statistic.as_list())


if __name__ == '__main__':
    statistics = statistic_model(20, 20000, 18, [0.01, 0.01, 0.01, 0.01])
    write_to_csv('output.csv', statistics)
