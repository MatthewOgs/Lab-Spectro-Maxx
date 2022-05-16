import sys
import openpyxl as xl;
from copy import copy
from openpyxl.styles import colors
from openpyxl.styles import Font, Color
from openpyxl.utils import rows_from_range
import mysql.connector
#conn = pytds.connect('Server=MATTHEW-DELL\SQLEXPRESS;Database=LabResultsTest;Trusted_Connection=yes;')
mydb = mysql.connector.connect(
        host="localhost",
        user="pi",
        password="Frog3146",
        )
con = mydb.cursor()


#cursor = conn.cursor()
cols = ["ZN", "PB", "SN" ,"P" ,"MN" ,"FE" ,"NI" ,"SI" ,"MG" ,"CR" ,"ASN" ,"SB" ,"CD" ,"BI" ,"CO" ,"AL" ,"S" ,"BE" ,"B" ,"SE" ,"CU" ,"IMP"]
delimeter = ", "
alloyCol = ""
fileDirResult = sys.argv[1].replace("_", " ")
fileDirDisplay = "/home/pi/Display/Data.xlsx"
#print(fileDirResult.find('~$'))
if (fileDirResult.find('.xlsx') != -1 and fileDirResult.find('~$') == -1):
    #print(fileDirResult)
    wbResult = xl.load_workbook(fileDirResult)
    shResult = wbResult['Sheet1']
    testTypeVal = shResult["A4"].value
    gradeTypeVal = shResult["B4"].value
    measTime = shResult["C2"].value
    recalTime = shResult["D2"].value
    Operator = shResult["G2"].value
    my_char=ord('b') # convert char to ascii
    start = 0
    newConc = [] * 20
    #vals = [] * 7
    while my_char<= ord('w'):
        #print(start)
        newCell1 = shResult[chr(my_char)+"10"]
        newCell2 = shResult[chr(my_char)+"11"]
        newCell3 = shResult[chr(my_char)+"12"]
        #print(newCell1.value)
        newConc.append(str(newCell1.value) + ";" + str(newCell1.font.color.rgb) + ";" + str(newCell2.value) + ";" + str(newCell2.font.color.rgb) + ";" + str(newCell3.value) + ";" + str(newCell3.font.color.rgb))
        #print(newConc[start])
        my_char+=1 # iterate over abc
        start+=1
    
    sql = "INSERT INTO LabResults.Lab_Res (Sample_Name, Grade_Name, Meas_Time, Recalc_Time, Operator, ZN, PB, SN, P, MN, FE, NI, SI, MG, CR, ASN, SB, CD, BI, CO, AL, S, BE, B, SE, CU, IMP) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    vals = (str(testTypeVal), str(gradeTypeVal), str(measTime), str(recalTime), str(Operator), newConc[0], newConc[1], newConc[2], newConc[3] , newConc[4], newConc[5], newConc[6], newConc[7], newConc[8], newConc[9], newConc[10], newConc[11], newConc[12], newConc[13], newConc[14], newConc[15], newConc[16], newConc[17], newConc[18], newConc[19], newConc[20], newConc[21])
    con.execute(sql, vals)
    mydb.commit()
    print("Committed to DB")
else:
    print("Tmp file found. Disregarding file...")