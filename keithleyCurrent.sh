#!/bin/bash

if [ ! -d $PWD/logs ]; then
    mkdir -p $PWD/logs
fi
scp daq:~/sdvlp/keithleyClient/keithleyLog_2015_05_*.txt $PWD/logs
