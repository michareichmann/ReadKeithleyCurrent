#!/usr/bin/python

import argparse
import glob
import array
from datetime import datetime, time
from collections import OrderedDict

import ROOT

parser = argparse.ArgumentParser()
parser.add_argument("-l1", "--logsKeithley", nargs='?', default="logs/", help="enter the filepath of the Keithley-log")
parser.add_argument("-l2", "--logsEudaq", nargs='?', default="eudaq_logs/", help="enter the filepath of the EUDAQ-log")
parser.add_argument("-r", "--run", nargs='?', default="0", help="enter the runnumber without date information")
parser.add_argument("start", nargs='?', default="1111-01-01.00:00:00",
                    help="enter the runnumber without date information")
parser.add_argument("stop", nargs='?', default="2020-01-01.00:00:00",
                    help="enter the runnumber without date information")
args = parser.parse_args()

print "Looking for Run:", args.run


# function defintions
def convert_time(string):
    string = string.day * 24 * 3600 + string.hour * 3600 + string.minute * 60 + string.second
    return string

# get start and stop of the run from eudaq logfile
run_name = ""
if args.run > 99:
    run_name = "150500" + str(args.run)
elif args.run > 9:
    run_name = "1505000" + str(args.run)
time_start = ""
time_stop = "2015-12-31 23:59:59.999"
if args.run != "0":
    start_tag = "Starting Run " + run_name
    stop_tag = "Stopping Run " + run_name
    eudaq_log_dir = str(args.logsEudaq) + "2015-*"
    for name in glob.glob(eudaq_log_dir):
        logfile = open(name, 'r')
        for line in logfile:
            data = line.split("\t")
            if len(data) > 1:
                if data[1].startswith(start_tag):
                    time_start = data[2]
                    print "start:", data[2]
                if data[1].startswith(stop_tag):
                    time_stop = data[2]
                    print "stop: ", data[2]
        if len(time_start) > 3:
            break
        logfile.close()

    # example string: '2015-05-29 14:14:40.923'
    time_start = datetime.strptime(time_start, "%Y-%m-%d %H:%M:%S.%f")
    time_stop = datetime.strptime(time_stop, "%Y-%m-%d %H:%M:%S.%f")


# start and stop for noRun mode
if args.run == "0":
    bla1 = datetime.strptime(args.start, "%Y-%m-%d.%H:%M:%S")
    bla2 = datetime.strptime(args.stop, "%Y-%m-%d.%H:%M:%S")
    if bla1 < bla2:
        time_start = bla1
        time_stop = bla2
    else:
        time_start = bla2
        time_stop = bla1


# find file to begin with
keithley_log_dir = str(args.logsKeithley) + "keithleyLog_" + str(time_start.year) + "*"
log_names = []
for name in glob.glob(keithley_log_dir):
    log_names.append(name)
log_names = sorted(log_names)
last_line = False

begin_file = 0
for i in range(len(log_names)):
    data = open(log_names[i], 'r')
    for line in data:
        first_line = line.split()
        if len(first_line) == 0:
            break
        if first_line[1].startswith(str(time_start.year)):
            break
    if len(first_line) == 0:
        continue
    if first_line[1].startswith(str(time_start.year)):  # and last_line[1].startswith(str(time_start.year)):
        first_line = datetime.strptime(first_line[1] + " " + first_line[2], "%Y_%m_%d %H:%M:%S")
        # last_line = datetime.strptime(last_line[1]+" "+last_line[2], "%Y_%m_%d %H:%M:%S")
        if time_start < first_line:  # and time_start < last_line:
            begin_file = i - 1
            break
    data.close()

print "start with file:", log_names[begin_file]

# read out the currents from the Keithley logs
xx = {}
voltage = {}
current = {}
keithleys = OrderedDict([("Keithley1", "Silicon"), ("Keithley2", "Diamond front"), ("Keithley3", "Diamond back")])
for key in keithleys:
    xx[key] = []
    voltage[key] = []
    current[key] = []

for i in range(begin_file, len(log_names)):
    data = open(log_names[i], 'r')
    for line in data:
        info = line.split()
        if info[1].startswith(str(time_start.year)):
            time = datetime.strptime(info[1] + " " + info[2], "%Y_%m_%d %H:%M:%S")
            for key in keithleys:
                if len(info) > 3 and info[0].startswith(key):
                    if time_start < time < time_stop:
                        current[key].append(float(info[4]) * 1e9)
                        xx[key].append(convert_time(time))
                        voltage[key].append(float(info[3]))
            if time_stop < time:
                break
    data.close()

