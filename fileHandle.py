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

#########################################################################
# This program is designed to take an xml file from a Spectro Maxx result
# and proccess it accordingly for use on a display. The formatting is as follows
# Sample Name    Sample Time     Operator Name
# Grade Name     Recalc Time     
#           | CU | ZN | PB | SN | MN | FE | NI | AL | SB | AS | IMP|    
# Min Warn  | %  | %  | %  | %  | %  | %  | %  | %  | %  | %  | %  |   
# Rep       | %  | %  | %  | %  | %  | %  | %  | %  | %  | %  | %  |   
# Max Warn  | %  | %  | %  | %  | %  | %  | %  | %  | %  | %  | %  |  
#
# The program pulls the neccesary data from the Measurement Statistics 
# section of the xml. The conc% data for each element, including
# colour formatting is saved in a string with a ';' as a seperator in the
# for min%;blue;rep%;warningstate;max%;blue 
# e.g. 62.00;blue;64.54;InRange;68.45;blue. This string is stored in the
# column for the coresponding element, in the database. All data is saved
# in a database using auto increment as a primary key.
#########################################################################

from xml.dom import minidom
import sys
import os
import mysql.connector
import datetime
__author__ = "Matthew Ogilvie"
__copyright__ = "Copyright 2021, Copalcor Lab Software"
__credits__ = ["Matthew Ogilvie", "Andrew Heyes", "Bernard Bradford", "Benson Migwi", "Bongani Mthembu"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Matthew Ogilvie"
__email__ = "matthewogs@gmail.com"
__status__ = "Production"
#Create database connection. MYSQL must be installed and the table created before running program
mydb = mysql.connector.connect(
        host="localhost",#SQL host use IP if not on raspberrypi
        user="pi",#Admin user of MSQL database
        password="Frog3146",#Admin password for MYSQL database
        )
con = mydb.cursor()#Creat connection using above info

fileDirResult = sys.argv[1] #Full file name passed from the dirMon.sh script
if os.path.isfile(fileDirResult): #Check if the file exists or if the result was a temporary file
    mydoc = minidom.parse(fileDirResult) #Parse the XML file for manipulation
    sampIDs = mydoc.getElementsByTagName('IDValue') #Get the elements by ID value for the name and the grade
    newConc = [] * 20 #Create array for each voncentration for each element
    sampName = sampIDs[0].childNodes[0].data #Write sample name from XML to sampName
    if sampName.find("RC") != -1: #Check if sample name has 'RC' in it to test for Rodcaster. Change this to check for other tests
        gradeName = sampIDs[1].childNodes[0].data #Write grade name from XML to gradeName
        recalTimeList = mydoc.getElementsByTagName('SampleResult') #Create list for Sample Result to pull time and operator name
        recalTime = recalTimeList[0].attributes['RecalculationDateTime'].value #Pull recalculation time from Sample Result attributes
        Operator = recalTimeList[0].attributes['OperatorName'].value #Pull roperator name from Sample Result attributes
        measTimeList = mydoc.getElementsByTagName('MeasurementReplicate') #Get list of measurement replicates for Last sample time
        measTime = measTimeList[0].attributes['MeasureDateTime'].value #Pull Last sample time from first measurment replicate
        messtats = mydoc.getElementsByTagName('MeasurementStatistics') #Get list of measurement statistics, this is where the results and min max values are stored, we ignore the values for each spark as they are averaged here
        elements = messtats[0].getElementsByTagName('Element') #Populate list with the elements in the statistics, these conttain the ave, min and max
        rangeof = (len(elements)) #Get length of the elements list
        for elementno in range(rangeof): #Run loop through results using list length
            result = elements[elementno].getElementsByTagName('ElementResult') #Get list of values within elemet
            limits = result[1].getElementsByTagName('ResultValueLimit') #Get the limits in the list of results
            element = elements[elementno].attributes['ElementName'].value #Get element name from the attributes
            warnstate = result[1].attributes['WarningStatus'].value #Get the warning state from the attribute in the 2nd result value
            actresult = float(result[1].childNodes[1].childNodes[0].data) #Get the result from the 2nd result value and make it a float value
            if actresult < 0.001: #Check if the result requires more than 2 decimal places
                actresultr = round(actresult,4) #Round to 4 decimal places for ver small values
            else:
                actresultr = round(actresult,2) #Round to 2 decimal places for all other values
            limitsCnt = len(limits) #Get the length of the limit list
            gotLower = 0 #Set lower to 0
            gotUpper = 0 #Set upper to 0
            if result[1].attributes['WarningStatus'].value != 'NotUsed': #If result limits not used the skip check for upper and lower
                for i in range(limitsCnt): #Run through limits list to get upper and/or lower limits, this is the avoid using the cal min and max as limits, these are not used in corrections
                    if limits[i].attributes['Type'].value == 'LowerWarningLimit': #If the attribute LowerWarningLimit exists then use the value
                        lower = float(limits[i].childNodes[0].data) #lower value is equal to the current chile node in limits list and is converted to float
                        if lower < 0.001: #Check if the result requires more than 2 decimal places
                            lowerr = round(lower,4) #Round to 4 decimal places for ver small values
                        else:
                            lowerr = round(lower,2) #Round to 2 decimal places for all other values
                        gotLower = 1 #Set when lower now has a value
                    if limits[i].attributes['Type'].value == 'UpperWarningLimit': #If the attribute UpperWarningLimit exists then use the value
                        upper = float(limits[i].childNodes[0].data) #upper value is equal to the current chile node in limits list and is converted to float
                        if upper < 0.001: #Check if the result requires more than 2 decimal places
                            upperr = round(upper,4) #Round to 4 decimal places for ver small values
                        else:
                            upperr = round(upper,2) #Round to 2 decimal places for all other values
                        gotUpper = 1 #Set when upper now has a value
            #Put '--' into lower or upper if the limit was not available
            if gotLower == 0: 
                lowerr = '--'
            if gotUpper == 0:
                upperr = '--'
            newConc.append(str(lowerr) + ';Blue;' + str(actresultr) + ';' + warnstate + ';' + str(upperr) + ';Blue') #Append all values into one string for current element being read, this is to add a string array to each column in the results sql table. Note: Values are seperated by a ";"
        #SQL statement to save choose what columns to use when saving
        sql = "INSERT INTO LabResults.Lab_Res (Sample_Name, Grade_Name, Meas_Time, Recalc_Time, Operator, ZN, PB, SN, P, MN, FE, NI, SI, MG, CR, ASN, SB, CD, BI, CO, AL, S, BE, B, SE, CU, IMP) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        #Values to be placed in columns, from variables above NOTE:newConc[x] is the element string from the for loop above
        vals = (str(sampName), str(gradeName), str(measTime), str(recalTime), str(Operator), newConc[0], newConc[1], newConc[2], newConc[3] , newConc[4], newConc[5], newConc[6], newConc[7], newConc[8], newConc[9], newConc[10], newConc[11], newConc[12], newConc[13], newConc[14], newConc[15], newConc[16], newConc[17], newConc[18], newConc[19], newConc[20], newConc[21])
        con.execute(sql, vals) #Execute the statement to the SQL connection created above
        mydb.commit() #Commit to the database
        time = datetime.datetime.now() #Get date and time for the log entry
        print(str(time) + " - Committed to DB") #Log entry save to /home/pi/Scripts/Logs/fileHandle.log NOTE: Log is set in the directory monitor bash script, location: /home/pi/Scripts/monitorDir.sh
    else:
        time = datetime.datetime.now() #Get date and time for the log entry
        print(str(time) + " - Not Rodcaster Test") #Log entry save to /home/pi/Scripts/Logs/fileHandle.log NOTE: Log is set in the directory monitor bash script, location: /home/pi/Scripts/monitorDir.sh
else:
    time = datetime.datetime.now()
    print(str(time) + " - Temporary File Found, no changes made")
