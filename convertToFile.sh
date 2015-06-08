#!/bin/sh

if [ ! -d $PWD/runs ]; then
	mkdir -p $PWD/runs
fi

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
start=288
end=288
ff=png

# parsing
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

# change the ending of the file to look for if you want to convert all
echo $ff
if [ "$ff" = "all" ]; then
	runff=eps
	start=1
	end=500
else
	runff=$ff
fi

#loop over the python script
end=`expr $end + 1`
while [ $start -lt $end ]
do
   	if [ $start -lt 10 ]; then
      	run=run00$start.$runff
   	elif [ $start -lt 100 ]; then
      	run=run0$start.$runff
	else
		run=run$start.$runff
   	fi
	echo "checking if $run exists"
   	if [ ! -f $PWD/runs/$run ]; then
      	python readKeithleyCurrent.py -r $start -s -f $ff
	else
		echo "$run already exists"
	fi
	start=`expr $start + 1`
done


