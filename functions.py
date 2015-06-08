import glob
from datetime import datetime, time


# convert datetime to number
def convert_time(string):
    string = string.day * 24 * 3600 + string.hour * 3600 + string.minute * 60 + string.second
    return string


# converts the entered run number
def convert_run(number):
    run_number = ""
    number = int(number)
    if number >= 1000:
        print "The entered run number has to be lesser then 1000"
        exit()
    elif number >= 100:
        run_number = "150500" + str(number)
    elif number >= 10:
        run_number = "1505000" + str(number)
    else:
        run_number = "15050000" + str(number)
    return run_number


# read eudaq logfile and get the start and stop time of the run
def get_start_stop(run, logdir, start="", stop=""):
    print "Looking for Run:", run
    time_interval = ["", "2015-12-31 23:59:59.999"]

    if run != "0":
        run_name = convert_run(run)
        start_tag = "Starting Run " + run_name
        stop_tag = "Stopping Run " + run_name
        eudaq_log_dir = str(logdir) + "2015-*"
        time_interval = find_start_stop(start_tag, stop_tag, time_interval, eudaq_log_dir)

    elif run == "0":
        if len(start) > 5:
            time_interval[0] = datetime.strptime(start, "%Y-%m-%d-%H-%M-%S")
            time_interval[1] = datetime.strptime(stop, "%Y-%m-%d-%H-%M-%S")
            sorted(time_interval)
        else:
            run_name1 = convert_run(start)
            run_name2 = convert_run(stop)
            start_tag = "Starting Run " + run_name1
            stop_tag = "Stopping Run " + run_name2
            eudaq_log_dir = str(logdir) + "2015-*"
            time_interval = find_start_stop(start_tag, stop_tag, time_interval, eudaq_log_dir)
    print "time start:", datetime.strftime(time_interval[0], '%Y-%m-%d %H:%M:%S')
    print "time stop :", datetime.strftime(time_interval[1], '%Y-%m-%d %H:%M:%S')
    return time_interval


# find start and stop in file
def find_start_stop(start, stop, interval, log):
    for name in glob.glob(log):
        logfile = open(name, 'r')
        for line in logfile:
            data = line.split("\t")
            if len(data) > 1:
                if data[1].startswith(start):
                    interval[0] = data[2]
                if data[1].startswith(stop):
                    interval[1] = data[2]
        if len(interval[0]) > 3:
            break
        logfile.close()

    # example string: '2015-05-29 14:14:40.923'
    interval[0] = datetime.strptime(interval[0], "%Y-%m-%d %H:%M:%S.%f")
    interval[1] = datetime.strptime(interval[1], "%Y-%m-%d %H:%M:%S.%f")
    return interval


# find file to begin with
def find_start_file(log, times):
    keithley_log_dir = str(log) + "keithleyLog_" + str(times[0].year) + "*"
    log_names = []
    for name in glob.glob(keithley_log_dir):
        log_names.append(name)
    log_names = sorted(log_names)

    begin_file = 0
    for i in range(len(log_names)):
        data = open(log_names[i], 'r')
        for line in data:
            first_line = line.split()
            if len(first_line) == 0:
                break
            if first_line[1].startswith(str(times[0].year)):
                break
        # if whole file is empty continue
        if len(first_line) == 0:
            continue
        if first_line[1].startswith(str(times[0].year)):
            first_line = datetime.strptime(first_line[1] + " " + first_line[2], "%Y_%m_%d %H:%M:%S")
            if times[0] < first_line:
                begin_file = i - 1
                break
        data.close()

    print "start with file:", log_names[begin_file]
    valid_items = len(log_names)-begin_file
    for i in range(valid_items):
        log_names[i] = log_names[begin_file+i]
    for i in range(valid_items,len(log_names)-1):
        del log_names[valid_items]
    return log_names