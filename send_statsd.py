"""
This script obtains the Hardware readings (CPU, GPU and Ram) from OpenHardwareMonitor.exe and sends to the statsd server.

Remember to run OpenHardwareMonitor.exe.
This script will fail it is not running.

Remember to set Environment Variables:
$SERVER_IP
Stores the IP address of the StatsD Server where the statsd service is open at UDP port 8125
e.g. $SERVER_IP=127.0.0.1

$PARENT_CPU & $PARENT_GPU
Stores the IP address of the StatsD Server where the statsd service is open at UDP port 8125
The double // is necessary to prevent windows from interpreting the single slash as root directory
e.g. $PARENT_CPU=//amdcpu/0
e.g. $PARENT_GPU=//atigpu/0

$COMPUTER_NAME
Stores the parent name for the DB entry to be created in the statsd DB.
e.g. $COMPUTER_NAME=my_desktop
"""
import statsd
import os
from Libraries.OpenHardwareMonitor import get_pc
import json
from datetime import datetime

def main():
    # Print Current Time
    now = datetime.now()
    print(str(now))

    # Get and Check enviroment variables
    SERVER_IP  = os.environ['SERVER_IP' ]
    print("$SERVER_IP={}".format(SERVER_IP))
    PARENT_CPU = os.environ['PARENT_CPU'].replace("//","/")
    print("$PARENT_CPU={}".format(PARENT_CPU))
    PARENT_GPU = os.environ['PARENT_GPU'].replace("//","/")
    print("$PARENT_GPU={}".format(PARENT_GPU))
    COMPUTER_NAME  = os.environ['COMPUTER_NAME' ]

    # Get OpenHardwareMonitor.exe results
    pc = get_pc(PARENT_CPU, PARENT_GPU)
    pc.print_status()

    # Send results using statsd
    statsd_client = statsd.StatsClient(SERVER_IP, 8125)
    pc.send_status(COMPUTER_NAME, statsd_client)

if __name__ == "__main__":
    main()