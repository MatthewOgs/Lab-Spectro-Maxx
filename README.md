# Lab-Spectro-Maxx
Monitor Directory on Pi for new files and process data into SQL database
This program is intended to monitor a directory on a Raspberry Pi and when a new file is found it must process the file
The directory monitor program waits for a network folder to be mounted before running.

The python program processes an xml file, from the Spectrometer. The data is manipulated and then stored in a SQL database.

Requirements:

inotify-tools package
