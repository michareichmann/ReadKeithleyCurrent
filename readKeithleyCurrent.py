#!/usr/bin/python

import argparse, glob
import ROOT
import numpy as n
import array
from datetime import datetime, date, time
from collections import OrderedDict

parser = argparse.ArgumentParser()
parser.add_argument("-l1","--logsKeithley", nargs='?', default="logs/",help="enter the filepath of the Keithley-log")
parser.add_argument("-l2","--logsEudaq", nargs='?', default="eudaq_logs/",help="enter the filepath of the EUDAQ-log")
parser.add_argument("-r", "--run", nargs='?', default="0",help="enter the runnumber without date information")
parser.add_argument("start", nargs='?', default="1111-01-01.00:00:00",help="enter the runnumber without date information")
parser.add_argument("stop", nargs='?', default="2020-01-01.00:00:00",help="enter the runnumber without date information")
args = parser.parse_args()

print "Looking for Run:", args.run
def convertTime(string):
    string = string.day*24*3600+string.hour*3600 + string.minute*60 + string.second
    return string

## get start and stop of the run from eudaq logfile
if args.run > 99:
    runname = "150500"+str(args.run)
elif args.run >9:
    runname = "1505000"+str(args.run)
time_start = ""
time_stop = "2015-12-31 23:59:59.999"
if args.run != "0":
    start_tag = "Starting Run "+runname
    stop_tag  = "Stopping Run "+runname
    eudaq_log_dir = str(args.logsEudaq)+"2015-*"
    for name in glob.glob(eudaq_log_dir):
        logfile = open(name,'r')
        for line in logfile:
            data = line.split("\t")
            if len(data)>1:
                if data[1].startswith(start_tag):
                    time_start = data[2]
                    print "start:", data[2]
                if data[1].startswith(stop_tag):
                    time_stop = data[2]
                    print "stop: ", data[2]
        if len(time_start) > 3:
            break
    logfile.close()


    #example string: '2015-05-29 14:14:40.923'
    time_start = datetime.strptime(time_start, "%Y-%m-%d %H:%M:%S.%f")
    time_stop  = datetime.strptime(time_stop, "%Y-%m-%d %H:%M:%S.%f")


#start and stop for noRun mode
if args.run == "0":
    bla1 = datetime.strptime(args.start, "%Y-%m-%d.%H:%M:%S")
    bla2 = datetime.strptime(args.stop, "%Y-%m-%d.%H:%M:%S")
    if bla1 < bla2:
        time_start = bla1
        time_stop  = bla2
    else:
        time_start = bla2
        time_stop  = bla1


#find file to begin with
keithley_log_dir = str(args.logsKeithley)+"keithleyLog_"+str(time_start.year)+"*"
log_names = []
for name in glob.glob(keithley_log_dir):
    log_names.append(name)
log_names = sorted(log_names)
last_line = False

begin_file = 0
for i in range(len(log_names)):
    data = open(log_names[i],'r')
    for line in data:
        first_line = line.split()
        if len(first_line) == 0: break
        if first_line[1].startswith(str(time_start.year)): break
    if len(first_line) == 0:
        continue
    if first_line[1].startswith(str(time_start.year)):# and last_line[1].startswith(str(time_start.year)):
        first_line = datetime.strptime(first_line[1]+" "+first_line[2], "%Y_%m_%d %H:%M:%S")
        #last_line = datetime.strptime(last_line[1]+" "+last_line[2], "%Y_%m_%d %H:%M:%S")
        if time_start < first_line:# and time_start < last_line:
            begin_file = i-1
            break
    data.close()

print "start with file:", log_names[begin_file]

##read out the currents from the Keithley logs
xx      = {}
voltage = {}
current = {}
keithleys = OrderedDict([("Keithley1","Silicon"),("Keithley2","Diamond front"),("Keithley3","Diamond back")])
for key in keithleys:
    xx[key]         = []
    voltage[key]    = []
    current[key]    = []

for i in range(begin_file,len(log_names)):
    data = open(log_names[i],'r')
    for line in data:
        info = line.split()
        if info[1].startswith(str(time_start.year)):
            time = datetime.strptime(info[1]+" "+info[2], "%Y_%m_%d %H:%M:%S")
            for key in keithleys:
                if len(info) > 3 and info[0].startswith(key):
                    if time > time_start and time < time_stop:
                        current[key].append(float(info[4])*1e9)
                        xx[key].append(convertTime(time))
                        voltage[key].append(float(info[3]))
            if time_stop < time:
                break
    data.close()



