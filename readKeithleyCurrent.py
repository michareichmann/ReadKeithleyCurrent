#!/usr/bin/python

# ====================================
# IMPORTS
# ====================================
import argparse
from time import time, sleep
from KeithleyInfo import KeithleyInfo
from RunInfo import RunInfo
import functions
import functions1
from root_stuff import RootGraphs
from ROOT import gROOT
import signal
import sys
from analysis import Analysis

# measure time:
start_time = time()

# ====================================
# PARSER
# ====================================
parser = argparse.ArgumentParser()
default_json_file = "/home/testbeam/sdvlp/eudaqLogReader/runs_PSI_August_2015.json"
default_log_file1 = "/home/testbeam/sdvlp/keithleyClient/PSI_2015_08/Keithley237"
default_log_file2 = "/home/testbeam/sdvlp/keithleyClient/PSI_2015_08/Keithley2657A"
parser.add_argument("-d1", "--logsKeithley1", nargs='?', default=default_log_file1, help="enter the filepath of the Keithley-log")
parser.add_argument("-d2", "--logsKeithley2", nargs='?', default=default_log_file2, help="enter the filepath of the Keithley-log")
parser.add_argument("-j", "--jsonfile", nargs='?', default=default_json_file, help="enter the name of the json file")
parser.add_argument("-fl", "--first_last", action="store_true", help="enter to show first and last run")
parser.add_argument("start", nargs='?', default="-1",
                    help="enter the runnumber without date information")
parser.add_argument("stop", nargs='?', default="-1",
                    help="enter the runnumber without date information")
parser.add_argument("-s", "--save", action="store_true", help="enter -s to save the file")
parser.add_argument("-f", "--fileformat", nargs='?', default="pdf", help="enter file format e.g. pdf")
parser.add_argument("-rt", "--rel_time", action="store_true", help="enter -rt to start the time axis from zero")
parser.add_argument("-dr", "--dia_runs", action="store_true", help="enter -d to plot the current as long as dia was in")
parser.add_argument("-a", "--averaging", action="store_true", help="enter -d for averaging")
parser.add_argument("-n", "--number", nargs='?', default="2", help="enter number of keithleys")
parser.add_argument("-ap", "--points", nargs='?', default="10", help="number of averaging points")
args = parser.parse_args()

logs = [args.logsKeithley1, args.logsKeithley2]
r1 = functions1.convert_date(args.start)
r2 = functions1.convert_date(args.stop)

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
run_mode = True
if args.stop != "-1":
    run_mode = False


# ====================================
# SHOW THE RUNS PER DIAMOND
# ====================================
if args.dia_runs:
    x = RunInfo(args.jsonfile)
    x.print_dia_runs()
    print 'elapsed time:', functions.elapsed_time(start_time)
    exit()

# ====================================
# SHOW FIRST ANS LAST RUN
# ====================================
if args.first_last:
    x = RunInfo(args.jsonfile)
    x.print_times()
    print 'elapsed time:', functions.elapsed_time(start_time)
    exit()


# ====================================
# GET INFO FROM JSON AND KEIHTLEY LOG
# ====================================
log_dir = ["", ""]
log_dir[0] = functions1.get_log_dir(logs[0])
log_dir[1] = functions1.get_log_dir(logs[1])
x = KeithleyInfo(log_dir, args.jsonfile, r1, r2, args.number, args.averaging, args.points)
print "starting with log file:", x.log_names["Keithley1"][0]
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
# SAVING DATA
# ====================================
if args.save:
    z.save_as(args.fileformat)

# ====================================
# UPDATE LOOP
# ====================================
signal.signal(signal.SIGINT, signal_handler)
while True:
    print "\r%s"%time(),
    sys.stdout.flush()
    x.find_data()
    z.main_loop()
    sleep(10)




