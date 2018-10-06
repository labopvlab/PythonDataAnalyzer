#! python3

import os
from tkinter import filedialog
import xlsxwriter
from datetime import datetime

"""

"""


def HallSummary():
    ready=0
    j=0
    while j<2:
        try: 
            file_path =filedialog.askopenfilenames(title="Please select the Hall files")
            if file_path!='':
                ready=1
                directory = filedialog.askdirectory(title="Where saving?")        
                if not os.path.exists(directory):
                    os.makedirs(directory)
                    os.chdir(directory)
                else :
                    os.chdir(directory)
                break
            else:
                print("Please select correct .hall files")
                j+=1
        except:
            print("no file selected")
            j+=1
    if ready:
        summary=[["FileName","Date","User","I","Temp","Bulk Conc.", "Sheet Conc.",
          "Resistivity","Conductivity","Magneto res.","Mobility", 
          "Avg Hall coeff"
          ]]

        for i in range(len(file_path)):
            Filename=os.path.split(file_path[i])[1][:-5]
            
            filerawdata = open(file_path[i],"r").readlines()
            
            Date=filerawdata[1].split("\t")[0]
            User=filerawdata[1].split("\t")[1]
            
            I=0
            Temp=0
            BulkConc=0
            SheetConc=0
            Resistivity=0
            Conductivity=0
            MagnetoRes=0
            Mobility=0
            AvgHall=0
            
            for k in range(5,len(filerawdata)):
                I+=float(filerawdata[k].split("\t")[1])
                Temp+=float(filerawdata[k].split("\t")[2])
                BulkConc+=float(filerawdata[k].split("\t")[3])
                SheetConc+=float(filerawdata[k].split("\t")[4])
                Resistivity+=float(filerawdata[k].split("\t")[5])
                Conductivity+=float(filerawdata[k].split("\t")[6])
                MagnetoRes+=float(filerawdata[k].split("\t")[7])
                Mobility+=float(filerawdata[k].split("\t")[8])
                AvgHall+=float(filerawdata[k].split("\t")[9])
            summary.append([Filename,Date,User,I/3,Temp/3,BulkConc/3,SheetConc/3,Resistivity/3,Conductivity/3, MagnetoRes/3,Mobility/3,AvgHall/3])   
            
            workbook = xlsxwriter.Workbook('HallEffect_summary_'+datetime.now().strftime("%y%m%d")+'.xlsx')        
            worksheet = workbook.add_worksheet("Summary")
            for item in range(len(summary)):
                for item0 in range(len(summary[item])):
                    worksheet.write(item,item0,summary[item][item0])
            workbook.close()



###############################################################################        
if __name__ == '__main__':
    HallSummary()

