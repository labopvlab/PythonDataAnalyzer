#! python3

import os

#import sys
#sys.setrecursionlimit(1500) #to avoid error on some computer: RuntimeError: maximum recursion depth exceeded in cmp
#import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import tkinter as tk
from tkinter import *
#import tkMessageBox as messagebox
#from ttk import *
from tkinter.ttk import Treeview
from tkinter import Button, Label, Frame, Entry, Checkbutton, IntVar, Toplevel, Scrollbar, Canvas, OptionMenu, StringVar

from tkinter import filedialog
from pathlib import Path
import numpy as np
import copy
import xlsxwriter
import xlrd
from scipy.interpolate import interp1d
from scipy import integrate
from operator import itemgetter
from itertools import groupby, chain
#import PIL
from PIL import Image as ImageTk
from matplotlib.ticker import MaxNLocator
#from matplotlib.cm import rainbow
from tkinter import font as tkFont
from matplotlib.transforms import Bbox
#import dill 
import pickle
import six
#from matplotlib import rc
from tkcolorpicker import askcolor 
from functools import partial


LARGE_FONT= ("Verdana", 12)
DATA=[]
testdata=[]

def center(win):
    """
    centers a tkinter window
    :param win: the root or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()
    
###############################################################################             
    

class DarkToLight(Toplevel):

    def __init__(self, *args, **kwargs):
        
        Toplevel.__init__(self, *args, **kwargs)
        Toplevel.wm_title(self, "DarkToLight")
        Toplevel.config(self,background="white")
        self.wm_geometry("713x277")
        self.wm_resizable(False,False)
        center(self)
        self.initUI()

    def initUI(self):
        
        self.canvas0 = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.superframe=Frame(self.canvas0,background="#ffffff")
        self.canvas0.pack(side="left", fill="both", expand=True)
        
        label = tk.Label(self.canvas0, text="Change low illumination files to Light", font=LARGE_FONT, bg="black",fg="white")
        label.pack(fill=tk.X,expand=0)

        self.frame0 = Frame(self.canvas0,bg='grey')
        self.frame0.pack(fill=tk.X, expand=0)
        
        self.TableBuilder(self.frame0)
        
    class TableBuilder(Frame):
        def __init__(self, parent):
            Frame.__init__(self, parent)
            self.parent=parent
            self.initialize_user_interface()
    
        def initialize_user_interface(self):
            global DATA
            global testdata
            testdata=[]
            self.parent.config(background="white")
                      
            for item in range(len(DATA)):
                testdata.append([DATA[item]["Illumination"],DATA[item]["SampleName"],float('%.2f' % float(DATA[item]["CellSurface"])),DATA[item]["ScanDirection"],float('%.2f' % float(DATA[item]["Jsc"])),float('%.2f' % float(DATA[item]["Voc"])),float('%.2f' % float(DATA[item]["FF"])),float('%.2f' % float(DATA[item]["Eff"])),float('%.2f' % float(DATA[item]["Roc"])),float('%.2f' % float(DATA[item]["Rsc"])),float('%.2f' % float(DATA[item]["Vmpp"])),float('%.2f' % float(DATA[item]["Jmpp"]))])
                
            self.tableheaders=('Illumination','Sample','Area','Scan direct.','Jsc','Voc','FF','Eff.','Roc','Rsc','Vmpp','Jmpp')
                        
            # Set the treeview
            self.tree = Treeview( self.parent, columns=self.tableheaders, show="headings")
            
            for col in self.tableheaders:
                self.tree.heading(col, text=col.title(), command=lambda c=col: self.sortby(self.tree, c, 0))
                self.tree.column(col, width=int(round(1.5*tkFont.Font().measure(col.title()))), anchor='n')   
            
            self.import_button = Button(self.parent, text = "Import Data", command = self.importdata)
            self.import_button.grid(row=0, column=4, columnspan=1,rowspan=1)
            
            self.buttondarktolight = Button(self.parent, text="Change dark to light",command = self.changetolight,fg='black')
            self.buttondarktolight.grid(row=0, column=5, columnspan=1,rowspan=1)
            
            vsb = Scrollbar(orient="vertical", command=self.tree.yview)
            self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=())
            self.tree.grid(row=1,column=0, columnspan=15,rowspan=10, sticky='nsew', in_=self.parent)
            self.treeview = self.tree
            
            self.insert_data(testdata)

        def insert_data(self, testdata):
            for item in testdata:
                self.treeview.insert('', 'end', values=item)

        def sortby(self, tree, col, descending):
            data = [(tree.set(child, col), child) for child in tree.get_children('')]
            try:
                data.sort(key=lambda t: float(t[0]), reverse=descending)
            except ValueError:
                data.sort(reverse=descending)
            for ix, item in enumerate(data):
                tree.move(item[1], '', ix)
            # switch the heading so it will sort in the opposite direction
            tree.heading(col,text=col.capitalize(), command=lambda _col_=col: self.sortby(tree, _col_, int(not descending)))
        
        def changetolight(self):
            global DATA 
            
            #check which sample is selected in the table
            #correct the illumination status in data
            
            
            for j in range(len(self.treeview.selection())):
                selected_item = self.treeview.selection()[j] ## get selected item
                for i in range(len(DATA)):
                    if DATA[i]["SampleName"]==self.treeview.item(selected_item)["values"][1]:
                        DATA[i]["Illumination"]="Light"
                        
                        #export all files in .iv format as the rawdata files, in same folder as the original files with _corr extension
                        os.chdir(self.directory)
                        filetoread = open(DATA[i]["filename"]+'.iv',"r")
                        filerawdata = filetoread.readlines()
                        
                        #os.rename(DATA[i]["filename"]+'.iv',DATA[i]["filename"]+'_old.iv')
                        
                        for item in range(len(filerawdata)):
                            if "Illumination:" in filerawdata[item]:
                                #partdict["Illumination"]=filerawdata[item][14:-1]
                                filerawdata[item]="Illumination:\tLight"
                                break
                        
                        DATAforexport=filerawdata
                        file = open(DATA[i]["filename"]+'_new.iv','w')
                        file.writelines("%s" % item for item in DATAforexport)
                        file.close()  
                        
                        
                        
            self.updateTable()
            
        def updateTable(self):
            self.initialize_user_interface()
            #print("updatingtable")
        
        def importdata(self):
            global DATA 
                           
            finished=0
            j=0
            while j<2:
                file_pathnew=[]
                file_path =filedialog.askopenfilenames(title="Please select the IV files")
                if file_path!='':
                    filetypes=[os.path.splitext(item)[1] for item in file_path]
                    if len(list(set(filetypes)))==1:
                        self.directory = str(Path(file_path[0]).parent)
                        print(self.directory)
                        os.chdir(self.directory)
                        #directory = str(Path(file_path[0]).parent.parent)+'\\correctedIV'
                        #if not os.path.exists(directory):
                        #    os.makedirs(directory)
                        #    os.chdir(directory)
                        #else :
                        #    os.chdir(directory)
                        filetype=list(set(filetypes))[0]
                        if filetype==".iv":
                            file_pathnew=file_path
                            print("these are rawdata files")
                            self.getdatalistsfromIVTFfiles(file_pathnew)
                            finished=1
                            break
                        else:
                            print("not .iv files... try again")
                            j+=1
                    else:
                        print("Multiple types of files... please choose one!")
                        j+=1
                else:
                    print("Please select IV files")
                    j+=1
            
            if finished:
                print("getdata done")
                print(len(DATA))
                
                self.updateTable()
        
        def getdatalistsfromIVTFfiles(self, file_path):
            global DATA
            global DATAdark
            
            for i in range(len(file_path)):
                filename=os.path.basename(file_path[i])[:-3]
                print(filename)
                filetoread = open(file_path[i],"r")
                filerawdata = filetoread.readlines()
                #print(i)
                filetype = 0
                for item0 in range(len(filerawdata)):
                    if "voltage/current" in filerawdata[item0]:
                        filetype = 1
                        break
                    if "IV FRLOOP" in filerawdata[item0]:
                        filetype =2
                        break
                    elif "Mpp tracker" in filerawdata[item0]:
                        filetype = 3
                        break
                    elif "Fixed voltage" in filerawdata[item0]:
                        filetype = 4
                        break
                        
                if filetype ==1 or filetype==2: #J-V files and FRLOOP
                    partdict = {}
                    partdict["filename"]=filename
                    partdict["MeasComment"]="-"
                    for item in range(len(filerawdata)):
                        if "Measurement comment:" in filerawdata[item]:
                            partdict["MeasComment"]=filerawdata[item][21:-1]
                            break
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
                            if filerawdata[item-1][19:-1]=='':
                                partdict["SampleName"]=filerawdata[item][15:-1]+"_"+partdict["Cellletter"]
                            else:
                                partdict["SampleName"]=filerawdata[item][15:-1]+"_"+filerawdata[item-1][19:-1]+"_"+partdict["Cellletter"]
                            partdict["DepID"]=filerawdata[item][15:-1]
                            partdict["DepID"]=partdict["DepID"].replace("-","_")
                            partdict["SampleName"]=partdict["SampleName"].replace("-","_")
                            break
                    for item in range(len(filerawdata)):
                        if "IV measurement time:" in filerawdata[item]:
                            partdict["MeasDayTime"]=filerawdata[item][22:-1]
                            break
                    for item in range(len(filerawdata)):
                        if "Cell size [m2]:" in filerawdata[item]:
                            partdict["CellSurface"]=float(filerawdata[item][17:-1])
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
                    for item in range(len(filerawdata)):
                        if "Pmpp [W/m2]:" in filerawdata[item]:
                            partdict["Pmpp"]=float(filerawdata[item][19:-1])
                            break                
                    for item in range(len(filerawdata)):
                        if "Vmpp [V]:" in filerawdata[item]:
                            partdict["Vmpp"]=float(filerawdata[item][10:-1])*1000
                            break                
                    for item in range(len(filerawdata)):
                        if "Jmpp [A]:" in filerawdata[item]:
                            partdict["Jmpp"]=float(filerawdata[item][10:-1])*0.1
                            break   
                    for item in range(len(filerawdata)):
                        if "Roc [Ohm.m2]:" in filerawdata[item]:
                            partdict["Roc"]=float(filerawdata[item][15:-1])*10000
                            break
                    for item in range(len(filerawdata)):
                        if "Rsc [Ohm.m2]:" in filerawdata[item]:
                            partdict["Rsc"]=float(filerawdata[item][15:-1])*10000
                            break
                    partdict["VocFF"]=float(partdict["Voc"])*float(partdict["FF"])*0.01
                    partdict["RscJsc"]=float(partdict["Rsc"])*float(partdict["Jsc"])*0.001
                    for item in range(len(filerawdata)):
                        if "Number of points:" in filerawdata[item]:
                            partdict["NbPoints"]=float(filerawdata[item][17:-1])
                            break
                    for item in range(len(filerawdata)):
                        if "Delay [s]:" in filerawdata[item]:
                            partdict["Delay"]=float(filerawdata[item][10:-1])
                            break
                    for item in range(len(filerawdata)):
                        if "Integration time [s]:" in filerawdata[item]:
                            partdict["IntegTime"]=float(filerawdata[item][21:-1])
                            break
                    for item in range(len(filerawdata)):
                        if "Vstart:" in filerawdata[item]:
                            partdict["Vstart"]=float(filerawdata[item][7:-1])
                            break
                    for item in range(len(filerawdata)):
                        if "Vend:" in filerawdata[item]:
                            partdict["Vend"]=float(filerawdata[item][5:-1])
                            break
                    for item in range(len(filerawdata)):
                        if "Illumination:" in filerawdata[item]:
                            partdict["Illumination"]=filerawdata[item][14:-1]
                            break
                    if abs(float(partdict["Vstart"]))>abs(float(partdict["Vend"])):
                        partdict["ScanDirection"]="Reverse"
                    else:
                        partdict["ScanDirection"]="Forward"
                    for item in range(len(filerawdata)):
                        if "Imax compliance [A]:" in filerawdata[item]:
                            partdict["ImaxComp"]=filerawdata[item][21:-1]
                            break
                    for item in range(len(filerawdata)):
                        if "I sense range:" in filerawdata[item]:
                            partdict["Isenserange"]=filerawdata[item][15:-1]
                            break
                    for item in range(len(filerawdata)):
                        if "User name:" in filerawdata[item]:
                            partdict["Operator"]=filerawdata[item][11:-1]
                            break
                    for item in range(len(filerawdata)):
                        if "MEASURED IV DATA" in filerawdata[item]:
                                pos=item+2
                                break
                        elif "MEASURED IV FRLOOP DATA" in filerawdata[item]:
                                pos=item+2
                                break
                    ivpartdat = [[],[]]#[voltage,current]
                    for item in range(pos,len(filerawdata),1):
                        ivpartdat[0].append(float(filerawdata[item].split("\t")[2]))
                        ivpartdat[1].append(0.1*float(filerawdata[item].split("\t")[3][:-1]))
                    partdict["IVData"]=ivpartdat
                    
                    partdict["Group"]="Default group"
                    partdict["Setup"]="TFIV"              
                    partdict["RefNomCurr"]=999
                    partdict["RefMeasCurr"]=999
                    partdict["AirTemp"]=999
                    partdict["ChuckTemp"]=999
        
                    #still missing: test for transposition, mirror
                    try:
                        if partdict["Illumination"]=="Light" and max(ivpartdat[0])>0.001*float(partdict["Voc"]):
                            f = interp1d(ivpartdat[0], ivpartdat[1], kind='cubic')
                            x2 = lambda x: f(x)
                            partdict["AreaJV"] = integrate.quad(x2,0,0.001*float(partdict["Voc"]))[0]
                        else:
                            partdict["AreaJV"] =""
                    except ValueError:
                        print("there is a ValueError on sample ",i)
                    
                    
                    DATA.append(partdict)
                    
            
            DATA = sorted(DATA, key=itemgetter('SampleName')) 
            names=[d["SampleName"] for d in DATA if "SampleName" in d]
            groupednames=[list(j) for i, j in groupby(names)]
            for item in range(len(groupednames)):
                if len(groupednames[item])!=1:
                    for item0 in range(1,len(groupednames[item]),1):
                        groupednames[item][item0]+= "_"+str(item0)
            groupednames=list(chain.from_iterable(groupednames))
            for item in range(len(DATA)):
                DATA[item]['SampleName']=groupednames[item]        
        
###############################################################################        
if __name__ == '__main__':
    app = DarkToLight()
    app.mainloop()





























