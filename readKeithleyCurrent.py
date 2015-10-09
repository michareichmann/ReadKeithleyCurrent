#!/usr/bin/python

# ====================================
# IMPORTS
# ====================================
import argparse
from time import time, sleep, strftime, localtime
from KeithleyInfo import KeithleyInfo
from KeithleyInfoOld import KeithleyInfoOld
from RunInfo import RunInfo
from RunInfoOld import RunInfoOld
import functions
import functions1
from root_stuff import RootGraphs
from ROOT import gROOT
import signal
import sys
from analysis import Analysis
from collections import OrderedDict

# measure time:
start_time = time()


# ====================================
# DEFAULTS
# ====================================
default_json_file = "/home/testbeam/sdvlp/readKeithleyCurrent/run_log.json_20150901"
default_log_file1 = "/home/testbeam/sdvlp/keithleyClient/PSI_2015_08/Keithley237"
default_log_file2 = "/home/testbeam/sdvlp/keithleyClient/PSI_2015_08/Keithley2657A"
json_files = OrderedDict([("May", '/home/testbeam/sdvlp/readKeithleyCurrent/runs_PSI_May_2015.json'),
                        ("August", '/home/testbeam/sdvlp/readKeithleyCurrent/run_log.json_20150901')])
hv_logs_may = '/data/psi_2015_05/logs_keithley/'

# ====================================
# PARSER
# ====================================
parser = argparse.ArgumentParser()
# default_json_file = "/home/testbeam/sdvlp/eudaqLogReader/runs_PSI_August_2015.json"
parser.add_argument("-d1", "--logsKeithley1", nargs='?', default=default_log_file1, help="enter the filepath of the Keithley-log")
parser.add_argument("-d2", "--logsKeithley2", nargs='?', default=default_log_file2, help="enter the filepath of the Keithley-log")
parser.add_argument("-j", "--jsonfile", nargs='?', default=default_json_file, help="enter the name of the json file")
parser.add_argument("-fl", "--first_last", action="store_true", help="enter to show first and last run")
parser.add_argument("start", nargs='?', default="-1",
                    help="enter the runnumber without date information")
parser.add_argument("stop", nargs='?', default="-1",
                    help="enter the runnumber without date information")
parser.add_argument("-s", "--save", action="store_true", help="enter -s to save the file")
parser.add_argument("-f", "--fileformat", nargs='?', default="png", help="enter file format e.g. pdf")
parser.add_argument("-rt", "--rel_time", action="store_true", help="enter -rt to start the time axis from zero")
parser.add_argument("-dr", "--dia_runs", action="store_true", help="enter -d to plot the current as long as dia was in")
parser.add_argument("-a", "--averaging", action="store_true", help="enter -d for averaging")
parser.add_argument("-n", "--number", nargs='?', default="2", help="enter number of keithleys")
parser.add_argument("-ap", "--points", nargs='?', default="10", help="number of averaging points")
parser.add_argument("-l", "--loop_mode", action="store_true", help="enter -d for looping")
parser.add_argument("-c", "--back", nargs='?', default="24", help="hours to go back", type=int)
parser.add_argument("-tb", "--testbeam", nargs='?', default="August", help="test campaing")
parser.add_argument("-rp", "--runplan", action="store_true", help="print runplan")


args = parser.parse_args()

logs = [args.logsKeithley1, args.logsKeithley2]
if args.start != "-1":
    r1 = functions1.convert_date(args.start)
    r2 = functions1.convert_date(args.stop)
else:
    r1 = functions1.plot24(0, args.back)
    r2 = functions1.plot24(1, args.back)
loop_mode = True if args.loop_mode else False

# ====================================
# SIGNAL HANDLER
# ====================================
def signal_handler(signal, frame):
    print '\nReceived SIGINT'
    print 'whole sequence:', functions.elapsed_time(start_time)
    print 'exiting Programm'
    exit()

# ====================================
# SINGLE RUN MODE
# ====================================
run_mode = False
try:
    int(r1)
    run_mode = True
except ValueError:
    pass


# ====================================
# SHOW THE RUN PLAN
# ====================================
if args.runplan:
    x = RunInfo(json_files[args.testbeam], r1, r2)
    x.print_run_list()
    exit()

# ====================================
# SHOW THE RUNS PER DIAMOND
# ====================================
if args.dia_runs:
    if args.testbeam == 'May':
        x = RunInfoOld(json_files[args.testbeam])
    else:
        x = RunInfo(json_files[args.testbeam])
    x.print_dia_runs()
    print 'elapsed time:', functions.elapsed_time(start_time)
    exit()

# ====================================
# SHOW FIRST ANS LAST RUN
# ====================================
if args.first_last:
    if args.testbeam == 'May':
        x = RunInfoOld(json_files[args.testbeam])
    else:
        x = RunInfo(json_files[args.testbeam])
    x.print_times()
    print 'elapsed time:', functions.elapsed_time(start_time)
    exit()


# ====================================
# GET INFO FROM JSON AND KEIHTLEY LOG
# ====================================
log_dir = ["", ""]
log_dir[0] = functions1.get_log_dir(logs[0])
log_dir[1] = functions1.get_log_dir(logs[1])
if args.testbeam == 'May':
    x = KeithleyInfoOld(hv_logs_may, json_files[args.testbeam], r1, r2, args.number)
else:
    x = KeithleyInfo(log_dir, args.jsonfile, r1, r2, args.number, args.averaging, args.points)
    print "starting with log files:"
    for key in x.keithleys:
        print key + ":", x.log_names[key][0].split("/")[-1]
if not args.save:
    print 'start:', x.start
    print 'stop: ', x.stop
    print 'class instantiation:', functions.elapsed_time(start_time)

# convert to relative time
if args.rel_time:
    x.relative_time()


# ====================================
# PROCESS DATA WITH ROOT
# ====================================
# switch off printing the canvas for the save mode
if args.save:
    gROOT.SetBatch(1)

# start class instance
do_histo = False
if not do_histo:
    z = RootGraphs(x, run_mode, args.number)
    z.init_loop()
else:
    z = RootGraphs(x, run_mode, args.number)
    test = Analysis(x, run_mode, args.number)
    test.main_loop()




# ====================================
# UPDATE LOOP
# ====================================
if loop_mode:
    signal.signal(signal.SIGINT, signal_handler)
    print "\nStarting loop-mode!"
    while True:
        print "\rlast update:", strftime("%H:%M:%S", localtime()),
        sys.stdout.flush()
        x.update_data()
        z.refresh_graphs()
        z.make_margins()
        z.main_loop()
        sleep(10)
else:
    z.main_loop()
    if not args.save:
        raw_input()

# ====================================
# SAVING DATA
# ====================================
if args.save:
    z.save_as(args.fileformat)





