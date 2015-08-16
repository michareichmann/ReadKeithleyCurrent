# ====================================
# IMPORTS
# ====================================
import glob
from datetime import datetime
import json
from collections import OrderedDict
from time import time

aver_points = 50
weight = 0.93

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
        if not self.run_stop.isdigit():
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
        if self.data[self.stop_run]["stop time"][0] < self.data[self.stop_run]["start time"][0]:
            s = list(self.date_stop)
            print self.date_stop
            s[4] = str(int(s[4]) + 1)
            self.date_stop = "".join(s)
            print self.date_stop
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
        run_number = "150800" + str(number)
    elif number >= 10:
        run_number = "1508000" + str(number)
    else:
        run_number = "15080000" + str(number)
    return run_number


# prints elapsed time
def elapsed_time(start):
    string = str('{0:0.2f}'.format(time() - start)) + ' seconds'
    return string
    
def get_log_dir(directory):
    K6517 = ['k6517', '6517', '6517b', 'k6517b']
    K2657 = ['k2657', '2657', '2657a', 'k2657b', 'dia2']
    K237 = ['k237', '237', 'dia1']
    K1 = ['k1', 'keithley1', 'silicon', 'sil']
    if directory.lower() in K6517:
        return '/home/testbeam/sdvlp/keithleyClient/PSI_2015_08/Keithley6517'
    elif directory.lower() in K2657:
        return '/home/testbeam/sdvlp/keithleyClient/PSI_2015_08/Keithley2657A'
    elif directory.lower() in K1:
        return '/home/testbeam/sdvlp/keithleyClient/PSI_2015_08/Keithley1'
    elif directory.lower() in K237:
        return '/home/testbeam/sdvlp/keithleyClient/PSI_2015_08/Keithley237'
    elif len(directory) < 6:
        print "Could not find any alias for entered log file directory. exiting..."
        exit()
    return directory


# ====================================
# CLASS FOR THE DATA
# ====================================
class KeithleyInfo(RunInfo):
    """reads in information from the keithley log file"""

    def __init__(self, log, jsonfile, start, stop, number, averaging):
        self.single_mode = (True if number == "1" else False)
        self.do_averaging = (True if averaging else False)
        RunInfo.__init__(self, jsonfile, start, stop)
        self.keithleys = OrderedDict([("Keithley1", "Silicon"),
                                      ("Keithley2", str(self.dia1)),
                                      ("Keithley3", str(self.dia2))])
        self.log_dir = str(log) + "/HV*log"
        self.keithley_name = self.get_keithley_name()
        print self.keithley_name
        if self.single_mode:
            self.keithleys = OrderedDict([("Keithley1", self.keithley_name)])
        self.log_names = self.logs_from_start()
        self.mean_curr = 0
        self.mean_volt = 0
        data = self.find_data()
        self.time_x = data[0]
        self.current_y = data[1]
        self.voltage_y = data[2]

    def get_keithley_name(self):
        name = self.log_dir.split('/')
        for i in name:
            if i.lower().startswith('keithley') and not i.lower().endswith('client'):
                name = i
                break
        return str(name)

    def get_lognames(self):
        log_names = []
        for name in glob.glob(self.log_dir):
            log_names.append(name)
        log_names = sorted(log_names)
        return log_names

    def get_start_log(self):
        start_log = 0
        log_names = self.get_lognames()
        for i in range(len(log_names)):
            name = log_names[i].strip('.log').split('/')
            name = name[-1].split('_')
            log_date = ""
            for j in range(3, 9):
                log_date += name[j] + " "
            log_date = log_date.strip(' ')
            log_date = datetime.strptime(log_date, "%Y %m %d %H %M %S")
            if log_date >= self.start:
                break
            start_log = i
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

    @staticmethod
    def get_log_date(name):
        name = name.strip('.log').split('/')
        name = name[-1].split('_')
        log_date = ""
        for i in range(3, 6):
            log_date += name[i] + "-"
        log_date = log_date.strip('-')
        return log_date

    def find_data(self):
        dicts = [self.create_dicts(), self.create_dicts(), self.create_dicts()]
        stop = False
        ind = 0
        for name in self.log_names:
            self.mean_curr = 0
            self.mean_volt = 0
            log_date = self.get_log_date(name)
            data = open(name, 'r')
            if ind == 0:
                self.find_start(data, log_date)
            index = 0
            for line in data:
                info = line.split()
                if self.is_float(info[1]):
                    now = datetime.strptime(log_date + " " + info[0], "%Y-%m-%d %H:%M:%S")
                    index = self.averaging(dicts, now, info, index)
                    if self.stop < now:
                        stop = True
                        break
            data.close()
            if stop:
                break
        self.check_empty(dicts)
        ind += 1
        return dicts

    def averaging(self, dicts, now, info, index, shifting=False):
        for key in self.keithleys:
            if len(info) > 2:
                # print self.start, now, self.stop
                if self.start < now < self.stop and float(info[2]) < 1e30:
                    index += 1
                    if self.do_averaging:
                        if not shifting:
                            self.mean_curr += float(info[2]) * 1e9
                            self.mean_volt += float(info[1])
                            if index % aver_points == 0:
                                dicts[1][key].append(self.mean_curr / aver_points)
                                dicts[0][key].append(convert_time(now))
                                dicts[2][key].append(self.mean_volt / aver_points)
                                self.mean_curr = 0
                                self.mean_volt = 0
                        else:
                            if index <= aver_points:
                                self.mean_curr += float(info[2]) * 1e9
                                dicts[1][key].append(self.mean_curr / index)
                                if index == aver_points:
                                    self.mean_curr /= aver_points
                            else:
                                mean_curr = self.mean_curr * weight + (1 - weight) * float(info[2]) * 1e9
                                dicts[1][key].append(mean_curr)
                            dicts[0][key].append(convert_time(now))
                            dicts[2][key].append(float(info[1]))
                    else:
                        dicts[1][key].append(float(info[2]) * 1e9)
                        dicts[0][key].append(convert_time(now))
                        dicts[2][key].append(float(info[1]))
        return index

    def find_start(self, data, log_date):
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
                    if self.is_float(info[1]):
                        now = datetime.strptime(log_date + " " + info[0], "%Y-%m-%d %H:%M:%S")
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

    @staticmethod
    def is_float(string):
        try:
            float(string)
            return True
        except ValueError:
            return False

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

if __name__ == '__main__':
    test = KeithleyInfo('logs_237', 'test.json', '2015-06-29.10:50', '2015-06-29.12:00', '1')
