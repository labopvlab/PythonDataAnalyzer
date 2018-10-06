# -*- coding: utf-8 -*-
import os
import os.path
import shutil
from datetime import datetime

sourcefolderpath = r"\\sti1files.epfl.ch\pv-lab\pvlab-commun\LaboPVLab\Labo-IV\IV_backup\2018_06"
destinationfolderpath = r'C:\Users\jwerner\Desktop\New folder\Allivfiles'



#listofpaths=os.listdir(sourcefolderpath)
#print(listofpaths[0])
#
#os.chdir(destinationfolderpath)
#
#shutil.copy(listofpaths[0], "file.iv")



def get_filepaths(directory, destination):
    i=1
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            print(i)
            i+=1
            if filepath.endswith('.iv'):
                filetoread = open(filepath,"r")
                filerawdata = filetoread.readlines()
                for item in range(len(filerawdata)):
                    if "User name:" in filerawdata[item]:
                        operator=filerawdata[item][11:-1].strip()
#                        if operator in ["jwerner", "gdubuis", "walter", "niesen"]:
                        if operator == "jwerner":
                            shutil.copy(filepath, os.path.join(destination, filename))
                        break



#get_filepaths(sourcefolderpath, destinationfolderpath)



def summarizefolder(directory):
    sumlist=[]
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            filetoread = open(filepath,"r")
            filerawdata = filetoread.readlines()
            filetype = 0
            check=0
            check1=0
            for item0 in range(len(filerawdata)):
                if "voltage/current" in filerawdata[item0]:
                    filetype = 1
                    break
                if "IV FRLOOP" in filerawdata[item0]:
                    filetype = 2
                    break
            for item0 in range(len(filerawdata)):
                if "% ANALYSIS OUTPUT" in filerawdata[item0] :
                    check=1
                    break
            for item0 in range(len(filerawdata)):
                if "Voc [V]:" in filerawdata[item0] :
                    check1=1
                    break
            if check==1 and check1==1:
                if filetype ==1 or filetype==2: #J-V files and FRLOOP
                    partdict = {}
                    
                    for item in range(len(filerawdata)):
                        if "Illumination:" in filerawdata[item]:
                            partdict["Illumination"]=filerawdata[item][14:-1]
                            break
                        else:
                            partdict["Illumination"]="Light"
                    if partdict["Illumination"]=="Light":
                        for item in range(len(filerawdata)):
                            if "IV measurement time:" in filerawdata[item]:
                                #partdict["MeasDayTime"]=filerawdata[item][22:-1]
                                partdict["MeasDayTime"]=filerawdata[item][22:-1]
                                break
                        for item in range(len(filerawdata)):
                            if "Voc [V]:" in filerawdata[item]:
                                partdict["Voc"]=float(filerawdata[item][19:-1])*1000
                                break            
                        for item in range(len(filerawdata)):
                            if "Jsc [A/m2]:" in filerawdata[item]:
                                partdict["Jsc"]=float(filerawdata[item][19:-1])*0.1
                                break            
                        for item in range(len(filerawdata)):
                            if "FF [.]:" in filerawdata[item]:
                                partdict["FF"]=float(filerawdata[item][18:-1])*100
                                break            
                        for item in range(len(filerawdata)):
                            if "Efficiency [.]:" in filerawdata[item]:
                                partdict["Eff"]=float(filerawdata[item][19:-1])*100
                                break
#                        print(filename)
#                        print("%.1f, %.1f, %.1f, %.1f"%(partdict["Voc"],partdict["Jsc"],partdict["FF"],partdict["Eff"]))
                        
                        sumlist.append(partdict)
                        
    file = open(os.path.join(directory, "summary.txt"),'w')
            
    for item in sumlist:
        linetowrite=item["MeasDayTime"]+"\t"+str(item["Voc"])+"\t"+str(item["Jsc"])+"\t"+str(item["FF"])+"\t"+str(item["Eff"])+"\n"
        file.writelines("%s" % linetowrite)
    file.close()  
    
    
#summarizefolder(destinationfolderpath)
    
    
    
    
    
def getsamplename(directory):
    samplelist=[]
    batchnamelist=[]
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            filetoread = open(filepath,"r")
            filerawdata = filetoread.readlines()
            filetype = 0
            check=0
            check1=0
            for item0 in range(len(filerawdata)):
                if "voltage/current" in filerawdata[item0]:
                    filetype = 1
                    break
                if "IV FRLOOP" in filerawdata[item0]:
                    filetype = 2
                    break
            for item0 in range(len(filerawdata)):
                if "% ANALYSIS OUTPUT" in filerawdata[item0] :
                    check=1
                    break
            for item0 in range(len(filerawdata)):
                if "Voc [V]:" in filerawdata[item0] :
                    check1=1
                    break
            if check==1 and check1==1:
                if filetype ==1 or filetype==2: #J-V files and FRLOOP
                    partdict = {}
                    
                    for item in range(len(filerawdata)):
                        if "Illumination:" in filerawdata[item]:
                            partdict["Illumination"]=filerawdata[item][14:-1]
                            break
                        else:
                            partdict["Illumination"]="Light"
                    if partdict["Illumination"]=="Light":
                        for item in range(len(filerawdata)):
                            if "Deposition ID:" in filerawdata[item]:
                                partdict["DepID"]=filerawdata[item][15:-1]
                                partdict["DepID"]=partdict["DepID"].replace("-","_")
                                partdict["DepID"]=partdict["DepID"].strip()
                                partdict["DepID"]=partdict["DepID"].replace("\t","")
                                partdict["batchname"]=partdict["DepID"].split("_")[0]
                                break
                        if partdict["batchname"][0]=="P":
                            batchnamelist.append(partdict["batchname"])
                            samplelist.append(partdict["DepID"])
    return [samplelist,batchnamelist]
                        
            
    
    
