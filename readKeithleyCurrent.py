#!/usr/bin/python

# ====================================
# IMPORTS
# ====================================
import json
import argparse
import glob
import array
from datetime import datetime, time
from time import time
from collections import OrderedDict
from functions import RunInfo, KeithleyInfo
import functions
import root_stuff
import ROOT

# measure time:
start_time = time()

# ====================================
# PARSER
# ====================================
parser = argparse.ArgumentParser()
parser.add_argument("-l1", "--logsKeithley", nargs='?', default="logs/", help="enter the filepath of the Keithley-log")
parser.add_argument("-l2", "--jsonfile", nargs='?', default="test.json", help="enter the name of the json file")
parser.add_argument("-fl", "--first_last", action="store_true", help="enter to show first and last run")
parser.add_argument("start", nargs='?', default="-1",
                    help="enter the runnumber without date information")
parser.add_argument("stop", nargs='?', default="-1",
                    help="enter the runnumber without date information")
parser.add_argument("-s", "--save", action="store_true", help="enter -s to save the file")
parser.add_argument("-f", "--fileformat", nargs='?', default="pdf", help="enter file format e.g. pdf")
parser.add_argument("-rt", "--rel_time", action="store_true", help="enter -rt to start the time axis from zero")
parser.add_argument("-d", "--dia_runs", action="store_true", help="enter -d to plot the current as long as dia was in")
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
    # for i in x.dia_runs():
    #     print i
    x.elapsed_time(start_time)
    exit()

# ====================================
# SHOW FIRST ANS LAST RUN
# ====================================
if args.first_last:
    x = RunInfo(args.jsonfile)
    x.print_times()
    x.elapsed_time(start_time)
    exit()


# ====================================
# GET INFO FROM JSON AND KEIHTLEY LOG
# ====================================
x = KeithleyInfo(args.logsKeithley, args.jsonfile, args.start, args.stop)
print x.log_names[0]
if not args.save:
    print 'start:', x.start
    print 'stop: ', x.stop
    print 'this took ', time() - start_time, ' seconds'

# convert to relative time
if args.rel_time:
    x.relative_time()

# create the canvas
if args.save:
    ROOT.gROOT.SetBatch(1)

canvas_name = "Keithley Currents for Run " + args.start
if not run_mode:
    canvas_name = "Keithley Currents from " + args.start + " to " + args.stop

c = ROOT.TCanvas("c", canvas_name, 1000, 1000)
# c.Divide(1, 3)
c.SetFillColor(0)  # was 17
objects = []

space = 0.015
title = 0.93
p5 = ROOT.TPad("p5", "", space, space, 1 - space, title / 3 - space / 2)
p6 = ROOT.TPad("p6", "", space, title / 3 + space / 2, 1 - space, title * 2 / 3 - space / 2)
p7 = ROOT.TPad("p7", "", space, title * 2 / 3 + space / 2, 1 - space, title - space / 2)
p8 = ROOT.TPad("p8", "", space, title, 1 - space, 1)
p5.Draw()
p6.Draw()
p7.Draw()
p8.Draw()

p8.cd()
# pt = ROOT.TPaveText(.02,.1,.98,.9)
title_text1 = "PSI" + functions.convert_run(args.start)
title_text2 = "Flux = " + str(x.flux) + " kHz/cm^{2}"
if not run_mode:
    bla = str((int(args.stop) + int(args.start)) / 2)
    title_text1 = "PSI" + functions.convert_run(args.start) + " - " + args.stop
    title_text2 = 'all runs of ' + x.get_info(bla, "diamond 1") + ' & ' + x.get_info(bla, "diamond 2")

t2 = ROOT.TText(0.01, 0.31, title_text1)
t2.SetTextSize(0.5)
t2.SetTextAlign(11)

t3 = ROOT.TText(0.99, 0.31, title_text2)
t3.SetTextSize(0.5)
t3.SetTextAlign(31)
t3.Draw()
t2.Draw()


def get_pad(index):
    if index == 0:
        p7.cd()
    elif index == 1:
        p6.cd()
    elif index == 2:
        p5.cd()

# draw the graphs
for key, value in x.keithleys.items():
    ind = x.keithleys.items().index((key, value))
    # c.cd(ind + 1)
    get_pad(ind)

    # get edges of the frame
    dx = x.dx[key]
    dy = x.dy[key]
    ymax = max(x.current_y[key]) + dy
    ymin = min(x.current_y[key]) - dy

    # Graph Current
    g1 = root_stuff.graph1(key, x.time_x, x.current_y)

    # Graph Voltage
    g2 = root_stuff.graph2(key, x.time_x, x.voltage_y)

    # pad for graph g2
    p1 = root_stuff.pad1(key)
    h2 = root_stuff.frame2(key, x.time_x, dx, p1)
    # p1.GetFrame().SetFillColor(0)  # was 21
    g2.Draw("P")

    # second y-axis
    a1 = root_stuff.axis1(key, x.time_x, dx)

    # title pad
    p3 = root_stuff.pad3(key)
    t1 = root_stuff.text1(value)

    # border pad
    p4 = root_stuff.pad4(key)
    b1 = root_stuff.box1()

    # pad for graph g1
    p2 = root_stuff.pad2(key)
    h1 = root_stuff.frame1(p2, key, x.time_x, x.current_y, dx, dy)
    if not run_mode:
        for i in range(int(args.start), int(args.stop) + 1):
            s1 = functions.convert_time(x.get_time(i, "start time"))
            s2 = functions.convert_time(x.get_time(i, "stop time"))
            a2 = ROOT.TGaxis(s1, ymin, s1, ymax, ymin, ymax, 510, "+SU")
            tit = "run " + str(i) + "  "
            a2.SetTitle(tit)
            a2.SetLineColor(1)
            a2.SetTickSize(0)
            a2.SetLabelSize(0)
            a2.SetTitleSize(0.05)
            a2.SetTitleOffset(0.1)
            a3 = ROOT.TGaxis(s2, ymin, s2, ymax, ymin, ymax, 510, "-SU")
            a3.SetLineColor(13)
            a3.SetTickSize(0)
            a3.SetLabelSize(0)
            # draw only for runs longer than 4 minutes
            if s2 - s1 > 20 * 60:
                a2.Draw()
                a3.Draw()
            objects.append(a2)
            objects.append(a3)
    g1.Draw("P")

    # save the stuff s.t. it wont get lost in the loop
    objects.append(a1)
    objects.append(g1)
    objects.append(g2)
    objects.append(p1)
    objects.append(p2)
    objects.append(p3)
    objects.append(t1)
    objects.append(b1)
    # objects.append(cutg2)

c.Update()

if args.save:
    root_stuff.save_as(args.fileformat, c, args.start, args.stop)

print "this took", time() - start_time, "seconds"

if not args.save:
    raw_input()
