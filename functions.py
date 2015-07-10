# ====================================
# IMPORTS
# ====================================
import glob
from datetime import datetime, time
import json
from collections import OrderedDict
import operator
from time import time
import sys


# ====================================
# CLASS FOR RUN INFO FROM JSON
# ====================================
class RunInfo:
    """reads in information from the json file"""

    def __init__(self, fname, start="50", stop="-1"):
        # load json
        self.f = open(fname, 'r')
        self.data = json.load(self.f, object_pairs_hook=OrderedDict)
        self.time_mode = False
        self.first = self.first_run()
        self.last = self.last_run()
        self.run_start = start
        self.run_stop = stop
        if not start.isdigit():
            self.start = datetime.strptime(start, "%Y-%m-%d.%H:%M")
        else:
            self.start_run = convert_run(start)
            self.date_start = self.data[self.start_run]["begin date"]
            s1 = self.date_start + " " + self.data[self.start_run]["start time"]
            self.start = datetime.strptime(s1, "%m/%d/%Y %H:%M:%S")
        if not stop.isdigit() and stop != "-1":
            self.stop = datetime.strptime(stop, "%Y-%m-%d.%H:%M")
            self.dia1 = "unknown"
            self.dia2 = "unknown"
            self.type = "time interval"
            self.get_run_start_stop()
            self.time_mode = True
        else:
            self.stop_run = self.get_stop_run(stop)
            self.date_stop = self.data[self.stop_run]["begin date"]
            self.stop = datetime.strptime(self.s2(), "%m/%d/%Y %H:%M:%S")
            d1 = self.data[self.start_run]["diamond 1"]
            d2 = self.data[self.start_run]["diamond 2"]
            self.dia1 = d1 if d1 != "none" else "Diamond Front"
            self.dia2 = d2 if d2 != "none" else "Diamond Back"
            self.flux = self.data[self.start_run]["measured flux"]
            self.rate = self.data[self.start_run]["raw rate"]
            self.pixels = self.data[self.start_run]["masked pixels"]
            self.type = self.data[self.start_run]["type"]

    def get_run_start_stop(self):
        found_start = False
        for run in range(int(convert_run(self.first)), int(convert_run(self.last))+1):
            date = self.data[str(run)]["begin date"]
            start = self.data[str(run)]["start time"]
            if self.start < datetime.strptime(date + " " + start, "%m/%d/%Y %H:%M:%S") and not found_start:
                self.run_start = int(str(run)[4:])
                found_start = True
            if self.stop < datetime.strptime(date + " " + start, "%m/%d/%Y %H:%M:%S"):
                self.run_stop = int(str(run-1)[4:])
                break
            if self.data[str(run)]["diamond 1"] != "none":
                self.dia1 = self.data[str(run)]["diamond 1"]
                self.dia2 = self.data[str(run)]["diamond 2"]
        if not self.is_float(self.run_stop):
            self.run_stop = self.last

    def first_run(self):
        first_run = self.data.iterkeys().next()
        for run in self.data:
            if first_run > run:
                first_run = run
        first_run = int(str(first_run)[4:])
        return first_run

    def last_run(self):
        last_run = self.data.iterkeys().next()
        for run in self.data:
            if last_run < run:
                last_run = run
        last_run = int(str(last_run)[4:])
        return last_run

    def get_stop_run(self, stop):
        run = self.start_run
        if stop != '-1':
            run = convert_run(stop)
        return run

    def s2(self):
        s2 = self.date_stop + " " + self.data[self.stop_run]["stop time"]
        # take the start time of next run if you don't find a stop time
        if s2 == "none":
            run = str(int(self.stop_run) + 1)
            s2 = self.date_stop + " " + self.data[run]["start time"]
        return s2

    def dia_runs(self):
        dia_runs = []
        dia1 = self.data[convert_run(self.first)]["diamond 1"]
        end = 0
        for run in range(self.first, self.last + 1):
            dia1_now = self.data[convert_run(run)]["diamond 1"]
            dia2_now = self.data[convert_run(run)]["diamond 2"]
            if dia1_now != dia1 and dia1_now != "none":
                dia1 = dia1_now
                dia2 = dia2_now
                info = [str(dia1), str(dia2), run, end]
                dia_runs.append(info)
            if dia1_now == dia1:
                end = run
        for i in range(len(dia_runs) - 1):
            dia_runs[i][3] = dia_runs[i + 1][3]
        dia_runs[-1][3] = self.last
        return dia_runs

    def get_info(self, run, info):
        return self.data[convert_run(run)][info]

    def get_time(self, run, info):
        date = self.data[convert_run(run)]["begin date"]
        s = date + " " + self.data[convert_run(run)][info]
        if self.data[convert_run(run)][info] == "none":
            s = date + " " + self.data[convert_run(run+1)]["start time"]
        s = datetime.strptime(s, "%m/%d/%Y %H:%M:%S")
        return s

    def print_times(self):
        print 'first run:', self.first
        print 'last run:', self.last

    def print_dia_runs(self):
        max_length = 0
        for i in self.dia_runs():
            if len(i[0] + i[1]) > max_length:
                max_length = len(i[0] + i[1])
        for i in self.dia_runs():
            spaces = "  "
            for j in range(max_length - len(i[0] + i[1])):
                spaces += " "
            print i[0], '&', i[1], '\b:' + spaces + 'run', i[2], '-', i[3]

    @staticmethod
    def is_float(string):
        try:
            float(string)
            return True
        except ValueError:
            return False


