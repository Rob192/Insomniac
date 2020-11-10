from datetime import datetime, timedelta


def get_planning(start_time, stop_time, on_duration, off_duration):
    """
    Used to get the planning of the sessions for insomniac.
    :param start_time: start time in format "08:00"
    :param stop_time: stop time in format "20:00"
    :param on_duration: duration of the on phase in minutes
    :param off_duration: duration of the off phase in minutes
    :return: list of times when to start insomniac ['08:00', '08:50' ...]
    """
    start_time = datetime.strptime(start_time,'%H:%M')
    stop_time = datetime.strptime(stop_time,'%H:%M')
    on_duration = on_duration * 60
    off_duration = off_duration * 60

    cycle_duration = on_duration + off_duration
    number_of_cycles = (stop_time - start_time).total_seconds() // cycle_duration

    res = []
    for i in range(int(number_of_cycles)):
        res.append((start_time + timedelta(seconds=i * cycle_duration)).strftime('%H:%M'))

    return res

if __name__ == '__main__':
    start_time = "08:00"
    stop_time = "20:01"
    on_duration = 60
    off_duration = 30

    print(get_planning(start_time, stop_time, on_duration, off_duration))

