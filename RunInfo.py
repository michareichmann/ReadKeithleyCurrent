# ====================================
# IMPORTS
# ====================================
import json
from collections import OrderedDict
from functions1 import *


# ====================================
# CLASS FOR RUN INFO FROM JSON
# ====================================
class RunInfo:
    """reads in information from the json file"""

    def __init__(self, fname, start="51", stop="-1"):
        # load json
        self.f = open(fname, 'r')
        self.data = json.load(self.f, object_pairs_hook=OrderedDict)
        self.time_mode = False
        self.first = self.first_run()
        self.last = self.last_run()
        self.run_start = start
        self.run_stop = stop
        if not is_float(start):
            self.start = datetime.strptime(start, "%Y-%m-%d.%H:%M")
        else:
            # self.start_run = convert_run(start)
            self.start_run = start
            # self.date_start = self.data[self.start_run]["begin date"]
            self.date_start = self.data[self.start_run]["starttime0"]
            # s1 = self.date_start + " " + self.data[self.start_run]["start time"]
            # self.start = datetime.strptime(s1, "%m/%d/%Y %H:%M:%S")
            self.start = datetime.strptime(self.date_start, "%Y-%m-%dT%H:%M:%SZ")
            self.start = self.start + timedelta(hours=1)
        if not is_float(stop) and stop != "-1":
            self.stop = datetime.strptime(stop, "%Y-%m-%d.%H:%M")
            self.dia1 = "unknown"
            self.dia2 = "unknown"
            self.type = "time interval"
            # self.get_run_start_stop()
            self.time_mode = True
            self.update = False
        else:
            self.stop_run = self.get_stop_run(stop)
            # self.date_stop = self.data[self.stop_run]["begin date"]
            self.date_stop = self.data[self.stop_run]["endtime"]
            # self.stop = datetime.strptime(self.s2(), "%m/%d/%Y %H:%M:%S")
            self.stop = datetime.strptime(self.date_stop, "%Y-%m-%dT%H:%M:%SZ")
            self.stop = self.stop + timedelta(hours=1)
            self.update = True
            d1 = self.data[self.start_run]["dia1"]
            d2 = self.data[self.start_run]["dia2"]
            self.dia1 = d1 if d1 != "none" else "Diamond Front"
            self.dia2 = d2 if d2 != "none" else "Diamond Back"
            if self.dia1 == 'II6-96':
                self.dia1 = 'II6-95'
            self.flux = self.data[self.start_run]["measuredflux"]
            self.rate = self.data[self.start_run]["rawrate"]
            # self.pixels = self.data[self.start_run]["masked pixels"]
            self.type = self.data[self.start_run]["runtype"]

    def get_run_start_stop(self):
        found_start = False
        for run in range(int(convert_run(self.first)), int(convert_run(self.last))+1):
            date = self.data[str(run)]["begin date"]
            start = self.data[str(run)]["start time"]
            if self.start < datetime.strptime(date + " " + start, "%m/%d/%Y %H:%M:%S") and not found_start:
                self.run_start = int(str(run)[4:])
                found_start = True
            if self.stop != -1:
                if self.stop < datetime.strptime(date + " " + start, "%m/%d/%Y %H:%M:%S"):
                    self.run_stop = int(str(run-1)[4:])
                    break
            if self.data[str(run)]["diamond 1"] != "none":
                self.dia1 = self.data[str(run)]["dia1"]
                self.dia2 = self.data[str(run)]["dia2"]
        if not is_float(self.run_stop):
            self.run_stop = self.last

    def first_run(self):
        first_run = int(self.data.iterkeys().next())
        for run in self.data:
            if first_run > int(run):
                first_run = int(run)
        return int(first_run)

    def last_run(self):
        last_run = int(self.data.iterkeys().next())
        for run in self.data:
            if last_run < int(run):
                last_run = int(run)
        return int(last_run)

    def get_stop_run(self, stop):
        run = self.start_run
        if stop != '-1':
            # run = convert_run(stop)
            run = stop
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
        dia1 = self.data[str(self.first)]["dia1"]
        end = 0
        for run in range(self.first, self.last + 1):
            try:
                dia1_now = self.data[str(run)]["dia1"]
                dia2_now = self.data[str(run)]["dia2"]
                if dia1_now != dia1 and dia1_now != "none":
                    dia1 = dia1_now
                    dia2 = dia2_now
                    info = [str(dia1), str(dia2), run, end]
                    dia_runs.append(info)
                if dia1_now == dia1:
                    end = run
            except KeyError:
                continue
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


    def print_run_list(self):
        for run in range(int(self.run_start), int(self.run_stop)):
            try:
                if self.data[str(run)]['runtype'] == 'signal' or self.data[str(run)]['runtype'] == 'rate_scan':
                    print run, self.data[str(run)]['runtype'], '\t', \
                        self.data[str(run)]['dia1'], '\t', self.data[str(run)]['dia2'],\
                        "{0:6.1f}".format(self.data[str(run)]['measuredflux'])
            except KeyError:
                pass

if __name__ == '__main__':
    test = RunInfo('run_log.json_20150901', '340')
