# ====================================
# IMPORTS
# ====================================
from time import time, localtime, strftime


# ====================================
# HELPER FUNCTIONS
# ====================================
# convert datetime to number in seconds
def convert_time(date_time):
    seconds = (date_time.day - 1) * 24 * 3600 + date_time.hour * 3600 + date_time.minute * 60 + date_time.second
    if date_time.month == 6:
        seconds += 31 * 3600 * 24
    return seconds


# converts the entered run number
def convert_run(number):
    run_number = ""
    number = int(number)
    if number >= 1000:
        print "The entered run number has to be lesser then 1000"
        exit()
    elif number >= 100:
        run_number = "150800" + str(number)
    elif number >= 10:
        run_number = "1508000" + str(number)
    else:
        run_number = "15080000" + str(number)
    return run_number


def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


# prints elapsed time
def elapsed_time(start):
    string = str('{0:0.2f}'.format(time() - start)) + ' seconds'
    return string


def get_log_dir(directory):
    k6517 = ['k6517', '6517', '6517b', 'k6517b']
    k2657 = ['k2657', '2657', '2657a', 'k2657b', 'dia2', 'k2567', '2567']
    k237 = ['k237', '237', 'dia1']
    k1 = ['k1', 'keithley1', 'silicon', 'sil']
    if directory.lower() in k6517:
        return '/home/testbeam/sdvlp/keithleyClient/PSI_2015_08/Keithley6517'
    elif directory.lower() in k2657:
        return '/home/testbeam/sdvlp/keithleyClient/PSI_2015_08/Keithley2657A'
    elif directory.lower() in k1:
        return '/home/testbeam/sdvlp/keithleyClient/PSI_2015_08/Keithley1'
    elif directory.lower() in k237:
        return '/home/testbeam/sdvlp/keithleyClient/PSI_2015_08/Keithley237'
    elif len(directory) < 6:
        print "Could not find any alias for entered log file directory. exiting..."
        exit()
    return directory

def convert_date(atime):
    try:
        int(atime)
    except ValueError:
        print "ERRRRRROOOOOOOOOOOOR"
        if len(atime) > 6:
            return atime
        else:
            t = localtime()
            t = strftime('%Y-%m-%d.',t)
            t = t + atime
            print t
            return t
    return atime

