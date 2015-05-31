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
#logfile = open(args.l2)
if args.run > 99:
    runname = "150500"+str(args.run)
elif args.run >9:
    runname = "1505000"+str(args.run)
start_tag = "Starting Run "+runname
stop_tag  = "Stopping Run "+runname
time_start = ""
time_stop = "2015-12-31 23:59:59.999"
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
run_start  = convertTime(time_start)
run_stop   = convertTime(time_stop)
date = time_start.strftime("%Y-%m-%d")#time_start.

bla1 = datetime.strptime(args.start, "%Y-%m-%d.%H:%M:%S")
bla2 = datetime.strptime(args.stop, "%Y-%m-%d.%H:%M:%S")

if bla1.year != 1111:
    time_start = bla1
    time_stop  = bla2

## read out the currents from the Keithley logs
xx      = {}
voltage = {}
current = {}
keithleys = OrderedDict([("Keithley1","Silicon"),("Keithley2","Diamond front"),("Keithley3","Diamond back")])
for key in keithleys:
    xx[key]         = []
    voltage[key]    = []
    current[key]    = []
stop = False


keithley_log_dir = str(args.logsKeithley)+"keithleyLog_"+str(time_start.year)+"_0"+str(time_start.month)+"_"+str(time_start.day)+"*"
print keithley_log_dir
for name in glob.glob(keithley_log_dir):
    data = open(name,'r')
    for line in data:
        info = line.split()
        if info[1].startswith("2015"):
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
c = ROOT.TCanvas("c",canvas_name,1000,1000 )
pads = []
c.Divide(1,3)
c.SetFillColor(39)

## draw the graphs
#Keithley1
graphs = []
for key, value in keithleys.items():
    ind = keithleys.items().index((key,value))
    c.cd(ind+1)
#    pad1 = ROOT.TPad("pad1_"+key,"",0,0,1,1)
#    pad2 = ROOT.TPad("pad2_"+key,"",0,0,1,1)
#    pad2.SetFillStyle(4000) # transparent
#    pad1.Draw()
#    pad1.cd()
#    print pad1
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
    g.GetXaxis().SetTimeFormat("%H:%M:%S")
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
    c.cd(ind+1).SetGridx(10)
    g.Draw("AP")
    graphs.append(g)
#    print pad1
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
#    x = array.array('d',xx[key])
#    y = array.array('d',voltage[key])
#    g2 = ROOT.TGraph(len(x),x,y)
#    g2.Draw("P")
#    graphs.append(g2)
#    pads.append(pad1)
#    pads.append(pad2)

c.Update()



