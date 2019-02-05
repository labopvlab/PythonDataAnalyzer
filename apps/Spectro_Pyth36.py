#! python3

import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import tkinter as tk
from tkinter import Entry, Button,messagebox, Checkbutton, IntVar, Toplevel, OptionMenu, Frame, StringVar
from tkinter import filedialog
#import ttk
from tkinter import *
#import FileDialog
from pathlib import Path
import numpy as np
import copy
import csv
from timeit import default_timer as timer
from operator import truediv as div
from math import log, pow 


"""
- update legend modification: colors, reorder...


"""

LARGE_FONT= ("Verdana", 16)
SMALL_FONT= ("Verdana", 10)

echarge = 1.60218e-19
planck = 6.62607e-34
lightspeed = 299792458

SpectlegendMod=[]
titSpect=0

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

class SpectroApp(Toplevel):

    def __init__(self, *args, **kwargs):
        
        Toplevel.__init__(self, *args, **kwargs)
        Toplevel.wm_title(self, "SpectroApp")
        Toplevel.config(self,background="white")
        self.wm_geometry("500x500")
        center(self)
        self.initUI()
        
    def initUI(self):
        self.master.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        label = tk.Label(self, text="UV-vis spectrophotometric DATA Analyzer", font=LARGE_FONT,  bg="black",fg="white")
        label.pack(fill=tk.X,expand=0)
        
        frame1=Frame(self,borderwidth=0,  bg="white")
        frame1.pack(fill=tk.BOTH,expand=1)
        
        self.fig = plt.figure(figsize=(3, 2))
        canvas = FigureCanvasTkAgg(self.fig, frame1)
        canvas.get_tk_widget().pack(fill=tk.BOTH,expand=1)
        self.Spectrograph=self.fig.add_subplot(111)
        self.toolbar = NavigationToolbar2Tk(canvas, frame1)
        self.toolbar.update()
        canvas._tkcanvas.pack(fill = BOTH, expand = 1) 
        
        frame2=Frame(self,borderwidth=0,  bg="white")
        frame2.pack(fill=tk.X,expand=0)
        
        self.helpbutton = Button(frame2, text="Help",
                            command = self.Help)
        self.helpbutton.pack(side=tk.LEFT,expand=1)
        self.importdat = Button(frame2, text="Import DATA",
                            command = self.onOpen)
        self.importdat.pack(side=tk.LEFT,expand=1)
        self.menubutton = tk.Menubutton(frame2, text="Choose wisely", 
                                   indicatoron=True, borderwidth=1, relief="raised")
        self.menu = tk.Menu(self.menubutton, tearoff=False)
        self.menubutton.configure(menu=self.menu)
        self.menubutton.pack(side=tk.LEFT,expand=1)
        self.update = Button(frame2, text="Update Graph",
                            command = self.UpdateGraph, width=15)
        self.update.pack(side=tk.LEFT,expand=1)
        
        
        self.exportgraph = Button(frame2, text="Export this graph",
                            command = self.ExportGraph)
        self.exportgraph.pack(side=tk.LEFT,expand=1)
        
        
        frame3=Frame(self,borderwidth=0,  bg="white")
        frame3.pack(fill=tk.X,expand=0)
        
        Button(frame3, text="AbsCoeff&Tauc", command = self.AbsCoeffAndTauc).pack(side=tk.LEFT,expand=1)
        self.changespectlegend = Button(frame3, text="change legend",
                            command = self.ChangeLegendSpectgraph)
        self.changespectlegend.pack(side=tk.LEFT,expand=1)
        self.exportdat = Button(frame3, text="Export All DATA",
                            command = self.sortandexportspectro)
        self.exportdat.pack(side=tk.LEFT,expand=1)
        
        frame4=Frame(frame3,borderwidth=0,  bg="white")
        frame4.pack(side=tk.LEFT,fill=tk.X,expand=0)

        frame41=Frame(frame4,borderwidth=0,  bg="white")
        frame41.pack(side=tk.LEFT, expand=0)        
        frame411=Frame(frame41,borderwidth=0,  bg="white")
        frame411.pack(side=tk.TOP,expand=0)
        frame412=Frame(frame41,borderwidth=0,  bg="white")
        frame412.pack(side=tk.BOTTOM,expand=0)

        self.minx = tk.IntVar()
        Entry(frame411, textvariable=self.minx,width=5).pack(side=tk.LEFT,expand=1)
        tk.Label(frame412, text="Min X", bg="white").pack(side=tk.LEFT,expand=1)
        self.minx.set(320)
        self.maxx = tk.IntVar()
        Entry(frame411, textvariable=self.maxx,width=5).pack(side=tk.LEFT,expand=1)
        tk.Label(frame412, text="Max X", bg="white").pack(side=tk.LEFT,expand=1)
        self.maxx.set(2000)
        self.miny = tk.IntVar()
        Entry(frame411, textvariable=self.miny,width=5).pack(side=tk.LEFT,expand=1)
        tk.Label(frame412, text="Min Y", bg="white").pack(side=tk.LEFT,expand=1)
        self.miny.set(0)
        self.maxy = tk.IntVar()
        Entry(frame411, textvariable=self.maxy,width=5).pack(side=tk.LEFT,expand=1)
        tk.Label(frame412, text="Max Y", bg="white").pack(side=tk.LEFT,expand=1)
        self.maxy.set(100)
        
        frame42=Frame(frame4,borderwidth=0,  bg="white")
        frame42.pack(side=tk.RIGHT, expand=0)
        frame421=Frame(frame42,borderwidth=0,  bg="white")
        frame421.pack(expand=0)
        frame422=Frame(frame42,borderwidth=0,  bg="white")
        frame422.pack(expand=0)
        frame423=Frame(frame42,borderwidth=0,  bg="white")
        frame423.pack(expand=0)
        
        
        self.CheckLegend = IntVar()
        legend=Checkbutton(frame423,text='Legend',variable=self.CheckLegend, 
                           onvalue=1,offvalue=0,height=1, width=10,command=self.UpdateGraph, bg="white")
        legend.pack(side=tk.LEFT,expand=1)
        

        self.pos1 = IntVar()
        pos=Checkbutton(frame421,text=None,variable=self.pos1, 
                           onvalue=1,offvalue=0,height=1, width=1,command=self.UpdateGraph, bg="white")
        pos.pack(side=tk.LEFT,expand=1)
        self.pos2 = IntVar()
        pos=Checkbutton(frame421,text=None,variable=self.pos1, 
                           onvalue=2,offvalue=0,height=1, width=1,command=self.UpdateGraph, bg="white")
        pos.pack(side=tk.LEFT,expand=1)
        self.pos3 = IntVar()
        pos=Checkbutton(frame422,text=None,variable=self.pos1, 
                           onvalue=3,offvalue=0,height=1, width=1,command=self.UpdateGraph, bg="white")
        pos.pack(side=tk.LEFT,expand=1)
        self.pos4 = IntVar()
        pos=Checkbutton(frame422,text=None,variable=self.pos1, 
                           onvalue=4,offvalue=0,height=1, width=1,command=self.UpdateGraph, bg="white")
        pos.pack(side=tk.LEFT,expand=1)
        
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
            self.master.deiconify()
            
    def Help(self):
              
        self.window = tk.Toplevel()
        self.window.wm_title("HelpDesk")
        self.window.geometry("780x550")
        self.window.config(background="white")
        center(self.window)

        label = tk.Label(self.window, text="Help!", font=("Verdana", 30), bg="white")
        label.pack()
        label = tk.Label(self.window, text="   ", font=("Verdana", 30), bg="white")
        label.pack()
        label = tk.Label(self.window, text="How do I name my files?", font=("Verdana", 20), bg="white")
        label.pack()
        label = tk.Label(self.window, text="With the UV-vis spectrophotometer, you can measure:\nTotal reflectance: _TR\nTotal transmittance: _TT\nDiffuse reflectance: _DR\nDiffuse transmittance: _DT", font=("Verdana", 12), bg="white")
        label.pack() 
        label = tk.Label(self.window, text="By ending your measurement names with _TR, _TT, _DR or _DT, the program will be able to \nrecognise them, group them, and calculate the total absorptance.", font=("Verdana", 12), bg="white")
        label.pack()
        label = tk.Label(self.window, text="   ", font=("Verdana", 30), bg="white")
        label.pack()
        label = tk.Label(self.window, text="Which files can I use?", font=("Verdana", 20), bg="white")
        label.pack()
        label = tk.Label(self.window, text="ASC File: .Sample.Raw.asc\nExcel: .Sample.Raw.csv", font=("Verdana", 12), bg="white")
        label.pack()
        label = tk.Label(self.window, text="   ", font=("Verdana", 12), bg="white")
        label.pack()
        label = tk.Label(self.window, text="Example:\nNameOfSample_TR, which then become the file: NameOfSample_TR.Sample.Raw.asc", font=("Verdana", 12), bg="white")
        label.pack()
            
        
    def onOpen(self):
        
        self.GetSpectroDATA()
        self.names = ()
        self.names=self.SampleNames(self.DATA)
        self.menu = tk.Menu(self.menubutton, tearoff=False)
        self.menubutton.configure(menu=self.menu)
        self.choices = {}
        for choice in range(len(self.names)):
            self.choices[choice] = tk.IntVar(value=0)
            self.menu.add_checkbutton(label=self.names[choice], variable=self.choices[choice], 
                                 onvalue=1, offvalue=0, command = self.UpdateGraph)
        end = timer()
        print("Ready! %s seconds" %(end-self.start))

    def GetSpectroDATA(self):
        
        file_path = filedialog.askopenfilenames()

        print("Importing...")
        self.start = timer()
        
        directory = str(Path(file_path[0]).parent.parent)+'\\resultFilesSpectro'
        
        if not os.path.exists(directory):
            os.makedirs(directory)
            os.chdir(directory)
        else :
            os.chdir(directory)
        
        if os.path.splitext(file_path[0])[1] ==".asc": #for files .Sample.Raw.asc , file with spectro info at beginning, data starts after occurence of #DATA
            DATA = []
            for item in range(len(file_path)):                
                if os.path.split(file_path[item])[1][-15:]==".Sample.Raw.asc":
                    samplename=os.path.split(file_path[item])[1][:-15]
                else:
                    samplename=os.path.split(file_path[item])[1][:-4]
            
                if samplename[-3:]=="_TT" or samplename[-3:]=="-TT": 
                    curvetype="TT"
                    samplenameshort = samplename[:-3]
                elif samplename[-2:]=="_T" or samplename[-2:]=="-T":
                    curvetype="TT"
                    samplenameshort = samplename[:-2]
                elif samplename[-3:]=="_TR" or samplename[-3:]=="-TR" or samplename[-3:]=="_RT" or samplename[-3:]=="-RT":
                    curvetype="TR" 
                    samplenameshort = samplename[:-3]
                elif  samplename[-2:]=="_R" or samplename[-2:]=="-R":
                    curvetype="TR" 
                    samplenameshort = samplename[:-2]
                elif samplename[-3:]=="_DR" or samplename[-3:]=="-DR" :
                    curvetype="DR" 
                    samplenameshort = samplename[:-3]
                elif samplename[-3:]=="_DT" or samplename[-3:]=="-DT" :
                    curvetype="DT"
                    samplenameshort = samplename[:-3]
                
                file1 = open(file_path[item])
                content = file1.readlines()
                file1.close()
                
                dataCurve = content[(content.index('#DATA\n')):len(content)]                            
                dataWave = []
                dataInt = []
                for i in range(len(dataCurve)):
                    pos = dataCurve[i].find('\t')
                    dataWave.append(dataCurve[i][:pos])
                    dataInt.append(dataCurve[i][pos+1:-1])
                dataWave=list(map(float,dataWave[1:]))
                dataInt=list(map(float,dataInt[1:]))
                datadict = [samplenameshort, curvetype, dataWave, dataInt]
                DATA.append(datadict)
                
        elif os.path.splitext(file_path[0])[1] ==".csv":   #for excel files .Sample.Raw.csv (only two columns, data starts at second line)
            DATA = []
            for item in range(len(file_path)):
                samplename=os.path.split(file_path[item])[1][:-15]
                        
                if samplename[-3:]=="_TT" or samplename[-3:]=="-TT": 
                    curvetype="TT"
                    samplenameshort = samplename[:-3]
                elif samplename[-2:]=="_T" or samplename[-2:]=="-T":
                    curvetype="TT"
                    samplenameshort = samplename[:-2]
                elif samplename[-3:]=="_TR" or samplename[-3:]=="-TR" or samplename[-3:]=="_RT" or samplename[-3:]=="-RT":
                    curvetype="TR" 
                    samplenameshort = samplename[:-3]
                elif  samplename[-2:]=="_R" or samplename[-2:]=="-R":
                    curvetype="TR" 
                    samplenameshort = samplename[:-2]
                elif samplename[-3:]=="_DR" or samplename[-3:]=="-DR" :
                    curvetype="DR" 
                    samplenameshort = samplename[:-3]
                elif samplename[-3:]=="_DT" or samplename[-3:]=="-DT" :
                    curvetype="DT"
                    samplenameshort = samplename[:-3]
                    
                with open(file_path[item]) as csvfile:
                    readCSV = csv.reader(csvfile, delimiter=',')
                    
                    dataWave = []
                    dataInt = []
                    for row in readCSV:
                        dataWave.append(row[0])
                        dataInt.append(row[1])
                    dataWave=list(map(float,dataWave[1:]))
                    dataInt=list(map(float,dataInt[1:]))
                datadict = [samplenameshort, curvetype, dataWave, dataInt]
                DATA.append(datadict)   
                
        elif os.path.splitext(file_path[0])[1] ==".SP": #for .SP files generated by CSEM spectro
            DATA = []
            for item in range(len(file_path)):
                samplename=os.path.split(file_path[item])[1][:-3]                
            
                if samplename[-3:]=="_TT" or samplename[-3:]=="-TT": 
                    curvetype="TT"
                    samplenameshort = samplename[:-3]
                elif samplename[-2:]=="_T" or samplename[-2:]=="-T":
                    curvetype="TT"
                    samplenameshort = samplename[:-2]
                elif samplename[-3:]=="_TR" or samplename[-3:]=="-TR" or samplename[-3:]=="_RT" or samplename[-3:]=="-RT":
                    curvetype="TR" 
                    samplenameshort = samplename[:-3]
                elif  samplename[-2:]=="_R" or samplename[-2:]=="-R":
                    curvetype="TR" 
                    samplenameshort = samplename[:-2]
                elif samplename[-3:]=="_DR" or samplename[-3:]=="-DR" :
                    curvetype="DR" 
                    samplenameshort = samplename[:-3]
                elif samplename[-3:]=="_DT" or samplename[-3:]=="-DT" :
                    curvetype="DT"
                    samplenameshort = samplename[:-3]
                
                file1 = open(file_path[item])
                content = file1.readlines()
                file1.close()
                if content[-1] == '\n': #condition added to screen for extra blank line at the end of file. Necessary for CSEM spectro
                    del(content[-1])
                
                dataCurve = content[(content.index('#DATA\n')):len(content)] 
                dataWave = []
                dataInt = []
                for i in range(len(dataCurve)):
                    pos = dataCurve[i].find('\t')
                    dataWave.append(dataCurve[i][:pos])
                    dataInt.append(dataCurve[i][pos+1:-1])
                dataWave=list(map(float,dataWave[1:]))
                dataInt=list(map(float,dataInt[1:]))
                datadict = [samplenameshort, curvetype, dataWave, dataInt]
                DATA.append(datadict)
        
        DATADICTtot = []
        DATA2 = copy.deepcopy(DATA)
        while DATA != []:
            listpositions = []
            name = DATA[0][0]
            for i in range(len(DATA)):
                if DATA[i][0] == name:
                    listpositions.append(i)
                else:
                    i+=1
            datadict = {'Name': name, 'Wave': DATA[0][2], 'TR': [],'TT':[],'A':[],'DR':[],'DT':[]}
            for i in range(len(listpositions)):
                if DATA[i][1]=='TR':
                    datadict['TR']=DATA[i][3]
                elif DATA[i][1]=='TT':
                    datadict['TT']=DATA[i][3]
                elif DATA[i][1]=='DR':
                    datadict['DR']=DATA[i][3]
                elif DATA[i][1]=='DT':
                    datadict['DT']=DATA[i][3]
            if datadict['TR']!=[] and datadict['TT']!=[]:
                refl = [float(i) for i in datadict['TR']]
                trans = [float(i) for i in datadict['TT']]
                absorpt = [float(i) for i in [100 - (x + y) for x, y in zip(refl, trans)]]
                datadict['A']=absorpt
                DATA2.append([name,'A',DATA[0][2],absorpt])
            DATADICTtot.append(datadict)
            for index in sorted(listpositions, reverse=True):
                del DATA[index]
        self.DATADICTtot=DATADICTtot
        self.DATA=DATA2
        
            
    def SampleNames(self, DATAx):
        Names = list(self.names)
        for item in range(len(DATAx)):
            Names.append(DATAx[item][0]+'_'+ DATAx[item][1])
        return tuple(Names)
            
    def sortandexportspectro(self):
        DATADICTtot = self.DATADICTtot   
        for i in range(len(DATADICTtot)):
            l=[['Wavelength']+['nm']+DATADICTtot[i]['Wave'],]
            if DATADICTtot[i]['TR']!=[]:
                l.append(['TR']+['%']+DATADICTtot[i]['TR'])
            if DATADICTtot[i]['TT']!=[]:
                l.append(['TT']+['%']+DATADICTtot[i]['TT'])
            if DATADICTtot[i]['A']!=[]:
                l.append(['A']+['%']+DATADICTtot[i]['A'])    
            if DATADICTtot[i]['DT']!=[]:
                l.append(['DT']+['%']+DATADICTtot[i]['DT'])    
            if DATADICTtot[i]['DR']!=[]:
                l.append(['DR']+['%']+DATADICTtot[i]['DR'])
            #content=[[k[m] for k in l] for m in range(len(l[0]))])
        
            content=np.array(l).T.tolist()
            content1=[]
            for j in range(len(content)):
                strr=''
                for k in range(len(content[j])):
                    strr = strr + content[j][k]+'\t'
                strr = strr[:-1]+'\n'
                content1.append(strr)
                    
            file = open(DATADICTtot[i]['Name'] + '.txt','w')
            file.writelines("%s" % item for item in content1)
            file.close()
    
    def UpdateGraph(self):
        global titSpect
        global SpectlegendMod
        try:        
            DATAx=self.DATA
            sampletotake=[]
            for name, var in self.choices.items():
                sampletotake.append(var.get())
            sampletotake=[i for i,x in enumerate(sampletotake) if x == 1]
            
            if SpectlegendMod!=[]:
                self.Spectrograph.clear()
                spectfig=self.Spectrograph
                for i in range(len(sampletotake)):
                    x = DATAx[sampletotake[i]][2]
                    y = DATAx[sampletotake[i]][3]
                    if self.CheckLegend.get()==1:
                        newlegend=1
                        for item in range(len(SpectlegendMod)):
                            if SpectlegendMod[item][0]==DATAx[sampletotake[i]][0]+'_'+DATAx[sampletotake[i]][1]:
                                spectfig.plot(x,y,label=SpectlegendMod[item][1])
                                newlegend=0
                                break
                        if newlegend:
                            spectfig.plot(x,y,label=DATAx[sampletotake[i]][0]+'_'+DATAx[sampletotake[i]][1])
                            SpectlegendMod.append([DATAx[sampletotake[i]][0]+'_'+DATAx[sampletotake[i]][1],DATAx[sampletotake[i]][0]+'_'+DATAx[sampletotake[i]][1]])
                    else:
                        spectfig.plot(x,y)
            else:
                self.Spectrograph.clear()
                spectfig=self.Spectrograph
                for i in range(len(sampletotake)):
                    x = DATAx[sampletotake[i]][2]
                    y = DATAx[sampletotake[i]][3]
                    if self.CheckLegend.get()==1:
                        spectfig.plot(x,y,label=DATAx[sampletotake[i]][0]+'_'+DATAx[sampletotake[i]][1])
                        SpectlegendMod.append([DATAx[sampletotake[i]][0]+'_'+DATAx[sampletotake[i]][1],DATAx[sampletotake[i]][0]+'_'+DATAx[sampletotake[i]][1]])
                    else:
                        spectfig.plot(x,y)        
            
            self.Spectrograph.set_ylabel('Intensity (%)')
            self.Spectrograph.set_xlabel('Wavelength (nm)')
            if self.CheckLegend.get()==1:
                if self.pos1.get()!=0:
                    self.leg=spectfig.legend(loc=self.pos1.get())
                elif self.pos2.get()!=0:
                    self.leg=spectfig.legend(loc=self.pos2.get())
                elif self.pos3.get()!=0:
                    self.leg=spectfig.legend(loc=self.pos3.get())
                elif self.pos4.get()!=0:
                    self.leg=spectfig.legend(loc=self.pos4.get())
                else:
                    self.leg=spectfig.legend(loc=0)
            self.Spectrograph.axis([self.minx.get(),self.maxx.get(),self.miny.get(),self.maxy.get()])
            plt.gcf().canvas.draw()
        except AttributeError:
            print("you need to import data first...")
        
    def ExportGraph(self):
        try:
            f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
            self.fig.savefig(f, dpi=300, bbox_extra_artists=(self.leg,), transparent=True) 
        except:
            print("there is an exception...check legend maybe...")
    
    def GiveSpectatitle(self):
        self.window = tk.Toplevel()
        self.window.wm_title("Change title of spectro graph")
        center(self.window)
        self.window.geometry("325x55")
        self.titleSpect = tk.StringVar()
        entry=Entry(self.window, textvariable=self.titleSpect,width=40)
        entry.grid(row=0,column=0,columnspan=1)
        self.addtitlebutton = Button(self.window, text="Update",
                            command = self.giveSpectatitleupdate)
        self.addtitlebutton.grid(row=1, column=0, columnspan=1)
    def giveSpectatitleupdate(self): 
        global titSpect
        titSpect=1
        self.UpdateGraph()
            
    def ChangeLegendSpectgraph(self):
        global SpectlegendMod
        self.window = tk.Toplevel()
        self.window.wm_title("Change Legends")
        center(self.window)
        self.window.geometry("280x300")
         
        self.changeSpectlegend = Button(self.window, text="Update",
                            command = self.UpdateSpectLegMod)
        self.changeSpectlegend.grid(row=0, column=0, columnspan=3)

        self.listofanswer=[]
        for rowitem in range(len(SpectlegendMod)):
            label=tk.Label(self.window,text=SpectlegendMod[rowitem][0])
            label.grid(row=rowitem+1,column=0, columnspan=1)
            textinit = tk.StringVar()
            self.listofanswer.append(Entry(self.window,textvariable=textinit))
            textinit.set(SpectlegendMod[rowitem][1])
            self.listofanswer[rowitem].grid(row=rowitem+1,column=1, columnspan=2)
            
    def UpdateSpectLegMod(self):
        global SpectlegendMod
        leglist=[e.get() for e in self.listofanswer]
        for item in range(len(SpectlegendMod)):
            SpectlegendMod[item][1]=leglist[item]
        self.UpdateGraph()
        
    def AbsCoeffAndTauc(self):
        self.AbsCoeffAndTaucWin = tk.Toplevel()
        self.AbsCoeffAndTaucWin.wm_title("AbsCoeff, Tauc plot")
        self.AbsCoeffAndTaucWin.geometry("280x250")
        center(self.AbsCoeffAndTaucWin)
        
        #names=self.SampleNames(self.DATA)
        
        names=[item[0]+'-'+item[1] for item in self.DATA]
        
        namesshort=[]
        for item in names:
            if item.split("-")[0] not in namesshort:
                namesshort.append(item.split("-")[0])
        
        label = tk.Label(self.AbsCoeffAndTaucWin, text="Select:", font=12, bg="white",fg="black")
        label.pack(fill=tk.X, expand=1)
        
        self.RTchoice=StringVar()
        self.dropMenuTauc = OptionMenu(self.AbsCoeffAndTaucWin, self.RTchoice, *namesshort, command=())
        self.dropMenuTauc.pack(expand=1)
        self.RTchoice.set("")
        
        label = tk.Label(self.AbsCoeffAndTaucWin, text="Thickness:", font=12, bg="white",fg="black")
        label.pack(fill=tk.X, expand=1)
        
        self.thickness = tk.DoubleVar()
        Entry(self.AbsCoeffAndTaucWin, textvariable=self.thickness,width=5).pack()
        self.thickness.set(100)
        
        label = tk.Label(self.AbsCoeffAndTaucWin, text="Transition type:", font=12, bg="white",fg="black")
        label.pack(fill=tk.X, expand=1)

        transitions=["1/2 for direct allowed", "3/2 for direct forbidden", "2 for indirect allowed", "3 for indirect forbidden"]
        self.TransitionChoice=StringVar()
        self.dropMenuTaucTrans = OptionMenu(self.AbsCoeffAndTaucWin, self.TransitionChoice, *transitions, command=())
        self.dropMenuTaucTrans.pack(expand=1)
        self.TransitionChoice.set(transitions[0])
        
        ExportTauc = Button(self.AbsCoeffAndTaucWin, text="Export",width=15, command = self.AbsCoeffAndTaucSave)
        ExportTauc.pack(fill=tk.X, expand=1)
        
        label = tk.Label(self.AbsCoeffAndTaucWin, text="AbsCoeff=-Log(TT/(1-TR))/thickness;", font=("Verdana", 8), bg="white",fg="black")
        label.pack(fill=tk.BOTH, expand=1)
        label = tk.Label(self.AbsCoeffAndTaucWin, text="Tauc=(AbsCoeff * energy)^TransitionCoeff;", font=("Verdana", 8), bg="white",fg="black")
        label.pack(fill=tk.BOTH, expand=1)
        
        

    def AbsCoeffAndTaucSave(self):
        
        if self.RTchoice.get()!="":
            if self.thickness.get()!=0:
            
                reflectance=[]
                transmittance=[]
                absorptance=[]
                wavelength=[]
                sampletotake=[]
                
                names=[item[0]+'-'+item[1] for item in self.DATA]
                sampletotake=[i for i in range(len(names)) if self.RTchoice.get()==names[i].split("-")[0]]
                
                if len(sampletotake)>0:
                    wavelength=self.DATA[sampletotake[0]][2]
                    for item in sampletotake:
                        if names[item].split("-")[1]=="TR":
                            reflectance=self.DATA[item][3]
                        elif names[item].split("-")[1]=="TT":
                            transmittance=self.DATA[item][3]
                        elif names[item].split("-")[1]=="A":
                            absorptance=self.DATA[item][3]  
                
                if reflectance!=[] and transmittance != [] and absorptance!=[] and wavelength!=[]:
                    f = filedialog.asksaveasfilename(defaultextension=".txt",initialfile= self.DATA[sampletotake[0]][0]+"_AbscoefTauc.txt", filetypes = (("text file", "*.txt"),("All Files", "*.*")))
            
                    c = lightspeed
                    h = 4.1e-15
                    dataFactor=0.01
                    
                    transition=0.5
                    if self.TransitionChoice.get()=="1/2 for direct allowed":
                        transition=0.5
                    elif self.TransitionChoice.get()=="3/2 for direct forbidden":
                        transition=1.5
                    elif self.TransitionChoice.get()=="2 for indirect allowed":
                        transition=2
                    elif self.TransitionChoice.get()=="3 for indirect forbidden":
                        transition=3
                    
                    energy=[(c*h)/(float(x)/1e9) for x in wavelength]
                    m=[dataFactor*float(x) for x in transmittance]
                    n=[1-dataFactor*float(x) for x in reflectance]
                    o=list(map(div, m,n))
                    o=[abs(x) for x in o]
                    o=list(map(log,o))
                    abscoeff=[-float(x)/(self.thickness.get()*1e-7) for x in o]
                    ahc=[pow(abs(abscoeff[i]*energy[i]),float(transition)) for i in range(len(energy))]
                    logalpha=[log(abs(item)) for i in abscoeff]
                    
                    taucdata=[]
                    taucdata.append(wavelength)
                    taucdata.append(energy)
                    taucdata.append(reflectance)
                    taucdata.append(transmittance)
                    taucdata.append(absorptance)
                    taucdata.append(logalpha)
                    taucdata.append(abscoeff)
                    taucdata.append(ahc)
                    
                    taucdata=list(map(list,zip(*taucdata)))
                    
                    taucdata=[["Wavelength","Energy","Reflectance","Transmittance","Absorptance","LogAlpha","AbsCoeff","Tauc"]]+taucdata
            
                    file = open(f,'w')
                    file.writelines("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % tuple(item) for item in taucdata)
                    file.close()
                else:
                    print("cannot find the corresponding TR and TT files")
            else:
                print("the thickness should be non-zero")
        else:
            print("choose a sample")
        
        
###############################################################################        
if __name__ == '__main__':
    app = SpectroApp()
    #app.geometry("720x750")
    center(app)
    app.mainloop()