# ====================================
# HELPER FUNCTIONS
# ====================================
# convert datetime to number in seconds
def convert_time(date_time):
    seconds = (date_time.day - 1) * 24 * 3600 + date_time.hour * 3600 + date_time.minute * 60 + date_time.second
    if date_time.month == 6:
        seconds += 31 * 3600 * 24
    return seconds


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


# prints elapsed time
def elapsed_time(start):
    string = str('{0:0.2f}'.format(time() - start)) + ' seconds'
    return string


# ====================================
# CLASS FOR THE DATA
# ====================================
class KeithleyInfo(RunInfo):
    """reads in information from the keithley log file"""

    def __init__(self, log, jsonfile, start, stop, number):
        self.single_mode = (True if number == "1" else False)
        RunInfo.__init__(self, jsonfile, start, stop)
        self.keithleys = OrderedDict([("Keithley1", "Silicon"),
                                      ("Keithley2", str(self.dia1)),
                                      ("Keithley3", str(self.dia2))])
        if self.single_mode:
            self.keithleys = OrderedDict([("Keithley2", "II6-94")])
        self.log_dir = str(log) + "keithleyLog_" + str(self.start.year) + "*"
        self.log_names = self.logs_from_start()
        data = self.find_data()
        self.time_x = data[0]
        self.current_y = data[1]
        self.voltage_y = data[2]

    def get_lognames(self):
        log_names = []
        for name in glob.glob(self.log_dir):
            log_names.append(name)
        log_names = sorted(log_names)
        return log_names

    def get_start_log(self):
        valid_logs = []
        start_log = 0
        break_loop = False
        for i in range(len(self.get_lognames())):
            first_line = ""
            data = open(self.get_lognames()[i], 'r')
            # sys.stdout.flush()
            for line in data:
                first_line = line.split()
                if len(first_line) == 0:
                    break
                if first_line[1].startswith(str(self.start.year)):
                    valid_logs.append(i)
                    break
            # if whole file is empty continue
            if len(first_line) == 0:
                continue
            if first_line[1].startswith(str(self.start.year)):
                first_line = datetime.strptime(first_line[1] + " " + first_line[2], "%Y_%m_%d %H:%M:%S")
                if self.start < first_line:
                    start_log = valid_logs[0]
                    if len(valid_logs) > 2:
                        start_log = valid_logs[-2]
                    break_loop = True
                    break
            # take last logfile if nothing is found until then
            if i == len(self.get_lognames()) - 1 and start_log == 0:
                start_log = i
                break
            data.close()
            if break_loop:
                break
        return start_log

    def logs_from_start(self):
        log_names = []
        for i in range(self.get_start_log(), len(self.get_lognames())):
            log_names.append(self.get_lognames()[i])
        return log_names

    def create_dicts(self):
        dicts = {}
        for key in self.keithleys:
            dicts[key] = []
        return dicts

    def find_data(self):
        dicts = [self.create_dicts(), self.create_dicts(), self.create_dicts()]
        stop = False
        ind = 0
        for name in self.log_names:
            data = open(name, 'r')
            if ind == 0:
                self.find_start(data)
            for line in data:
                info = line.split()
                if info[1].startswith(str(self.start.year)):
                    now = datetime.strptime(info[1] + " " + info[2], "%Y_%m_%d %H:%M:%S")
                    for key in self.keithleys:
                        if len(info) > 3 and info[0].startswith(key):
                            if self.start < now < self.stop:
                                dicts[0][key].append(convert_time(now))
                                dicts[1][key].append(float(info[4]) * 1e9)
                                dicts[2][key].append(float(info[3]))
                    if self.stop < now:
                        stop = True
                        break
            data.close()
            if stop:
                break
        self.check_empty(dicts)
        ind += 1
        return dicts

    def find_start(self, data):
        lines = len(data.readlines())
        was_lines = 0
        data.seek(0)
        if lines > 10000:
            for i in range(6):
                lines /= 2
                for j in range(lines):
                    data.readline()
                while True:
                    info = data.readline().split()
                    if not info:
                        break
                    if info[1].startswith(str(self.start.year)):
                        now = datetime.strptime(info[1] + " " + info[2], "%Y_%m_%d %H:%M:%S")
                        if now < self.start:
                            was_lines += lines
                            break
                        else:
                            data.seek(0)
                            for k in range(was_lines):
                                data.readline()
                            break

    def check_empty(self, dicts):
        for i in range(len(dicts)):
            for key in self.keithleys:
                if len(dicts[i][key]) == 0:
                    if i == 0:
                        dicts[i][key] = [convert_time(self.start), convert_time(self.stop)]
                    else:
                        dicts[i][key] = [0]
                        dicts[i][key] = [0]

    def relative_time(self):
        for key in self.keithleys:
            zero = self.time_x[key][0]
            for i in range(len(self.time_x[key])):
                self.time_x[key][i] = self.time_x[key][i] - zero
        return self.time_x


