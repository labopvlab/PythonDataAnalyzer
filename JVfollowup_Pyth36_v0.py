#! python3

import os

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import tkinter as tk
from tkinter import Tk, messagebox, Entry, Button, Checkbutton, IntVar, Toplevel, OptionMenu, Frame, StringVar, Scrollbar, Listbox
from tkinter import filedialog
from tkinter import *
from pathlib import Path
import numpy as np
import xlsxwriter
import xlrd
from scipy.interpolate import interp1d, UnivariateSpline
from scipy import integrate, stats
from tkcolorpicker import askcolor 
import six
from functools import partial
import math
from operator import itemgetter
from itertools import groupby, chain
from datetime import datetime


#import THEANALYSER_pyth36 as analyserMain

"""
TODOLIST

- separate forward reverse

"""

DATA=[]
usernames=[]

LARGE_FONT= ("Verdana", 12)


def center(win):
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
    
class JVfollowup(Toplevel):

    def __init__(self, *args, **kwargs):
        
        Toplevel.__init__(self, *args, **kwargs)
        Toplevel.wm_title(self, "FollowingJVparameters")
        Toplevel.config(self,background="white")
        self.wm_geometry("500x500")
        center(self)
        self.initUI()


    def initUI(self):
        self.master.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.canvas0 = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.superframe=Frame(self.canvas0,background="#ffffff")
        self.canvas0.pack(side="left", fill="both", expand=True)
        
        label = tk.Label(self.canvas0, text="JV parameters over time", font=LARGE_FONT, bg="black",fg="white")
        label.pack(fill=tk.X,expand=0)
        
        frame1=Frame(self.canvas0,borderwidth=0,  bg="white")
        frame1.pack(fill=tk.BOTH,expand=1)
        frame1.bind("<Configure>", self.onFrameConfigure)
        self.fig1 = plt.figure(figsize=(3, 2))
        canvas = FigureCanvasTkAgg(self.fig1, frame1)
        canvas.get_tk_widget().pack(fill=tk.BOTH,expand=1)
        self.JVparamgraph = plt.subplot2grid((1, 5), (0, 0), colspan=5)
        self.toolbar = NavigationToolbar2TkAgg(canvas, frame1)
        self.toolbar.update()
        canvas._tkcanvas.pack(fill = BOTH, expand = 1) 
        
        
        frame2=Frame(self.canvas0,borderwidth=0,  bg="white")
        frame2.pack(fill=tk.X,expand=0)
        
        
        Button(frame2, text="import data", command = self.importdata).pack(side=tk.LEFT,expand=1)

        
        self.Usermenubutton = tk.Menubutton(frame2, text="Choose User", 
                                   indicatoron=True, borderwidth=1, relief="raised")
        self.Usermenu = tk.Menu(self.Usermenubutton, tearoff=False)
        self.Usermenubutton.configure(menu=self.Usermenu)
        self.Usermenubutton.pack(side=tk.LEFT,expand=1)

        
        Ytype = ["Jsc","Voc","FF","Eff","Vmpp","Jmpp","Roc","Rsc"]
        self.YtypeChoice=StringVar()
        self.YtypeChoice.set("Jsc") # default choice
        self.dropMenuFrame = OptionMenu(frame2, self.YtypeChoice, *Ytype, command=self.updateGraph)
        self.dropMenuFrame.pack(side=tk.LEFT,fill=tk.X,expand=1)
        
        
        Button(frame2, text="export graph", command = self.exportGraph).pack(side=tk.LEFT,expand=1)
        
        self.CheckAllgraph = IntVar()
        Checkbutton(frame2,text='all?',variable=self.CheckAllgraph, 
                           onvalue=1,offvalue=0,height=1, width=2, command = (), bg="white").pack(side=tk.LEFT,fill=tk.X,expand=1)

    def on_closing(self):
        global DATA
        global usernames
        
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            DATA=[]
            usernames=[]
            self.destroy()
            self.master.deiconify()
        
    def onFrameConfigure(self, event):
        #self.canvas0.configure(scrollregion=self.canvas0.bbox("all"))
        self.canvas0.configure(scrollregion=(0,0,500,500))
    
    def importdata(self):
        global DATA
        
        pathtofolder="//sti1files.epfl.ch/pv-lab/pvlab-commun/Groupe-Perovskite/Experiments/CellParametersFollowUP/"
        
        os.chdir(pathtofolder)

        file_pathnew=[]
        file_path =filedialog.askopenfilenames(title="Please select the .iv files", initialdir =pathtofolder)
        if file_path!='':
            filetypes=[os.path.splitext(item)[1] for item in file_path]
            if len(list(set(filetypes)))==1:
                filetype=list(set(filetypes))[0]
                if filetype==".iv":
                    file_pathnew=file_path
                    self.getdatalistsfromIVTFfiles(file_pathnew)
                else:
                    print("wrong files...")
            
    def getdatalistsfromIVTFfiles(self, file_path):
        global DATA  
        global usernames
                
        for i in range(len(file_path)):
            filetoread = open(file_path[i],"r")
            filerawdata = filetoread.readlines()
            print(i)
            filetype = 0
            for item0 in range(len(filerawdata)):
                if "voltage/current" in filerawdata[item0]:
                    filetype = 1
                    break
                if "IV FRLOOP" in filerawdata[item0]:
                    filetype =2
                    break
            try:         
                if filetype ==1 or filetype==2: #J-V files and FRLOOP
                    partdict = {}
                    
                    for item in range(len(filerawdata)):
                        if "Illumination:" in filerawdata[item]:
                            partdict["Illumination"]=filerawdata[item][14:-1]
                            break
                        else:
                            partdict["Illumination"]="Light"
                    if partdict["Illumination"]=="Light":
                    
                        partdict["SampleName"]=file_path[i].split("/")[-1][:-3]
                        
                        for item in range(len(filerawdata)):
                            if "IV measurement time:" in filerawdata[item]:
                                #partdict["MeasDayTime"]=filerawdata[item][22:-1]
                                
                                partdict["MeasDayTime"]=datetime.strptime(filerawdata[item][22:-1], '%Y-%m-%d %H:%M:%S.%f')
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
                            if "Vstart:" in filerawdata[item]:
                                partdict["Vstart"]=float(filerawdata[item][7:-1])
                                break
                        for item in range(len(filerawdata)):
                            if "Vend:" in filerawdata[item]:
                                partdict["Vend"]=float(filerawdata[item][5:-1])
                                break
                        
                        if abs(float(partdict["Vstart"]))>abs(float(partdict["Vend"])):
                            partdict["ScanDirection"]="Reverse"
                        else:
                            partdict["ScanDirection"]="Forward"
                        
                        for item in range(len(filerawdata)):
                            if "User name:" in filerawdata[item]:
                                partdict["Operator"]=filerawdata[item][11:-1]
                                break
                        
                        DATA.append(partdict)
            except:
                print("except")

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
        
        usernames=list(set([d["Operator"] for d in DATA]))
        #print(usernames)
        
        self.UserNames=tuple(usernames)
        self.Usermenu = tk.Menu(self.Usermenubutton, tearoff=False)
        self.Usermenubutton.configure(menu=self.Usermenu)
        self.choicesUsers = {}
        for choice in range(len(self.UserNames)):
            self.choicesUsers[choice] = tk.IntVar(value=0)
            self.Usermenu.add_checkbutton(label=self.UserNames[choice], variable=self.choicesUsers[choice], 
                                 onvalue=1, offvalue=0, command = ())
        print("ready")
        
    def updateGraph(self,a):
        global DATA
        global usernames
        
        takenforplot=[]
        for name, var in self.choicesUsers.items():
            takenforplot.append(var.get())
        m=[]
        for i in range(len(takenforplot)):
            if takenforplot[i]==1:
                m.append(usernames[i])
        takenforplot=m
        #print(takenforplot)
        
        #update graph
        self.JVparamgraph.clear()
        if takenforplot==[]:
            paramchoice=self.YtypeChoice.get()
                        
            timelist=[DATA[i]["MeasDayTime"] for i in range(len(DATA))]
            
            ydat=[DATA[i][paramchoice] for i in range(len(DATA))]
            
            self.JVparamgraph.plot(timelist,ydat,'o')
            
            self.JVparamgraph.set_ylabel(paramchoice, fontsize=14)
            #self.JVparamgraph.set_xlabel('Time', fontsize=14)
            plt.gcf().autofmt_xdate()
            plt.gcf().canvas.draw()
        else:
            
            for item in takenforplot:
                paramchoice=self.YtypeChoice.get()
                timelist=[DATA[i]["MeasDayTime"] for i in range(len(DATA)) if DATA[i]["Operator"]==item]
                ydat=[DATA[i][paramchoice] for i in range(len(DATA)) if DATA[i]["Operator"]==item]
                self.JVparamgraph.plot(timelist,ydat,'o', label=item)
            
            self.JVparamgraph.set_ylabel(paramchoice, fontsize=14)
            self.JVparamgraph.legend()
            plt.gcf().autofmt_xdate()
            plt.gcf().canvas.draw()
            
    def exportGraph(self):
        global DATA
        global usernames
        
        if self.CheckAllgraph.get()==0:
            f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
            self.fig1.savefig(f, dpi=300)

        else:
            f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))

            Ytype = ["Jsc","Voc","FF","Eff","Vmpp","Jmpp","Roc","Rsc"]

            for paramchoice in Ytype:
                takenforplot=[]
                for name, var in self.choicesUsers.items():
                    takenforplot.append(var.get())
                m=[]
                for i in range(len(takenforplot)):
                    if takenforplot[i]==1:
                        m.append(usernames[i])
                takenforplot=m

                self.JVparamgraph.clear()
                
                if takenforplot==[]:                                
                    timelist=[DATA[i]["MeasDayTime"] for i in range(len(DATA))]
                    
                    ydat=[DATA[i][paramchoice] for i in range(len(DATA))]
                    
                    self.JVparamgraph.plot(timelist,ydat,'o')
                    
                    self.JVparamgraph.set_ylabel(paramchoice, fontsize=14)
                    plt.gcf().autofmt_xdate()
                    plt.gcf().canvas.draw()
                else:
                    
                    for item in takenforplot:
                        timelist=[DATA[i]["MeasDayTime"] for i in range(len(DATA)) if DATA[i]["Operator"]==item]
                        ydat=[DATA[i][paramchoice] for i in range(len(DATA)) if DATA[i]["Operator"]==item]
                        self.JVparamgraph.plot(timelist,ydat,'o', label=item)
                    
                    self.JVparamgraph.set_ylabel(paramchoice, fontsize=14)
                    self.JVparamgraph.legend()
                    plt.gcf().autofmt_xdate()
                    plt.gcf().canvas.draw()
                
                self.fig1.savefig(f[:-4]+"_"+paramchoice+f[-4:], dpi=300)
            
            
            
            
###############################################################################        
if __name__ == '__main__':
    
    app = JVfollowup()
    app.mainloop()


