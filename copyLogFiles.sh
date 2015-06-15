#!/bin/bash

if [ ! -d $PWD/logs ]; then
    mkdir -p $PWD/logs
fi
rsync -aP daq:~/sdvlp/keithleyClient/keithleyLog*.txt $PWD/logs

if [ ! -d $PWD/eudaq_logs ]; then
    mkdir -p $PWD/eudaq_logs
fi
rsync -aP rapidshare:/mnt/raid/psi_2015_05/logs_eudaq/*.log $PWD/eudaq_logs
