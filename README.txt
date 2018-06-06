Checking HP raid status (also status of physical drives, logical drives, raid cache, physical drives temperature).
Tested on Ubuntu 16.04 and on Debian 8.

This script producing range of files where you can find current state of drives and raid controller.
You can change paths in the main script (see top of .py file).

Also this script has been maded for zabbix monitoring system and it utilize hpacucli programm 
(please see on HP site about it).

At least you need to have installed on server python3 and hpacucli programm.

With best regards, Constantine.
