#!/usr/bin/python

import argparse
import glob
import array
from datetime import datetime, time
from collections import OrderedDict
import functions
import root_stuff
import ROOT

parser = argparse.ArgumentParser()
parser.add_argument("-l1", "--logsKeithley", nargs='?', default="logs/", help="enter the filepath of the Keithley-log")
parser.add_argument("-l2", "--logsEudaq", nargs='?', default="eudaq_logs/", help="enter the filepath of the EUDAQ-log")
parser.add_argument("-r", "--run", nargs='?', default="0", help="enter the runnumber without date information")
parser.add_argument("start", nargs='?', default="1111-01-01.00:00:00",
                    help="enter the runnumber without date information")
parser.add_argument("stop", nargs='?', default="2020-01-01.00:00:00",
                    help="enter the runnumber without date information")
parser.add_argument("-s", "--save", action="store_true", help="enter -s to save the file")
parser.add_argument("-f", "--fileformat", nargs='?', default="png", help="enter file format e.g. pdf")
args = parser.parse_args()

time_interval = functions.get_start_stop(args.run, args.logsEudaq, args.start, args.stop)

log_names = functions.find_start_file(args.logsKeithley, time_interval)


# read out the currents from the Keithley logs
xx = {}
voltage = {}
current = {}
keithleys = OrderedDict([("Keithley1", "Silicon"), ("Keithley2", "Diamond front"), ("Keithley3", "Diamond back")])
for key in keithleys:
    xx[key] = []
    voltage[key] = []
    current[key] = []

for name in log_names:
    data = open(name, 'r')
    for line in data:
        info = line.split()
        if info[1].startswith(str(time_interval[0].year)):
            time = datetime.strptime(info[1] + " " + info[2], "%Y_%m_%d %H:%M:%S")
            for key in keithleys:
                if len(info) > 3 and info[0].startswith(key):
                    if time_interval[0] < time < time_interval[1]:
                        current[key].append(float(info[4]) * 1e9)
                        xx[key].append(functions.convert_time(time))
                        voltage[key].append(float(info[3]))
            if time_interval[1] < time:
                break
    data.close()

# check if empty
for key in keithleys:
    if len(xx[key]) == 0:
        xx[key] = [functions.convert_time(time_interval[0]), functions.convert_time(time_interval[1])]
    if len(current[key]) == 0:
        current[key] = [0]
    if len(voltage[key]) == 0:
        voltage[key] = [0]

# create the canvas
if args.save:
    ROOT.gROOT.SetBatch(1)

canvas_name = ""
if args.run == "0":
    canvas_name = "Keithley Currents from " + args.start + " to " + args.stop
else:
    canvas_name = "Keithley Currents for Run " + args.run
c = ROOT.TCanvas("c", canvas_name, 1000, 1000)
c.Divide(1, 3)
c.SetFillColor(17)
pads = []
graphs = []
axis = []
texts = []

# draw the graphs
for key, value in keithleys.items():
    ind = keithleys.items().index((key, value))
    c.cd(ind + 1)

    # Graph Current
    g1 = root_stuff.graph1(key, xx, current)

    # Graph Voltage
    g2 = root_stuff.graph2(key, xx, voltage)

    # pad for graph g1
    p1 = root_stuff.pad1(key)

    # get edges of the frame
    dy = 0.1 * (max(current[key]) - min(current[key]))
    dx = 0.05 * (max(xx[key]) - min(xx[key]))
    h1 = root_stuff.frame1(c, key, xx, current, dx, dy)
    p1.GetFrame().SetFillColor(21)
    p1.GetFrame().SetBorderSize(12)

    g1.Draw("P")

    # pad for graph g2
    p2 = root_stuff.pad2(key)
    h2 = root_stuff.frame2(key, xx, dx, p2)

    g2.Draw("P")

    # second y-axis
    a1 = root_stuff.axis1(key, xx, dx)

    # title pad
    p3 = root_stuff.pad3(key)
    t1 = root_stuff.text1(value)

    # save the stuff s.t. it wont get lost in the loop
    axis.append(a1)
    graphs.append(g1)
    graphs.append(g2)
    pads.append(p1)
    pads.append(p2)
    pads.append(p3)
    texts.append(t1)

c.Update()

if args.save:
    filename = "runs/run" + str(args.run) + "." + str(args.fileformat)
    c.SaveAs(filename)

if not args.save:
    raw_input()
