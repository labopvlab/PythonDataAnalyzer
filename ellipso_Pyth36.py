#! python3

import os
from tkinter import filedialog
import xlsxwriter

"""

"""

def EllipsoSummary():
    ready=0
    j=0
    while j<2:
        try: 
            file_path =filedialog.askopenfilenames(title="Please select the ellipso files")
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
                print("Please select correct ellipso files")
                j+=1
        except:
            print("no file selected")
            j+=1
    if ready:
        summary=[["Summary of ellipsometry results"],
                 ["Batch","SampleID","L1","L2","L5","Eg","eps_inf","A","E_0","C","Khi^2","model"]
                 ]
    
        for i in range(len(file_path)):
            samplename=os.path.split(file_path[i])[1][:-4]
            index=samplename.index("_")
            batchname=samplename[:index]
            measname=samplename[index+1:]
            
            filerawdata = open(file_path[i],"r").readlines()
            
            L1=float(filerawdata[8].split("=")[1].split(" ")[1])
            L2=float(filerawdata[9].split("=")[1].split(" ")[2])
            L5=float(filerawdata[10].split("=")[1].split(" ")[1])
            Eg=float(filerawdata[11].split("=")[1].split(" ")[3])
            eps=float(filerawdata[12].split("=")[1].split(" ")[3])
            A=float(filerawdata[13].split("=")[1].split(" ")[1])
            E0=float(filerawdata[14].split("=")[1].split(" ")[3])
            C=float(filerawdata[15].split("=")[1].split(" ")[3])
            khi=float(filerawdata[4].split("=")[1].split(" ")[1])
            modelfile=filerawdata[27].split(":")[1].split(" ")[1]
            summary.append([batchname,measname,L1,L2,L5,Eg,eps,A,E0,C,khi,modelfile])
        
        
        workbook = xlsxwriter.Workbook(batchname+'_ellipso_summary.xlsx')
        worksheet = workbook.add_worksheet("Summary")
        
        for item in range(len(summary)):
            for item0 in range(len(summary[item])):
                worksheet.write(item,item0,summary[item][item0])
        
        workbook.close()



###############################################################################        
if __name__ == '__main__':
    EllipsoSummary()









