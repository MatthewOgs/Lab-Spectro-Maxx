#!/bin/sh
#########################################################################
# Copyright 2021 Matthew Ogilvie
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#########################################################################


###########################################################################################
#This script is intended to monitor a directory set by MONITORDIR. 
#It also waits for a network file to be mounted before starting
#The monitoring is done using inotify-tools API
#Please install the inotify tools using, 'sudo apt-get install inotify-tools'
#The script will not work without it.
#To run the script at startup add bash '/home/pi/Scripts/monitorDir.sh &' to rc.local
#The '&' allows for the script not to halt the boot process
#This script monitors a directory that rsync's with the mounted directory and
#thus waits for the directory to be mounted first
###########################################################################################

while ! grep -q /mnt/Lab </proc/mounts; do #Wait for network director to be mounted, exit the statement when it is
  sleep 1
done
echo $now - Drive Mounted &>> /home/pi/Scripts/Logs/dirMon.log #Log when drive is mounted, only executes once at boot
MONITORDIR="/home/pi/Results" #Set to desired directory for monitoring
BUFFER="NULL" #Set buffer file to empty
#Monitor for new files that have been saved to the directory only trigger 
#when writing is done. Full file name and path are saved to NEWFILE
inotifywait -m -r -e move,close_write --format '%w%f' "${MONITORDIR}" | while read NEWFILE 
do
if [[ "$BUFFER" == "$NEWFILE" ]]; #Check if buffer NEWFILE is duplicated, bug in inotify-wait sometimes reads same file twice
    then
    	  #Log duplicate file found 
        echo $now - Duplicate Found &>> /home/pi/Scripts/Logs/dirMon.log
    else
    	  #Run python script for file handling and processing.
        python3 /home/pi/Scripts/fileHandle.py "${NEWFILE// /_}" &>> /home/pi/Scripts/Logs/fileHandle.log;
        #Save new buffer file name
        BUFFER=$NEWFILE
        #Log new file found and proccessed
        now=$(date) #Get current date and time - Only used for logging purposes
        echo $now - New File Found and Processed&>> /home/pi/Scripts/Logs/dirMon.log
fi
done
exit

    
