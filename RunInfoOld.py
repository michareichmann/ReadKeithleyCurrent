# ====================================
# IMPORTS
# ====================================
from datetime import datetime
import json
from collections import OrderedDict
from functions1 import convert_run, is_float


# ====================================
# CLASS FOR RUN INFO FROM JSON
# ====================================
class RunInfoOld:
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
        if not is_float(self.run_stop):
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


if __name__ == '__main__':
    test = RunInfoOld('runs_PSI_May_2015.json', '340')