# ====================================
# BACKUP IF THERE IS NO JSON
# ====================================

# # read eudaq logfile and get the start and stop time of the run
# def get_start_stop(run, logdir, start="", stop=""):
#     print "Looking for Run:", run
#     time_interval = ["", "2015-12-31 23:59:59.999"]
#
#     if run != "0":
#         run_name = convert_run(run)
#         start_tag = "Starting Run " + run_name
#         stop_tag = "Stopping Run " + run_name
#         eudaq_log_dir = str(logdir) + "2015-*"
#         time_interval = find_start_stop(start_tag, stop_tag, time_interval, eudaq_log_dir, run)
#
#     elif run == "0":
#         if len(start) > 5:
#             time_interval[0] = datetime.strptime(start, "%Y-%m-%d-%H-%M-%S")
#             time_interval[1] = datetime.strptime(stop, "%Y-%m-%d-%H-%M-%S")
#             sorted(time_interval)
#         else:
#             run_name1 = convert_run(start)
#             run_name2 = convert_run(stop)
#             start_tag = "Starting Run " + run_name1
#             stop_tag = "Stopping Run " + run_name2
#             eudaq_log_dir = str(logdir) + "2015-*"
#             time_interval = find_start_stop(start_tag, stop_tag, time_interval, eudaq_log_dir, run)
#     print "time start:", datetime.strftime(time_interval[0], '%Y-%m-%d %H:%M:%S')
#     print "time stop :", datetime.strftime(time_interval[1], '%Y-%m-%d %H:%M:%S')
#     return time_interval

# # find start and stop in file
# def find_start_stop(start, stop, interval, log, run):
#     while True:
#         for name in glob.glob(log):
#             logfile = open(name, 'r')
#             for line in logfile:
#                 data = line.split("\t")
#                 if len(data) > 1:
#                     if data[1].startswith(start):
#                         interval[0] = data[2]
#                     if data[1].startswith(stop):
#                         interval[1] = data[2]
#             if len(interval[0]) > 3:
#                 break
#             logfile.close()
#         if interval[0] == "":
#             print "There was no data in the logfiles --> exit"
#             exit()
#         if interval[1] == "2015-12-31 23:59:59.999":
#             run_name = convert_run(run)
#             stop = "Starting Run " + str(int(run_name)+1)
#             interval[0] = ""
#         else:
#             break
#
#
#     # example string: '2015-05-29 14:14:40.923'
#     interval[0] = datetime.strptime(interval[0], "%Y-%m-%d %H:%M:%S.%f")
#     interval[1] = datetime.strptime(interval[1], "%Y-%m-%d %H:%M:%S.%f")
#     return interval
