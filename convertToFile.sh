#!/bin/sh

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
start=288
end=288

while getopts ":a:b:" opt; do
  case $opt in
    a)
      start=$OPTARG
      ;;
    b)
      end=$OPTARG
      ;;
  esac
done

echo "start with Run $start and stop with run $end"

while [ $start -lt $end ]
do
   python readKeithleyCurrent.py -r $start
   start=`expr $start + 1`
done


