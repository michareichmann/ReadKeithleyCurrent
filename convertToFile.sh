#!/bin/sh

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
start=288
end=288
ff=png

while getopts ":a:b:c:" opt; do
  case $opt in
    a)
      start=$OPTARG
      ;;
    b)
      end=$OPTARG
      ;;
    c)
      ff=$OPTARG
      ;;
  esac
done

echo "start with Run $start and stop with run $end"

end=`expr $end + 1`
while [ $start -lt $end ]
do
   python readKeithleyCurrent.py -r $start -s -f $ff
   start=`expr $start + 1`
done


