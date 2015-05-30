#!/usr/bin/python

import argparse
import ROOT
import numpy as n
import array
from datetime import datetime, date, time
from collections import OrderedDict

parser = argparse.ArgumentParser()
parser.add_argument("-l1", nargs='?', default="logs/keithleyLog_2015_05_29_06_44.txt",help="enter the filepath of the Keithley-log")
parser.add_argument("-l2", nargs='?', default="eudaq_logs/2015-05-29.log",help="enter the filepath of the EUDAQ-log")
parser.add_argument("-r", "--run", nargs='?', default="0",help="enter the runnumber without date information")
args = parser.parse_args()

print "Looking for Run:", args.run

def convertTime(string):
    string = string.day*24*3600+string.hour*3600 + string.minute*60 + string.second
    return string

## get start and stop of the run from eudaq logfile
logfile = open(args.l2)
if args.run > 99:
    runname = "150500"+str(args.run)
elif args.run >9:
    runname = "1505000"+str(args.run)
start_tag = "Starting Run "+runname
stop_tag  = "Stopping Run "+runname
time_start = ""
time_stop = ""
for line in logfile:
    data = line.split("\t")
    if len(data)>1:
        if data[1].startswith(start_tag):
            time_start = data[2]
            print "start:", data[2]
        if data[1].startswith(stop_tag):
            time_stop = data[2]
            print "stop: ", data[2]
logfile.close()

#example string: '2015-05-29 14:14:40.923'
time_start = datetime.strptime(time_start, "%Y-%m-%d %H:%M:%S.%f")
time_stop  = datetime.strptime(time_stop, "%Y-%m-%d %H:%M:%S.%f")
run_start  = convertTime(time_start)
run_stop   = convertTime(time_stop)
date = time_start.strftime("%Y-%m-%d")#time_start.

## read out the currents from the Keithley logs
xx = {}
yy = {}
keithleys = OrderedDict([("Keithley1","Silicon"),("Keithley2","Diamond front"),("Keithley3","Diamond back")])
for key in keithleys:
    xx[key] = []
    yy[key] = []
data = open(args.l1,'r')
for line in data:
    info = line.split()
    time = convertTime(datetime.strptime(date+" "+info[2], "%Y-%m-%d %H:%M:%S"))
    for key in keithleys:
        if len(info) > 3 and info[0].startswith(key):
            if time > run_start and time < run_stop:
                yy[key].append(float(info[4])*1e9)
                xx[key].append(time)
data.close()


## create the canvas
c = ROOT.TCanvas("c","Keithley Currents",1000,1000 )
c.Divide(1,3)
c.SetFillColor(39)


## draw the graphs
#Keithley1
graphs = []
for key, value in keithleys.items():
    ind = keithleys.items().index((key,value))
    c.cd(ind+1)
    x = array.array('d',xx[key])
    y = array.array('d',yy[key])
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

c.Update()



