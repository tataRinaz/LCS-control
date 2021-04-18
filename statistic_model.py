import csv
from collections import Counter

import lcs
from states import LCSType, DeviceState


class Statistics:
    run_index: int
    denials_count: int
    failures_count: int
    generators_count: int
    busy_count: int
    messages_per_run: int

    def __init__(self):
        self.run_index = 0
        self.elapsed_time = 0
        self.denials_count = 0
        self.failures_count = 0
        self.generators_count = 0
        self.busy_count = 0
        self.messages_per_run = 0
        self.math_expectation = 0
        self.standard_deviation = 0

    def as_list(self):
        return [self.run_index,
                self.denials_count,
                self.failures_count,
                self.busy_count,
                self.generators_count,
                self.elapsed_time,
                self.math_expectation,
                self.standard_deviation]


def get_generator_index(stats: [Statistics]):
    for i in range(len(stats)):
        if stats[i].generators_count != 0:
            return i

    return None


def process_statistics(stats: [Statistics]):
    denial_count = 0

    generator_index = get_generator_index(stats)

    generator_wasted_time = 3.08 + 0.052 * generator_index if generator_index is not None else 0.

    for i in range(len(stats)):
        denial_count += stats[i].denials_count
        wasted_time = 292
        wasted_time += 0.272 * stats[i].failures_count + 1.292 * stats[i].busy_count
        wasted_time += denial_count * 29.920

        if i == 0:
            wasted_time += generator_wasted_time

        if generator_index is not None:
            wasted_time += 29.920

        stats[i].elapsed_time = wasted_time

    math_expectation = sum(stat.elapsed_time for stat in stats) / len(stats)
    standart_deviation = sum((math_expectation - stat.elapsed_time) ** 2 for stat in stats)

    return stats, math_expectation, standart_deviation


def statistic_model(group_count, total_messages_count, terminals_count, probabilities):
    system = lcs.LCS(terminals_count, probabilities, LCSType.Statistics)
    statistics = []

    unprocessed_messages = total_messages_count
    for group_num in range(group_count):
        stats = Statistics()
        stats.run_index = group_num + 1

        lcs_runs_count = int(unprocessed_messages / (terminals_count * (group_count - group_num)))
        messages_per_run = terminals_count * lcs_runs_count

        device_states_counter = Counter()
        for _ in range(lcs_runs_count):
            statistics_result, _ = system.process()
            device_states_counter += statistics_result

        stats.denials_count = device_states_counter[DeviceState.DENIAL]
        stats.busy_count = device_states_counter[DeviceState.BUSY]
        stats.failures_count = device_states_counter[DeviceState.FAILURE]
        stats.generators_count = device_states_counter[DeviceState.GENERATOR]

        unprocessed_messages -= messages_per_run
        statistics.append(stats)

    stats, math_expect, standard_deviation = process_statistics(statistics)

    res = Statistics()
    res.denials_count = sum(stats.denials_count for stats in statistics)
    res.busy_count = sum(stats.busy_count for stats in statistics)
    res.failures_count = sum(stats.failures_count for stats in statistics)
    res.elapsed_time = sum(stats.elapsed_time for stats in statistics)
    res.math_expectation = math_expect
    res.standard_deviation = standard_deviation

    statistics.append(res)

    return statistics


def write_to_csv(output_filename, statistics):
    field_names = ['Тысяча сообщений', 'Отказов', 'Сбоев', 'Занятых',
                   'Наличие генератора', 'Затраченное время', 'МО', 'СКО']

    generator_index = get_generator_index(statistics)
    # If generator occured we should mark all runs as with generator
    if generator_index is not None:
        def modify(stat):
            stat.generators_count = generator_index
            return stat

        statistics = list(map(modify, statistics))

    with open(output_filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(field_names)
        for statistic in statistics:
            writer.writerow(statistic.as_list())

        csv_file.close()


if __name__ == '__main__':
    statistics, me, std = statistic_model(20, 20000, 18, [0.01, 0.01, 0.01, 0.01])
    write_to_csv('output.csv', statistics, me, std)