#[samplelist,batchnamelist]=getsamplename(destinationfolderpath)
#    
#print(len(list(set(samplelist))))    
#print(len(list(set(batchnamelist))))    
#print(list(set(batchnamelist)))
#    
    
    
def getnumberofcells(directory):
    samplelist=[]
    batchnamelist=[]
    celllist=[]
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            filetoread = open(filepath,"r")
            filerawdata = filetoread.readlines()
            filetype = 0
            check=0
            check1=0
            for item0 in range(len(filerawdata)):
                if "voltage/current" in filerawdata[item0]:
                    filetype = 1
                    break
                if "IV FRLOOP" in filerawdata[item0]:
                    filetype = 2
                    break
            for item0 in range(len(filerawdata)):
                if "% ANALYSIS OUTPUT" in filerawdata[item0] :
                    check=1
                    break
            for item0 in range(len(filerawdata)):
                if "Voc [V]:" in filerawdata[item0] :
                    check1=1
                    break
            if check==1 and check1==1:
                if filetype ==1 or filetype==2: #J-V files and FRLOOP
                    partdict = {}
                    
                    for item in range(len(filerawdata)):
                        if "Illumination:" in filerawdata[item]:
                            partdict["Illumination"]=filerawdata[item][14:-1]
                            break
                        else:
                            partdict["Illumination"]="Light"
                    if partdict["Illumination"]=="Light":
                        for item in range(len(filerawdata)):
                            if "Cell number:" in filerawdata[item]:
                                partdict["CellNumber"]=float(filerawdata[item][23:-1])
                                if partdict["CellNumber"]==1:
                                    partdict["Cellletter"]='A'
                                elif partdict["CellNumber"]==2:
                                    partdict["Cellletter"]='B'
                                elif partdict["CellNumber"]==3:
                                    partdict["Cellletter"]='C'
                                else:
                                    partdict["Cellletter"]='Single'
                                break
                        for item in range(len(filerawdata)):
                            if "Deposition ID:" in filerawdata[item]:
                                partdict["DepID"]=filerawdata[item][15:-1]
                                partdict["DepID"]=partdict["DepID"].replace("-","_")
                                partdict["DepID"]=partdict["DepID"].strip()
                                partdict["DepID"]=partdict["DepID"].replace("\t","")
                                partdict["cell"]=partdict["DepID"]+"_"+partdict["Cellletter"]
                                partdict["batchname"]=partdict["DepID"].split("_")[0]
                                break
                        if partdict["batchname"][0]=="P":
                            batchnamelist.append(partdict["batchname"])
                            samplelist.append(partdict["DepID"])
                            celllist.append(partdict["cell"])
                            print(partdict["cell"])
    return [samplelist,batchnamelist,celllist]

[samplelist,batchnamelist,celllist]=getnumberofcells(destinationfolderpath)

print(len(list(set(samplelist))))    
print(len(list(set(batchnamelist))))    
print(len(list(set(celllist))))   


def gettotalMpptime(directory):
    mpptime=0
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            filetoread = open(filepath,"r")
            filerawdata = filetoread.readlines()
            filetype = 0
            filetype2 = 0

            for item0 in range(len(filerawdata)):
                if "Mpp tracker" in filerawdata[item0]:
                    filetype = 1
                    break
            for item0 in range(len(filerawdata)):
                if "% MEASURED Pmpptracker" in filerawdata[item0]:
                    filetype2 = 1
                    break
                
            if filetype ==1 and filetype2==1:
#                for item in range(len(filerawdata)):
#                    if "MEASURED Pmpptracker" in filerawdata[item]:
#                        pos=item+2
#                        break
                mpptime+=float(filerawdata[len(filerawdata)-1].split("\t")[2])
#                mpppartdat = []#[voltage,current,time,power,vstep]
#                for item in range(pos,len(filerawdata),1):
#                    mpppartdat.append(float(filerawdata[item].split("\t")[2]))
                
    return mpptime
    
#mppdirect=  r"C:\Users\jwerner\switchdrive\python\IVAnalyzer\data" 
#    
#    
#print(gettotalMpptime(destinationfolderpath))
#    
#    
    
    
    
    
    
    
    
    
    
    
    