## create the canvas
canvas_name = "Keithley Currents for Run"+args.run
c = ROOT.TCanvas("c",canvas_name,1500,1000 )
c.Divide(2,3)
c.SetFillColor(39)
pads = []
graphs = []

## draw the graphs
#Keithley1
for key, value in keithleys.items():
    ind = keithleys.items().index((key,value))
    c.cd(ind*2+1)
    # pad1 = ROOT.TPad("pad1_"+key,"",0,0,1,1)
#    pad2 = ROOT.TPad("pad2_"+key,"",0,0,1,1)
#    pad2.SetFillStyle(4000) # transparent
#     pad1.Draw()
#     pad1.cd(ind+1)
#     print pad1
    x = array.array('d',xx[key])
    y = array.array('d',current[key])
    g = ROOT.TGraph(len(x),x,y)
    g.Draw("AP")

    #g.SetTitle(value)
    g.GetHistogram().SetTitle(value)
    #g.GetHistogram().SetTitleSize(0.5)
    #g.GetHistogram().SetTitleFont(60)
    ##X-axis
    g.GetXaxis().SetTitle("#font[22]{time [hh:mm:ss]}")
    g.GetXaxis().CenterTitle()
    g.GetXaxis().SetTimeFormat("%H:%M")
    g.GetXaxis().SetTimeOffset(1486249200)
    g.GetXaxis().SetTimeDisplay(1)
    g.GetXaxis().SetTitleSize(0.05)
    g.GetXaxis().SetLabelSize(0.05)
    g.GetXaxis().SetTitleOffset(0.90)
    ##Y-axis
    g.GetYaxis().SetTitleOffset(0.69)
    g.GetYaxis().SetTitle("#font[22]{current [nA]}")
    g.GetYaxis().CenterTitle()
    g.GetYaxis().SetLabelSize(0.05)
    g.GetYaxis().SetTitleSize(0.06)
    g.GetYaxis().SetTitleOffset(0.69)
    ##graph
    g.SetMarkerColor(2)
    g.SetMarkerSize(0.2)
    g.SetMarkerStyle(20)
    c.cd(ind*2+1).SetGridx(10)
    g.Draw("AP")
    graphs.append(g)
#
#    ymin = min(voltage[key])
#    ymax = max(voltage[key])
#    if ymin == ymax:
#        if ymin<0:
#            ymax =0
#        else:
#            ymin = 0
#    print ymax, ymin,g.GetHistogram().GetYaxis().GetXmin(),g.GetHistogram().GetYaxis().GetXmax()
#    dy = (ymax-ymin)/0.8
#    xmin = pad1.GetUxmin()
#    xmax = pad1.GetUxmax()
#    print xmin,xmax,bla,blub
#    dx = (xmax-xmin)/0.8
#    pad2.Range(xmin,ymin-0.1-dy, xmax, ymax+0.1*dy)
#    c.cd(ind+1)
#    pad2.Draw()
#    pad2.cd()
    c.cd(ind*2+2)
    c.cd(ind*2+2).SetGridy(10)
    x = array.array('d',xx[key])
    y = array.array('d',voltage[key])
    g2 = ROOT.TGraph(len(x),x,y)
    g2.GetHistogram().SetTitle(value)
    g2.GetYaxis().SetRangeUser(-1100,1100)
    g2.GetXaxis().SetTitle("#font[22]{time [hh:mm:ss]}")
    g2.GetXaxis().CenterTitle()
    g2.GetXaxis().SetTimeFormat("%H:%M")
    g2.GetXaxis().SetTimeOffset(1486249200)
    g2.GetXaxis().SetTimeDisplay(1)
    g2.GetXaxis().SetTitleSize(0.05)
    g2.GetXaxis().SetLabelSize(0.05)
    g2.GetXaxis().SetTitleOffset(0.90)
    g2.GetYaxis().SetTitleOffset(0.69)
    g2.GetYaxis().SetTitle("#font[22]{voltage [V]}")
    g2.GetYaxis().CenterTitle()
    g2.GetYaxis().SetLabelSize(0.05)
    g2.GetYaxis().SetTitleSize(0.06)
    g2.GetYaxis().SetTitleOffset(0.69)
    g2.SetMarkerColor(4)
    g2.SetMarkerSize(0.2)
    g2.SetMarkerStyle(20)
    g2.Draw("AP")
    graphs.append(g2)
#    pads.append(pad1)
#    pads.append(pad2)

c.Update()


raw_input()
