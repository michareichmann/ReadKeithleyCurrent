# ====================================
# IMPORTS
# ====================================
import glob
from datetime import datetime
from collections import OrderedDict
from RunInfoOld import RunInfoOld
from functions1 import convert_time


class KeithleyInfoOld(RunInfoOld):
    """reads in information from the keithley log file"""

    def __init__(self, log, jsonfile, start, stop, number):
        self.single_mode = (True if number == "1" else False)
        self.number = number
        RunInfoOld.__init__(self, jsonfile, start, stop)
        hv_name = 'Keithley'
        self.keithleys = OrderedDict([])
        self.device_names = ['Silicon', str(self.dia1), str(self.dia2)]
        if number == '1':
            self.keithleys = OrderedDict([("Keithley2", self.device_names[1])])
        elif number == '2':
            for i in range(1, 3):
                self.keithleys.update({hv_name + str(i + 1): self.device_names[i]})
        else:
            for i in range(int(number)):
                self.keithleys.update({hv_name + str(i + 1): self.device_names[i]})
        self.log_dir = str(log) + "keithleyLog_" + str(self.start.year) + "*"
        self.log_names = self.logs_from_start()
        data = self.find_data()
        self.time_x = data[0]
        self.current_y = data[1]
        self.voltage_y = data[2]
        self.dias = self.make_dict(self.dia1, self.dia2)

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

    def make_dict(self, arg1, arg2):
        if self.number == '1':
            return OrderedDict([("Keithley1", arg1)])
        elif self.number == "2":
            return OrderedDict([("Keithley2", arg1),
                                ("Keithley3", arg2)])


if __name__ == '__main__':
    test = KeithleyInfoOld('/data/psi_2015_05/logs_keithley/', 'runs_PSI_May_2015.json', '340', '-1', '2')
