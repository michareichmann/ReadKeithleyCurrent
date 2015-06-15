#!/usr/bin/python

import json
from functions import RunInfo
import functions
from collections import OrderedDict

filename = "runs_PSI_May_2015.json"



def calc_flux(pixels, rate):
    area = ((80 * 52 - pixels) * 15e-5)
    flux = rate / area / 1e3
    if rate == -1:
        flux = -1
    else:
        flux = int(round(flux, 0))
    return flux

f = open(filename, 'r')
data = json.load(f, object_pairs_hook=OrderedDict)
f.close()

x = RunInfo(filename)
start = x.first_run()
stop = x.last_run()
print start, stop
for run in range(start, stop):
    print run
    if run <= stop:
        x = RunInfo(filename, run)
    rate = x.rate
    pixel = x.pixels
    if rate != -1 and pixel != 0:
        data[functions.convert_run(run)]["measured flux"] = calc_flux(pixel, rate)

d = open("test.json", 'w')
d.write(json.dumps(data, indent=4))
d.close()
