#!/usr/bin/python

# ====================================
# IMPORTS
# ====================================
import argparse
from time import time
from functions1 import RunInfo, KeithleyInfo
import functions
from root_stuff import RootGraphs
from ROOT import gROOT
from analysis import Analysis

# measure time:
start_time = time()

# ====================================
# PARSER
# ====================================
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--logsKeithley", nargs='?', default="logs/", help="enter the filepath of the Keithley-log")
parser.add_argument("-j", "--jsonfile", nargs='?', default="test.json", help="enter the name of the json file")
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
parser.add_argument("-n", "--number", nargs='?', default="1", help="enter number of keithleys")
args = parser.parse_args()


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
x = KeithleyInfo(args.logsKeithley, args.jsonfile, args.start, args.stop, args.number, args.averaging)
print "starting with log file:", x.log_names[0]
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
    z.main_loop()
else:
    test = Analysis(x, run_mode, args.number)
    test.main_loop()



# ====================================
# SAVING DATA
# ====================================
if args.save:
    z.save_as(args.fileformat)

# print time information
print 'whole sequence:', functions.elapsed_time(start_time)

# input to look at the data
if not args.save:
    raw_input()