# create the canvas
canvas_name = "Keithley Currents for Run " + args.run
c = ROOT.TCanvas("c", canvas_name, 1000, 1000)
c.Divide(1, 3)
c.SetFillColor(70)
pads = []
graphs = []
axis = []
texts = []

# draw the graphs
for key, value in keithleys.items():
    ind = keithleys.items().index((key, value))
    c.cd(ind + 1)

    # Graph Current
    x = array.array('d', xx[key])
    y = array.array('d', current[key])
    g1 = ROOT.TGraph(len(x), x, y)
    g1.SetMarkerColor(2)
    g1.SetMarkerSize(0.5)
    g1.SetMarkerStyle(20)

    # Graph Voltage
    x = array.array('d', xx[key])
    y = array.array('d', voltage[key])
    g2 = ROOT.TGraph(len(x), x, y)
    g2.SetMarkerColor(4)
    g2.SetMarkerSize(0.5)
    g2.SetMarkerStyle(20)

    # first pad
    p1 = ROOT.TPad("p1", "test", 0, 0, 1, 1)
    p1.SetTitle("test1")
    p1.SetFillColor(67)
    p1.SetGridx()
    p1.Draw()
    p1.cd()

    dy = 0.1 * (max(current[key]) - min(current[key]))
    dx = 0.05 * (max(xx[key]) - min(xx[key]))
    h1 = c.DrawFrame(min(xx[key])-dx, min(current[key]) - dy, max(xx[key])+dx, max(current[key]) + dy)
    # X-axis
    h1.GetXaxis().SetTitle("#font[22]{time [hh:mm]}")
    h1.GetXaxis().CenterTitle()
    h1.GetXaxis().SetTimeFormat("%H:%M")
    h1.GetXaxis().SetTimeOffset(1486249200)
    h1.GetXaxis().SetTimeDisplay(1)
    h1.GetXaxis().SetLabelSize(0.05)
    h1.GetXaxis().SetTitleSize(0.06)
    h1.GetXaxis().SetTitleOffset(0.9)
    h1.SetTitleSize(0.05)
    # Y-axis
    h1.GetYaxis().SetTitleOffset(0.69)
    h1.GetYaxis().SetTitle("#font[22]{current [nA]}")
    h1.GetYaxis().CenterTitle()
    h1.GetYaxis().SetLabelSize(0.05)
    h1.GetYaxis().SetTitleSize(0.06)
    h1.GetYaxis().SetTitleOffset(0.7)
    # pad
    p1.SetTitle(key)
    p1.GetFrame().SetFillColor(21)
    p1.GetFrame().SetBorderSize(12)

    g1.Draw("P")

    # second pad
    p2 = ROOT.TPad("p2_" + key, "", 0, 0, 1, 1)
    p2.SetFillStyle(4000)
    p2.SetFillColor(0)
    p2.SetFrameFillStyle(4000)
    p2.SetGridy()
    p2.Draw()
    p2.cd()

    h2 = p2.DrawFrame(min(xx[key]) - dx, -1100, max(xx[key]) + dx, 1100)
    h2.GetXaxis().SetTickLength(0)
    h2.GetYaxis().SetTickLength(0)
    h2.GetXaxis().SetLabelOffset(99)
    h2.GetYaxis().SetLabelOffset(99)

    g2.Draw("P")

    # draw the second axis
    a1 = ROOT.TGaxis(max(xx[key])+dx, -1100, max(xx[key])+dx, 1100, -1100, 1100, 510, "+L")
    a1.SetTitle("#font[22]{voltage [V]}")
    a1.SetTitleSize(0.06)
    a1.SetTitleOffset(0.5)
    a1.CenterTitle()
    a1.SetTitleColor(4)
    a1.SetLabelSize(0.05)
    a1.SetLineColor(4)
    a1.SetLabelColor(4)
    a1.SetLabelOffset(0.01)
    a1.Draw()

    c.Update()

    # save the stuff s.t. it wont get lost in the loop
    axis.append(a1)
    graphs.append(g1)
    graphs.append(g2)
    pads.append(p1)
    pads.append(p2)

    # third pad
    p3 = ROOT.TPad("p3_" + key, "", 0, 0, 1, 1)
    p3.SetFillStyle(4000)
    p3.SetFillColor(0)
    p3.SetFrameFillStyle(4000)
    p3.Draw()
    p3.cd()
    t22 = ROOT.TText(0.1,0.92,value)
    t22.SetTextSize(0.09)
    t22.Draw()
    texts.append(t22)

    # axis_title = ROOT.TPaveText(.1, .1, .9, .9)
    # axis_title.AddText("voltage [V]")
    # # axis.SetTextSize(0.05)
    # axis_title.Draw()

c.Update()
filename = "Run"+str(args.run)+".png"
c.SaveAs(filename)

# raw_input()
