#! python3

import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import tkinter as tk
from tkinter import *
from tkinter.ttk import Treeview
from tkinter import messagebox, Button, Label, Frame, Entry, Checkbutton, IntVar, Toplevel, Scrollbar, Canvas, OptionMenu, StringVar

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
from tkinter import font as tkFont
from matplotlib.transforms import Bbox
import pickle
import six
from tkinter import colorchooser
from functools import partial
import darktolight as DtoL
import os.path
import shutil
import sqlite3

"""
TODOLIST

- low illumination: mirrored curves, chech automatically and mirror the curve
- illumination intensity given in legend
=> place dark data analysis in a pop-up window
 
- make it compatible with HIT files: how to select the batch, wafer, cell names? check with Mario&Co if they agreed on something


- when finish autoanalysis, it doesn't plot back the same as before for the mpp

- low-intensity meas: if several intensities for a single cell
    get automatic graph of Voc&Jsc&FF as function of intensity
    fits ? something to extract?

- group: modify the name of an existing group => automatically change in all samples
- group: select which one to plot (so that we don't have to delete them)

"""
#%%############# Global variable definition
testdata = []
DATA = [] #[{"SampleName":, "CellNumber": , "MeasDayTime":, "CellSurface":, "Voc":, "Jsc":, "FF":, "Eff":, "Pmpp":, "Vmpp":, "Jmpp":, "Roc":, "Rsc":, "VocFF":, "RscJsc":, "NbPoints":, "Delay":, "IntegTime":, "Vstart":, "Vend":, "Illumination":, "ScanDirection":, "ImaxComp":, "Isenserange":,"AreaJV":, "Operator":, "MeasComment":, "IVData":}]
DATAJVforexport=[]
DATAJVtabforexport=[]
DATAmppforexport=[]
DATAgroupforexport=[]
takenforplot=[]
takenforplotmpp=[]

DATAMPP = []
DATAdark = []
DATAFV=[]

IVlegendMod = []
IVlinestyle = []
colorstylelist = ['black', 'red', 'blue', 'brown', 'green','cyan','magenta','olive','navy','orange','gray','aliceblue','antiquewhite','aqua','aquamarine','azure','beige','bisque','blanchedalmond','blue','blueviolet','brown','burlywood','cadetblue','chartreuse','chocolate','coral','cornflowerblue','cornsilk','crimson','darkblue','darkcyan','darkgoldenrod','darkgray','darkgreen','darkkhaki','darkmagenta','darkolivegreen','darkorange','darkorchid','darkred','darksalmon','darkseagreen','darkslateblue','darkslategray','darkturquoise','darkviolet','deeppink','deepskyblue','dimgray','dodgerblue','firebrick','floralwhite','forestgreen','fuchsia','gainsboro','ghostwhite','gold','goldenrod','greenyellow','honeydew','hotpink','indianred','indigo','ivory','khaki','lavender','lavenderblush','lawngreen','lemonchiffon','lightblue','lightcoral','lightcyan','lightgoldenrodyellow','lightgreen','lightgray','lightpink','lightsalmon','lightseagreen','lightskyblue','lightslategray','lightsteelblue','lightyellow','lime','limegreen','linen','magenta','maroon','mediumaquamarine','mediumblue','mediumorchid','mediumpurple','mediumseagreen','mediumslateblue','mediumspringgreen','mediumturquoise','mediumvioletred','midnightblue','mintcream','mistyrose','moccasin','navajowhite','navy','oldlace','olive','olivedrab','orange','orangered','orchid','palegoldenrod','palegreen','paleturquoise','palevioletred','papayawhip','peachpuff','peru','pink','plum','powderblue','purple','red','rosybrown','royalblue','saddlebrown','salmon','sandybrown','seagreen','seashell','sienna','silver','skyblue','slateblue','slategray','snow','springgreen','steelblue','tan','teal','thistle','tomato','turquoise','violet','wheat','white','whitesmoke','yellow','yellowgreen']

MPPlegendMod = []
MPPlinestyle = []

titIV =0
titmpp=0
titStat=0
samplesgroups=["Default group"]

listofanswer=[]
listoflinestyle=[]
listofcolorstyle=[]


#%%#############

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
    
#%%#############             
    
class IVApp(Toplevel):

    def __init__(self, *args, **kwargs): 
        """
        initialize the graphical user interface with all buttons, graphs and tables, calling the functions defined below
        """
        Toplevel.__init__(self, *args, **kwargs)
        Toplevel.wm_title(self, "IVApp")
        Toplevel.config(self,background="white")
        self.wm_geometry("1050x700")
        self.wm_resizable(True,True)
        center(self)
        #self.iconbitmap('icon1.ico') #gives an error when calling self.__init__() : TclError: bitmap "icon1.ico" not defined
        
        self.master.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.canvas0 = tk.Canvas(self, borderwidth=0, background="white")
        self.superframe=Frame(self.canvas0,background="white")
        
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas0.yview)
        self.canvas0.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.hsb = tk.Scrollbar(self, orient="horizontal", command=self.canvas0.xview)
        self.canvas0.configure(xscrollcommand=self.hsb.set)
        self.hsb.pack(side="bottom", fill="x")
        
        self.canvas0.pack(side="left", fill="both", expand=True)
        
        self.canvas0.create_window((1,4), window=self.superframe, anchor="nw", 
                                  tags="self.superframe")
        self.superframe.bind("<Configure>", self.onFrameConfigure)
        
        ############ the figures #################
        self.fig = plt.figure(figsize=(13, 10))
        self.fig.patch.set_facecolor('white')
        canvas = FigureCanvasTkAgg(self.fig, self.superframe)
        canvas.get_tk_widget().grid(row=0,column=0,rowspan=80,columnspan=100)
        self.IVsubfig = self.fig.add_subplot(331)        
        self.mppsubfig = self.fig.add_subplot(333) 
        self.GroupStatfig = self.fig.add_subplot(337)  
         
        label = tk.Label(self.superframe, text="IV & MPPT DATA Analyzer", bg="black",fg="white")
        label.grid(row = 0, column = 0, rowspan = 2, columnspan = 100, sticky = "wens")
              
        self.Frame2 = Frame(self.superframe, bg="white")
        self.Frame2.grid(row = 34, column = 0, rowspan = 15, columnspan = 100, sticky = "wens") 

        for r in range(15):
            self.Frame2.rowconfigure(r, weight=1)    
        for c in range(100):
            self.Frame2.columnconfigure(c, weight=1)
               
        #### Group ####
        columnpos = 8
        rowpos = 49
        
        self.saveGroupgraph = Button(self.superframe, text="Save graph",
                            command = self.GraphGroupsave_as)
        self.saveGroupgraph.grid(row=rowpos, column=8, columnspan=5)
        
        GroupChoiceList = ["Voc","Jsc","FF", "Eff", "Roc", "Rsc","Vmpp","Jmpp"]
        self.GroupChoice=StringVar()
        self.GroupChoice.set("Eff") # default choice
        self.dropMenuGroup = OptionMenu(self.superframe, self.GroupChoice, *GroupChoiceList, command=self.UpdateGroupGraph)
        self.dropMenuGroup.grid(row=rowpos, column=columnpos+5, columnspan=5)
        
        self.Big4 = IntVar()
        Big4=Checkbutton(self.superframe,text="Big4",variable=self.Big4, 
                           onvalue=1,offvalue=0,height=1, width=3, command = (),fg='black',background='white')
        Big4.grid(row=rowpos, column=columnpos+10, columnspan=3)
        
        self.RF = IntVar()
        RF=Checkbutton(self.superframe,text="RF",variable=self.RF, 
                           onvalue=1,offvalue=0,height=1, width=3, command = lambda: self.UpdateGroupGraph(1),fg='black',background='white')
        RF.grid(row=rowpos, column=columnpos+14, columnspan=3)
        self.boxplot = IntVar()
        boxplot=Checkbutton(self.superframe,text="box",variable=self.boxplot, 
                           onvalue=1,offvalue=0,height=1, width=3, command = lambda: self.UpdateGroupGraph(1),fg='black',background='white')
        boxplot.grid(row=rowpos, column=columnpos+17, columnspan=3)
        self.boxplot.set(1)
        
        self.fontsizeGroupGraph = tk.DoubleVar()
        entry=Entry(self.superframe, textvariable=self.fontsizeGroupGraph,width=3)
        entry.grid(row=rowpos,column=columnpos+22,columnspan=1)
        tk.Label(self.superframe, text="Fontsize",fg='black',background='white').grid(row=rowpos,column=columnpos+23,columnspan=4)
        self.fontsizeGroupGraph.set(8)
        
        self.rotationGroupGraph = tk.DoubleVar()
        entry=Entry(self.superframe, textvariable=self.rotationGroupGraph,width=3)
        entry.grid(row=rowpos+2,column=8,columnspan=1)
        tk.Label(self.superframe, text="RotLab",fg='black',background='white').grid(row=rowpos+1,column=8,columnspan=2)
        self.rotationGroupGraph.set(30)
        
        #### JV ####

        columnpos = 24
        rowpos = 0
        
        self.saveIVgraph = Button(self.Frame2, text="Save graph",
                            command = self.GraphJVsave_as)
        self.saveIVgraph.grid(row=rowpos+1, column=columnpos, columnspan=3)
                
        self.updateIVgraph = Button(self.Frame2, text="Update graph",
                            command = self.UpdateIVGraph)
        self.updateIVgraph.grid(row=rowpos+2, column=columnpos, columnspan=3)
        
        self.changeIVlegend = Button(self.Frame2, text="change legend",
                            command = self.ChangeLegendIVgraph)
        self.changeIVlegend.grid(row=rowpos+3, column=columnpos, columnspan=3)
        
        self.CheckIVLegend = IntVar()
        legend=Checkbutton(self.Frame2,text='Legend',variable=self.CheckIVLegend, 
                           onvalue=1,offvalue=0,height=1, width=10, command = self.UpdateIVGraph,fg='black',background='white')
        legend.grid(row=rowpos+1, column=columnpos+3, columnspan=3)
        
        self.CheckIVLog = IntVar()
        logJV=Checkbutton(self.Frame2,text='Log',variable=self.CheckIVLog, 
                           onvalue=1,offvalue=0,height=1, width=10, command = self.UpdateIVGraph,fg='black',background='white')
        logJV.grid(row=rowpos+1, column=columnpos+5, columnspan=3)
        
        self.IVtitle = Button(self.Frame2, text="Title",
                            command = self.GiveIVatitle)
        self.IVtitle.grid(row=rowpos, column=columnpos+3, columnspan=3)
        
        self.IVminx = tk.DoubleVar()
        entry=Entry(self.Frame2, textvariable=self.IVminx,width=5)
        entry.grid(row=rowpos+4,column=columnpos,columnspan=1)
        tk.Label(self.Frame2, text="Min X",fg='black',background='white').grid(row=rowpos+5,column=columnpos,columnspan=1)
        self.IVminx.set(-0.2)
        self.IVmaxx = tk.DoubleVar()
        Entry(self.Frame2, textvariable=self.IVmaxx,width=5).grid(row=rowpos+4,column=columnpos+1,columnspan=1)
        tk.Label(self.Frame2, text="Max X",fg='black',background='white').grid(row=rowpos+5,column=columnpos+1,columnspan=1)
        self.IVmaxx.set(1.3) 
        self.IVminy = tk.DoubleVar()
        Entry(self.Frame2, textvariable=self.IVminy,width=5).grid(row=rowpos+4,column=columnpos+2,columnspan=1)
        tk.Label(self.Frame2, text="Min Y",fg='black',background='white').grid(row=rowpos+5,column=columnpos+2,columnspan=1)
        self.IVminy.set(-22)
        self.IVmaxy = tk.DoubleVar()
        Entry(self.Frame2, textvariable=self.IVmaxy,width=5).grid(row=rowpos+4,column=columnpos+3,columnspan=1)
        tk.Label(self.Frame2, text="Max Y",fg='black',background='white').grid(row=rowpos+5,column=columnpos+3,columnspan=1)
        self.IVmaxy.set(5)
        
        self.IVlegpos1 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.IVlegpos1, 
                           onvalue=1,offvalue=0,height=1, width=1, command = self.UpdateIVGraph,fg='black',background='white')
        pos.grid(row=rowpos+2, column=columnpos+4, columnspan=1)
        self.pos2 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.IVlegpos1, 
                           onvalue=2,offvalue=0,height=1, width=1, command = self.UpdateIVGraph,fg='black',background='white')
        pos.grid(row=rowpos+2, column=columnpos+3, columnspan=1)
        self.pos3 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.IVlegpos1, 
                           onvalue=3,offvalue=0,height=1, width=1, command = self.UpdateIVGraph,fg='black',background='white')
        pos.grid(row=rowpos+3, column=columnpos+3, columnspan=1)
        self.pos4 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.IVlegpos1, 
                           onvalue=4,offvalue=0,height=1, width=1, command = self.UpdateIVGraph,fg='black',background='white')
        pos.grid(row=rowpos+3, column=columnpos+4, columnspan=1)
        self.pos5 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.IVlegpos1, 
                           onvalue=5,offvalue=0,height=1, width=1, command = self.UpdateIVGraph,fg='black',background='white')
        pos.grid(row=rowpos+4, column=columnpos+4, columnspan=1)
        
        
        #### MPP ###
        
        columnpos = 72
        rowpos = 0
        
        self.mppmenubutton = tk.Menubutton(self.Frame2, text="Choose mpp data", 
                                   indicatoron=True, borderwidth=1, relief="raised")
        self.mppmenu = tk.Menu(self.mppmenubutton, tearoff=False)
        self.mppmenubutton.configure(menu=self.mppmenu)
        self.mppmenubutton.grid(row=rowpos, column=columnpos, columnspan=3)

        self.savemppgraph = Button(self.Frame2, text="Save graph",
                            command = self.GraphMPPsave_as)
        self.savemppgraph.grid(row=rowpos+1, column=columnpos, columnspan=3)
        
        self.updatemppgraph = Button(self.Frame2, text="Update graph",
                           command = self.UpdateMppGraph)
        self.updatemppgraph.grid(row=rowpos+2, column=columnpos, columnspan=3)
        
        self.changempplegend = Button(self.Frame2, text="change legend",
                            command = self.ChangeLegendMPPgraph)
        self.changempplegend.grid(row=rowpos+3, column=columnpos, columnspan=3)
        
        self.CheckmppLegend = IntVar()
        legend=Checkbutton(self.Frame2,text='Legend',variable=self.CheckmppLegend, 
                           onvalue=1,offvalue=0,height=1, width=10, command = self.UpdateMppGraph,fg='black',background='white')
        legend.grid(row=rowpos+1, column=columnpos+3, columnspan=3)
        
        self.mpptitle = Button(self.Frame2, text="Title",
                            command = self.GiveMPPatitle)
        self.mpptitle.grid(row=rowpos, column=columnpos+3, columnspan=3)

        
        self.mppminx = tk.DoubleVar()
        Entry(self.Frame2, textvariable=self.mppminx,width=5).grid(row=rowpos+4,column=columnpos,columnspan=1)
        tk.Label(self.Frame2, text="Min X",fg='black',background='white').grid(row=rowpos+5,column=columnpos,columnspan=1)
        self.mppminx.set(0)
        self.mppmaxx = tk.DoubleVar()
        Entry(self.Frame2, textvariable=self.mppmaxx,width=5).grid(row=rowpos+4,column=columnpos+1,columnspan=1)
        tk.Label(self.Frame2, text="Max X",fg='black',background='white').grid(row=rowpos+5,column=columnpos+1,columnspan=1)
        self.mppmaxx.set(500)
        self.mppminy = tk.DoubleVar()
        Entry(self.Frame2, textvariable=self.mppminy,width=5).grid(row=rowpos+4,column=columnpos+2,columnspan=1)
        tk.Label(self.Frame2, text="Min Y",fg='black',background='white').grid(row=rowpos+5,column=columnpos+2,columnspan=1)
        self.mppminy.set(0)
        self.mppmaxy = tk.DoubleVar()
        Entry(self.Frame2, textvariable=self.mppmaxy,width=5).grid(row=rowpos+4,column=columnpos+3,columnspan=1)
        tk.Label(self.Frame2, text="Max Y",fg='black',background='white').grid(row=rowpos+5,column=columnpos+3,columnspan=1)
        self.mppmaxy.set(200)
        
        self.mpplegpos1 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.mpplegpos1, 
                           onvalue=1,offvalue=0,height=1, width=1, command = self.UpdateMppGraph,fg='black',background='white')
        pos.grid(row=rowpos+2, column=columnpos+4, columnspan=1)
        self.pos2 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.mpplegpos1, 
                           onvalue=2,offvalue=0,height=1, width=1, command = self.UpdateMppGraph,fg='black',background='white')
        pos.grid(row=rowpos+2, column=columnpos+3, columnspan=1)
        self.pos3 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.mpplegpos1, 
                           onvalue=3,offvalue=0,height=1, width=1, command = self.UpdateMppGraph,fg='black',background='white')
        pos.grid(row=rowpos+3, column=columnpos+3, columnspan=1)
        self.pos4 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.mpplegpos1, 
                           onvalue=4,offvalue=0,height=1, width=1, command = self.UpdateMppGraph,fg='black',background='white')
        pos.grid(row=rowpos+3, column=columnpos+4, columnspan=1)
        self.pos5 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.mpplegpos1, 
                           onvalue=5,offvalue=0,height=1, width=1, command = self.UpdateMppGraph,fg='black',background='white')
        pos.grid(row=rowpos+4, column=columnpos+4, columnspan=1)
        
        ############ the table ###################
        global testdata
        global DATA
        
        self.frame0 = Frame(self.superframe,bg='black')
        self.frame0.grid(row=48,column=35,rowspan=25,columnspan=65) #,sticky='wens'
        for r in range(25):
            self.frame0.rowconfigure(r, weight=1)    
        for c in range(65):
            self.frame0.columnconfigure(c, weight=1)
        
        self.import_button = Button(self.frame0, text = "Import Data", command = self.importdata)
        self.import_button.grid(row = 0, column = 0,columnspan=1)
#        self.loadsession_button = Button(self.frame0, text = "Load session", command = self.LoadSession)
#        self.loadsession_button.grid(row = 0, column = 4, columnspan=1)
#        self.savesession_button = Button(self.frame0, text = "Save session", command = self.SaveSession)
#        self.savesession_button.grid(row = 0, column = 5, columnspan=1)
        self.ExportAll = Button(self.frame0, text="DB & AutoAnalysis", command = self.AskforRefcells)
        self.ExportAll.grid(row=0, column=6, columnspan=1,rowspan=1)
        self.Darktolight = Button(self.frame0, text="DtoL.",command = self.darktolightchange,fg='black')
        self.Darktolight.grid(row=0, column=8, columnspan=1,rowspan=1)
        self.changeArea = Button(self.frame0, text="ChangeArea",command = self.changecellarea,fg='black')
        self.changeArea.grid(row=0, column=11, columnspan=1,rowspan=1)
        
        self.TableBuilder(self.frame0)
        
        self.workongoing = tk.Label(self.superframe, text='ready', font=12, relief=tk.RIDGE, width=10)
        self.workongoing.grid(row=32, column=0,columnspan=8,rowspan=10)
    

#%%######################################################################
        
    def on_closing(self):
        """
        what happens when user clicks on the red cross to exit the window.
        reinitializes all lists and destroys the window
        """
        global testdata, DATA, DATAJVforexport, DATAJVtabforexport
        global DATAmppforexport, DATAgroupforexport, takenforplot
        global takenforplotmpp, DATAMPP, DATAdark, DATAFV, IVlegendMod
        global IVlinestyle, colorstylelist, MPPlegendMod, MPPlinestyle
        global titIV, titmpp, titStat, samplesgroups, listofanswer, listoflinestyle, listofcolorstyle
        
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            testdata = []
            DATA = [] #[{"SampleName":, "CellNumber": , "MeasDayTime":, "CellSurface":, "Voc":, "Jsc":, "FF":, "Eff":, "Pmpp":, "Vmpp":, "Jmpp":, "Roc":, "Rsc":, "VocFF":, "RscJsc":, "NbPoints":, "Delay":, "IntegTime":, "Vstart":, "Vend":, "Illumination":, "ScanDirection":, "ImaxComp":, "Isenserange":,"AreaJV":, "Operator":, "MeasComment":, "IVData":}]
            DATAJVforexport=[]
            DATAJVtabforexport=[]
            DATAmppforexport=[]
            DATAgroupforexport=[]
            takenforplot=[]
            takenforplotmpp=[]
            plt.close()
            DATAMPP = []
            DATAdark = []
            DATAFV=[]
            
            IVlegendMod = []
            IVlinestyle = []
            colorstylelist = ['black', 'red', 'blue', 'brown', 'green','cyan','magenta','olive','navy','orange','gray','aliceblue','antiquewhite','aqua','aquamarine','azure','beige','bisque','blanchedalmond','blue','blueviolet','brown','burlywood','cadetblue','chartreuse','chocolate','coral','cornflowerblue','cornsilk','crimson','darkblue','darkcyan','darkgoldenrod','darkgray','darkgreen','darkkhaki','darkmagenta','darkolivegreen','darkorange','darkorchid','darkred','darksalmon','darkseagreen','darkslateblue','darkslategray','darkturquoise','darkviolet','deeppink','deepskyblue','dimgray','dodgerblue','firebrick','floralwhite','forestgreen','fuchsia','gainsboro','ghostwhite','gold','goldenrod','greenyellow','honeydew','hotpink','indianred','indigo','ivory','khaki','lavender','lavenderblush','lawngreen','lemonchiffon','lightblue','lightcoral','lightcyan','lightgoldenrodyellow','lightgreen','lightgray','lightpink','lightsalmon','lightseagreen','lightskyblue','lightslategray','lightsteelblue','lightyellow','lime','limegreen','linen','magenta','maroon','mediumaquamarine','mediumblue','mediumorchid','mediumpurple','mediumseagreen','mediumslateblue','mediumspringgreen','mediumturquoise','mediumvioletred','midnightblue','mintcream','mistyrose','moccasin','navajowhite','navy','oldlace','olive','olivedrab','orange','orangered','orchid','palegoldenrod','palegreen','paleturquoise','palevioletred','papayawhip','peachpuff','peru','pink','plum','powderblue','purple','red','rosybrown','royalblue','saddlebrown','salmon','sandybrown','seagreen','seashell','sienna','silver','skyblue','slateblue','slategray','snow','springgreen','steelblue','tan','teal','thistle','tomato','turquoise','violet','wheat','white','whitesmoke','yellow','yellowgreen']
            
            MPPlegendMod = []
            MPPlinestyle = []
            
            titIV =0
            titmpp=0
            titStat=0
            samplesgroups=["Default group"]
            
            listofanswer=[]
            listoflinestyle=[]
            listofcolorstyle=[]            

            self.destroy()
            self.master.deiconify()

    
    def darktolightchange(self):
        DtoL.DarkToLight()
        
    def onFrameConfigure(self, event):
        self.canvas0.configure(scrollregion=self.canvas0.bbox("all"))
        #self.canvas0.configure(scrollregion=(0,0,500,500))
    def start(self):
        self.progress["value"] = 0
        self.maxbytes = 100000
        self.progress["maximum"] = 100000
        self.read_bytes()
        
    def updateTable(self):
        self.TableBuilder(self.frame0)

#%%######################################################################
        
    def importdata(self):
        global DATA 
        global DATAFV
        global DATAMPP
        global DATAdark
               
        self.workongoing.configure(text="Importation\nstarted...\nPatience\nis a great\nvirtue")
        
        finished=0
        j=0
        while j<2:
            #try: 
            file_pathnew=[]
            file_path =filedialog.askopenfilenames(title="Please select the IV files")
            if file_path!='':
                filetypes=[os.path.splitext(item)[1] for item in file_path]
                if len(list(set(filetypes)))==1:
                    directory = str(Path(file_path[0]).parent.parent)+'\\resultFilesIV'
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                        os.chdir(directory)
                    else :
                        os.chdir(directory)
                    filetype=list(set(filetypes))[0]
                    if filetype==".iv":
                        file_pathnew=file_path
                        print("these are rawdata files")
                        self.getdatalistsfromIVTFfiles(file_pathnew)
                        finished=1
                        break
                    elif filetype==".xls":
                        celltest=[]
                        for k in range(len(file_path)):
                            wb = xlrd.open_workbook(file_path[k])
                            xlsheet = wb.sheet_by_index(0)
                            celltest.append(str(xlsheet.cell(3,0).value))
                        if len(list(set(celltest)))==1:
                            if celltest[0]=="User name:             ":#HIT excel files
                                print("HITfiles")
                                self.getdatalistsfromIVHITfiles(file_path)
                                finished=1
                                break
                            elif str(xlsheet.cell(3,1).value)=="Cell number":
                                print("thin film files")
                                for k in range(len(file_path)):
                                    wb = xlrd.open_workbook(file_path[k])
                                    sheet_names = wb.sheet_names()
                                    for j in range(len(sheet_names)):
                                        if 'Sheet' not in sheet_names[j]:
                                            xlsheet = wb.sheet_by_index(j)
                                            #print(sheet_names[j])
                                            item=0
                                            while(True):
                                                try:
                                                    #print(item)
                                                    cell1 = xlsheet.cell(68+item,17).value 
                                                    #print(cell1)
                                                    if cell1!="":
                                                        file_pathnew.append(cell1)
                                                        item+=1
                                                    else:
                                                        break
                                                except:
                                                    print("except")
                                                    break
                                self.getdatalistsfromIVTFfiles(file_pathnew)
                                finished=1
                                break
                            else:
                                print("these are not IV related .xls files... try again")
                                j+=1
                        else:
                            print("several types of .xls files... try again")
                            j+=1
                    else:
                        print("neither .iv or .xls IV files... try again")
                        j+=1
                else:
                    print("Multiple types of files... please choose one!")
                    j+=1
            else:
                print("Please select IV files")
                j+=1
            #except:
            #    print("no file selected")
            #    j+=1
        
        if finished:
            print("getdata done")
            print(len(DATA))
            print(len(DATAMPP))
            print(len(DATAdark))
            print(len(DATAFV))
            self.workongoing.configure(text="Imported:\n%d JV files\n%d MPP files\n%d Dark files " % (len(DATA),len(DATAMPP),len(DATAdark)))
            
            if DATAMPP!=[]:
                self.mppnames = ()
                self.mppnames=self.SampleMppNames(DATAMPP)
                self.mppmenu = tk.Menu(self.mppmenubutton, tearoff=False)
                self.mppmenubutton.configure(menu=self.mppmenu)
                self.choicesmpp = {}
                for choice in range(len(self.mppnames)):
                    self.choicesmpp[choice] = tk.IntVar(value=0)
                    self.mppmenu.add_checkbutton(label=self.mppnames[choice], variable=self.choicesmpp[choice], 
                                         onvalue=1, offvalue=0, command = self.UpdateMppGraph0)
            
            self.updateTable()
            
#%%######################################################################
            
    def UpdateGroupGraph(self,a):
        global DATA
        global DATAdark
        global DATAFV
        global DATAMPP
        global samplesgroups
        global DATAgroupforexport
        
        DATAgroupforexport=[]
        fontsizegroup=self.fontsizeGroupGraph.get()
        DATAx=copy.deepcopy(DATA)
        
        try:
            if len(samplesgroups)>1:    #if user defined group names different than "Default group"        
                grouplistdict=[]
                if self.RF.get()==0:    #select all data points
                    for item in range(1,len(samplesgroups),1):
                        groupdict={}
                        groupdict["Group"]=samplesgroups[item]
                        listofthegroup=[]
                        for item1 in range(len(DATAx)):
                            if DATAx[item1]["Group"]==groupdict["Group"]:
                                listofthegroup.append(DATAx[item1])
                        
                        listofthegroupRev=[]
                        listofthegroupFor=[]
                        for item1 in range(len(listofthegroup)):
                            if listofthegroup[item1]["ScanDirection"]=="Reverse":
                                listofthegroupRev.append(listofthegroup[item1])
                            else:
                                listofthegroupFor.append(listofthegroup[item1])
                        
                        groupdict["RevVoc"]=[x['Voc'] for x in listofthegroupRev if 'Voc' in x]
                        groupdict["ForVoc"]=[x['Voc'] for x in listofthegroupFor if 'Voc' in x]
                        groupdict["RevJsc"]=[x['Jsc'] for x in listofthegroupRev if 'Jsc' in x]
                        groupdict["ForJsc"]=[x['Jsc'] for x in listofthegroupFor if 'Jsc' in x]
                        groupdict["RevFF"]=[x['FF'] for x in listofthegroupRev if 'FF' in x]
                        groupdict["ForFF"]=[x['FF'] for x in listofthegroupFor if 'FF' in x]
                        groupdict["RevEff"]=[x['Eff'] for x in listofthegroupRev if 'Eff' in x]
                        groupdict["ForEff"]=[x['Eff'] for x in listofthegroupFor if 'Eff' in x]
                        groupdict["RevRoc"]=[x['Roc'] for x in listofthegroupRev if 'Roc' in x]
                        groupdict["ForRoc"]=[x['Roc'] for x in listofthegroupFor if 'Roc' in x]
                        groupdict["RevRsc"]=[x['Rsc'] for x in listofthegroupRev if 'Rsc' in x]
                        groupdict["ForRsc"]=[x['Rsc'] for x in listofthegroupFor if 'Rsc' in x]
                        groupdict["RevVmpp"]=[x['Vmpp'] for x in listofthegroupRev if 'Vmpp' in x]
                        groupdict["ForVmpp"]=[x['Vmpp'] for x in listofthegroupFor if 'Vmpp' in x]
                        groupdict["RevJmpp"]=[x['Jmpp'] for x in listofthegroupRev if 'Jmpp' in x]
                        groupdict["ForJmpp"]=[x['Jmpp'] for x in listofthegroupFor if 'Jmpp' in x]
                        
                        grouplistdict.append(groupdict)
                        
                elif self.RF.get()==1:      #select only the best RevFor of each cell
                    
                    for item in range(1,len(samplesgroups),1):
                        groupdict={}
                        groupdict["Group"]=samplesgroups[item]
                        listofthegroup=[]
                        for item1 in range(len(DATAx)):
                            if DATAx[item1]["Group"]==groupdict["Group"]:
                                listofthegroup.append(DATAx[item1])
    
                        grouper = itemgetter("DepID", "Cellletter",'ScanDirection')
                        result = []
                        for key, grp in groupby(sorted(listofthegroup, key = grouper), grouper):
                            result.append(list(grp))
                        
                        result1=[]
                        
                        for item in result:
                            result1.append(sorted(item,key=itemgetter('Eff'),reverse=True)[0])
                        
                        grouper = itemgetter('ScanDirection')
                        result2 = []
                        for key, grp in groupby(sorted(result1, key = grouper), grouper):
                            result2.append(list(grp))
                        
                        listofthegroupRev=[]
                        listofthegroupFor=[]
                        
                        if result2[0][0]['ScanDirection']=='Forward':
                            listofthegroupFor=result2[0]
                            if len(result2)>1:
                                listofthegroupRev=result2[1]
                        else:
                            listofthegroupRev=result2[0]
                            if len(result2)>1:
                                listofthegroupFor=result2[1]
    
                        groupdict["RevVoc"]=[x['Voc'] for x in listofthegroupRev if 'Voc' in x]
                        groupdict["ForVoc"]=[x['Voc'] for x in listofthegroupFor if 'Voc' in x]
                        groupdict["RevJsc"]=[x['Jsc'] for x in listofthegroupRev if 'Jsc' in x]
                        groupdict["ForJsc"]=[x['Jsc'] for x in listofthegroupFor if 'Jsc' in x]
                        groupdict["RevFF"]=[x['FF'] for x in listofthegroupRev if 'FF' in x]
                        groupdict["ForFF"]=[x['FF'] for x in listofthegroupFor if 'FF' in x]
                        groupdict["RevEff"]=[x['Eff'] for x in listofthegroupRev if 'Eff' in x]
                        groupdict["ForEff"]=[x['Eff'] for x in listofthegroupFor if 'Eff' in x]
                        groupdict["RevRoc"]=[x['Roc'] for x in listofthegroupRev if 'Roc' in x]
                        groupdict["ForRoc"]=[x['Roc'] for x in listofthegroupFor if 'Roc' in x]
                        groupdict["RevRsc"]=[x['Rsc'] for x in listofthegroupRev if 'Rsc' in x]
                        groupdict["ForRsc"]=[x['Rsc'] for x in listofthegroupFor if 'Rsc' in x]
                        groupdict["RevVmpp"]=[x['Vmpp'] for x in listofthegroupRev if 'Vmpp' in x]
                        groupdict["ForVmpp"]=[x['Vmpp'] for x in listofthegroupFor if 'Vmpp' in x]
                        groupdict["RevJmpp"]=[x['Jmpp'] for x in listofthegroupRev if 'Jmpp' in x]
                        groupdict["ForJmpp"]=[x['Jmpp'] for x in listofthegroupFor if 'Jmpp' in x]
                        
                        grouplistdict.append(groupdict)
                    
                self.GroupStatfig.clear()
                names=samplesgroups[1:]
                if self.GroupChoice.get()=="Eff":
                    Effsubfig = self.GroupStatfig 
                    #names=samplesgroups
                    valsRev=[]
                    for item in names:
                        valsRev.append([i["RevEff"] for i in grouplistdict if i["Group"]==item and "RevEff" in i])
                    valsFor=[]
                    for item in names:
                        valsFor.append([i["ForEff"] for i in grouplistdict if i["Group"]==item and "ForEff" in i])
                    valstot=[]
                    
                    for item in names:
                        DATAgroupforexport.append([item,"RevEff"]+[i["RevEff"] for i in grouplistdict if i["Group"]==item and "RevEff" in i][0])
                        DATAgroupforexport.append([item,"ForEff"]+[i["ForEff"] for i in grouplistdict if i["Group"]==item and "ForEff" in i][0])
                    DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
    
                    Rev=[]
                    Forw=[]
                    namelist=[]
                    for i in range(len(names)):
                        if valsRev[i][0]==[] and valsFor[i][0]==[]:
                            print(" ")
                        else:
                            Rev.append(valsRev[i][0])
                            Forw.append(valsFor[i][0])
                            valstot.append(valsRev[i][0]+valsFor[i][0])
                            namelist.append(names[i])
                    if self.boxplot.get()==1:
                        Effsubfig.boxplot(valstot,0,'',labels=namelist)
                    
                    for i in range(len(namelist)):
                        y=Rev[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Effsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                        y=Forw[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Effsubfig.scatter(x,y,s=15,color='blue', alpha=0.5) 
                    if self.boxplot.get()==0:
                        span=range(1,len(namelist)+1)
                        plt.xticks(span,namelist)
                        Effsubfig.set_xlim([0.5,span[-1]+0.5])
                        
                    Effsubfig.set_ylabel('Efficiency (%)')
                    for item in ([Effsubfig.title, Effsubfig.xaxis.label, Effsubfig.yaxis.label] +
                                 Effsubfig.get_xticklabels() + Effsubfig.get_yticklabels()):
                        item.set_fontsize(fontsizegroup)
                    
                    for tick in Effsubfig.get_xticklabels():
                        tick.set_rotation(self.rotationGroupGraph.get())
                        
                elif self.GroupChoice.get()=="Voc":
                    Vocsubfig = self.GroupStatfig 
                    #names=samplesgroups
                    valsRev=[]
                    for item in names:
                        valsRev.append([i["RevVoc"] for i in grouplistdict if i["Group"]==item and "RevVoc" in i])
                    valsFor=[]
                    for item in names:
                        valsFor.append([i["ForVoc"] for i in grouplistdict if i["Group"]==item and "ForVoc" in i])
                     
                    for item in names:
                        DATAgroupforexport.append([item,"RevVoc"]+[i["RevVoc"] for i in grouplistdict if i["Group"]==item and "RevVoc" in i][0])
                        DATAgroupforexport.append([item,"ForVoc"]+[i["ForVoc"] for i in grouplistdict if i["Group"]==item and "ForVoc" in i][0])
                    DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
    
                    valstot=[]
                    Rev=[]
                    Forw=[]
                    namelist=[]
                    for i in range(len(names)):
                        if valsRev[i][0]==[] and valsFor[i][0]==[]:
                            print(" ")
                        else:
                            Rev.append(valsRev[i][0])
                            Forw.append(valsFor[i][0])
                            valstot.append(valsRev[i][0]+valsFor[i][0])
                            namelist.append(names[i])
                    
                    if self.boxplot.get()==1:
                        Vocsubfig.boxplot(valstot,0,'',labels=namelist)
                    
                    for i in range(len(namelist)):
                        y=Rev[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Vocsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                        y=Forw[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Vocsubfig.scatter(x,y,s=15,color='blue', alpha=0.5)  
                    if self.boxplot.get()==0:
                        span=range(1,len(namelist)+1)
                        plt.xticks(span,namelist)
                        Vocsubfig.set_xlim([0.5,span[-1]+0.5])
                    Vocsubfig.set_ylabel('Voc (mV)')
                    for item in ([Vocsubfig.title, Vocsubfig.xaxis.label, Vocsubfig.yaxis.label] +
                                 Vocsubfig.get_xticklabels() + Vocsubfig.get_yticklabels()):
                        item.set_fontsize(fontsizegroup)
                    for tick in Vocsubfig.get_xticklabels():
                        tick.set_rotation(self.rotationGroupGraph.get())
                        
                elif self.GroupChoice.get()=="Jsc":    
                    Jscsubfig = self.GroupStatfig 
                    #names=samplesgroups
                    valsRev=[]
                    for item in names:
                        valsRev.append([i["RevJsc"] for i in grouplistdict if i["Group"]==item and "RevJsc" in i])
                    valsFor=[]
                    for item in names:
                        valsFor.append([i["ForJsc"] for i in grouplistdict if i["Group"]==item and "ForJsc" in i])
                     
                    for item in names:
                        DATAgroupforexport.append([item,"RevJsc"]+[i["RevJsc"] for i in grouplistdict if i["Group"]==item and "RevJsc" in i][0])
                        DATAgroupforexport.append([item,"ForJsc"]+[i["ForJsc"] for i in grouplistdict if i["Group"]==item and "ForJsc" in i][0])
                    DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                    
                    valstot=[]
                    Rev=[]
                    Forw=[]
                    namelist=[]
                    for i in range(len(names)):
                        if valsRev[i][0]==[] and valsFor[i][0]==[]:
                            print(" ")
                        else:
                            Rev.append(valsRev[i][0])
                            Forw.append(valsFor[i][0])
                            valstot.append(valsRev[i][0]+valsFor[i][0])
                            namelist.append(names[i])
                    
                    if self.boxplot.get()==1:
                        Jscsubfig.boxplot(valstot,0,'',labels=namelist)
                    
                    for i in range(len(namelist)):
                        y=Rev[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Jscsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                        y=Forw[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Jscsubfig.scatter(x,y,s=15,color='blue', alpha=0.5)  
                    if self.boxplot.get()==0:
                        span=range(1,len(namelist)+1)
                        plt.xticks(span,namelist)
                        Jscsubfig.set_xlim([0.5,span[-1]+0.5])
                    Jscsubfig.set_ylabel('Jsc (mA/cm'+'\xb2'+')')
                    for item in ([Jscsubfig.title, Jscsubfig.xaxis.label, Jscsubfig.yaxis.label] +
                                 Jscsubfig.get_xticklabels() + Jscsubfig.get_yticklabels()):
                        item.set_fontsize(fontsizegroup)
                    for tick in Jscsubfig.get_xticklabels():
                        tick.set_rotation(self.rotationGroupGraph.get())
                        
                elif self.GroupChoice.get()=="FF":
                    FFsubfig = self.GroupStatfig 
                    #names=samplesgroups
                    valsRev=[]
                    for item in names:
                        valsRev.append([i["RevFF"] for i in grouplistdict if i["Group"]==item and "RevFF" in i])
                    valsFor=[]
                    for item in names:
                        valsFor.append([i["ForFF"] for i in grouplistdict if i["Group"]==item and "ForFF" in i])
                    
                    for item in names:
                        DATAgroupforexport.append([item,"RevFF"]+[i["RevFF"] for i in grouplistdict if i["Group"]==item and "RevFF" in i][0])
                        DATAgroupforexport.append([item,"ForFF"]+[i["ForFF"] for i in grouplistdict if i["Group"]==item and "ForFF" in i][0])
                    DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                    
                    valstot=[]
                    Rev=[]
                    Forw=[]
                    namelist=[]
                    for i in range(len(names)):
                        if valsRev[i][0]==[] and valsFor[i][0]==[]:
                            print(" ")
                        else:
                            Rev.append(valsRev[i][0])
                            Forw.append(valsFor[i][0])
                            valstot.append(valsRev[i][0]+valsFor[i][0])
                            namelist.append(names[i])
                    
                    if self.boxplot.get()==1:
                        FFsubfig.boxplot(valstot,0,'',labels=namelist)
                    
                    for i in range(len(namelist)):
                        y=Rev[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            FFsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                        y=Forw[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            FFsubfig.scatter(x,y,s=15,color='blue', alpha=0.5)  
                    if self.boxplot.get()==0:
                        span=range(1,len(namelist)+1)
                        plt.xticks(span,namelist)
                        FFsubfig.set_xlim([0.5,span[-1]+0.5])
                    FFsubfig.set_ylabel('FF (%)')
                    for item in ([FFsubfig.title, FFsubfig.xaxis.label, FFsubfig.yaxis.label] +
                                 FFsubfig.get_xticklabels() + FFsubfig.get_yticklabels()):
                        item.set_fontsize(fontsizegroup)
                    for tick in FFsubfig.get_xticklabels():
                        tick.set_rotation(self.rotationGroupGraph.get())
                        
                elif self.GroupChoice.get()=="Roc":
                    Rocsubfig = self.GroupStatfig 
                    #names=samplesgroups
                    valsRev=[]
                    for item in names:
                        valsRev.append([i["RevRoc"] for i in grouplistdict if i["Group"]==item and "RevRoc" in i])
                    valsFor=[]
                    for item in names:
                        valsFor.append([i["ForRoc"] for i in grouplistdict if i["Group"]==item and "ForRoc" in i])
                     
                    for item in names:
                        DATAgroupforexport.append([item,"RevRoc"]+[i["RevRoc"] for i in grouplistdict if i["Group"]==item and "RevRoc" in i][0])
                        DATAgroupforexport.append([item,"ForRoc"]+[i["ForRoc"] for i in grouplistdict if i["Group"]==item and "ForRoc" in i][0])
                    DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                    
                    valstot=[]
                    Rev=[]
                    Forw=[]
                    namelist=[]
                    for i in range(len(names)):
                        if valsRev[i][0]==[] and valsFor[i][0]==[]:
                            print(" ")
                        else:
                            Rev.append(valsRev[i][0])
                            Forw.append(valsFor[i][0])
                            valstot.append(valsRev[i][0]+valsFor[i][0])
                            namelist.append(names[i])
                    
                    if self.boxplot.get()==1:
                        Rocsubfig.boxplot(valstot,0,'',labels=namelist)
                    
                    for i in range(len(namelist)):
                        y=Rev[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Rocsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                        y=Forw[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Rocsubfig.scatter(x,y,s=15,color='blue', alpha=0.5)  
                    if self.boxplot.get()==0:
                        span=range(1,len(namelist)+1)
                        plt.xticks(span,namelist)
                        Rocsubfig.set_xlim([0.5,span[-1]+0.5])
                    Rocsubfig.set_ylabel('Roc')
                    for item in ([Rocsubfig.title, Rocsubfig.xaxis.label, Rocsubfig.yaxis.label] +
                                 Rocsubfig.get_xticklabels() + Rocsubfig.get_yticklabels()):
                        item.set_fontsize(fontsizegroup)
                    for tick in Rocsubfig.get_xticklabels():
                        tick.set_rotation(self.rotationGroupGraph.get())
                        
                elif self.GroupChoice.get()=="Rsc":
                    Rscsubfig = self.GroupStatfig 
                    #names=samplesgroups
                    valsRev=[]
                    for item in names:
                        valsRev.append([i["RevRsc"] for i in grouplistdict if i["Group"]==item and "RevRsc" in i])
                    valsFor=[]
                    for item in names:
                        valsFor.append([i["ForRsc"] for i in grouplistdict if i["Group"]==item and "ForRsc" in i])
                    
                    for item in names:
                        DATAgroupforexport.append([item,"RevRsc"]+[i["RevRsc"] for i in grouplistdict if i["Group"]==item and "RevRsc" in i][0])
                        DATAgroupforexport.append([item,"ForRsc"]+[i["ForRsc"] for i in grouplistdict if i["Group"]==item and "ForRsc" in i][0])
                    DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                    
                    valstot=[]
                    Rev=[]
                    Forw=[]
                    namelist=[]
                    for i in range(len(names)):
                        if valsRev[i][0]==[] and valsFor[i][0]==[]:
                            print(" ")
                        else:
                            Rev.append(valsRev[i][0])
                            Forw.append(valsFor[i][0])
                            valstot.append(valsRev[i][0]+valsFor[i][0])
                            namelist.append(names[i])
                    
                    if self.boxplot.get()==1:
                        Rscsubfig.boxplot(valstot,0,'',labels=namelist)
                    
                    for i in range(len(namelist)):
                        y=Rev[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Rscsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                        y=Forw[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Rscsubfig.scatter(x,y,s=15,color='blue', alpha=0.5)  
                    if self.boxplot.get()==0:
                        span=range(1,len(namelist)+1)
                        plt.xticks(span,namelist)
                        Rscsubfig.set_xlim([0.5,span[-1]+0.5])
                    Rscsubfig.set_ylabel('Rsc')
                    for item in ([Rscsubfig.title, Rscsubfig.xaxis.label, Rscsubfig.yaxis.label] +
                                 Rscsubfig.get_xticklabels() + Rscsubfig.get_yticklabels()):
                        item.set_fontsize(fontsizegroup)
                    for tick in Rscsubfig.get_xticklabels():
                        tick.set_rotation(self.rotationGroupGraph.get())
                        
                elif self.GroupChoice.get()=="Vmpp":
                    Rscsubfig = self.GroupStatfig 
                    #names=samplesgroups
                    valsRev=[]
                    for item in names:
                        valsRev.append([i["RevVmpp"] for i in grouplistdict if i["Group"]==item and "RevVmpp" in i])
                    valsFor=[]
                    for item in names:
                        valsFor.append([i["ForVmpp"] for i in grouplistdict if i["Group"]==item and "ForVmpp" in i])
                     
                    for item in names:
                        DATAgroupforexport.append([item,"RevVmpp"]+[i["RevVmpp"] for i in grouplistdict if i["Group"]==item and "RevVmpp" in i][0])
                        DATAgroupforexport.append([item,"ForVmpp"]+[i["ForVmpp"] for i in grouplistdict if i["Group"]==item and "ForVmpp" in i][0])
                    DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                    
                    valstot=[]
                    Rev=[]
                    Forw=[]
                    namelist=[]
                    for i in range(len(names)):
                        if valsRev[i][0]==[] and valsFor[i][0]==[]:
                            print(" ")
                        else:
                            Rev.append(valsRev[i][0])
                            Forw.append(valsFor[i][0])
                            valstot.append(valsRev[i][0]+valsFor[i][0])
                            namelist.append(names[i])
                    
                    if self.boxplot.get()==1:
                        Rscsubfig.boxplot(valstot,0,'',labels=namelist)
                    
                    for i in range(len(namelist)):
                        y=Rev[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Rscsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                        y=Forw[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Rscsubfig.scatter(x,y,s=15,color='blue', alpha=0.5)  
                    if self.boxplot.get()==0:
                        span=range(1,len(namelist)+1)
                        plt.xticks(span,namelist)
                        Rscsubfig.set_xlim([0.5,span[-1]+0.5])
                    Rscsubfig.set_ylabel('Vmpp (mV)')
                    for item in ([Rscsubfig.title, Rscsubfig.xaxis.label, Rscsubfig.yaxis.label] +
                                 Rscsubfig.get_xticklabels() + Rscsubfig.get_yticklabels()):
                        item.set_fontsize(fontsizegroup) 
                    for tick in Rscsubfig.get_xticklabels():
                        tick.set_rotation(self.rotationGroupGraph.get())
                        
                elif self.GroupChoice.get()=="Jmpp":
                    Rscsubfig = self.GroupStatfig 
                    #names=samplesgroups
                    valsRev=[]
                    for item in names:
                        valsRev.append([i["RevJmpp"] for i in grouplistdict if i["Group"]==item and "RevJmpp" in i])
                    valsFor=[]
                    for item in names:
                        valsFor.append([i["ForJmpp"] for i in grouplistdict if i["Group"]==item and "ForJmpp" in i])
                     
                    for item in names:
                        DATAgroupforexport.append([item,"RevJmpp"]+[i["RevJmpp"] for i in grouplistdict if i["Group"]==item and "RevJmpp" in i][0])
                        DATAgroupforexport.append([item,"ForJmpp"]+[i["ForJmpp"] for i in grouplistdict if i["Group"]==item and "ForJmpp" in i][0])
                    DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                    
                    valstot=[]
                    Rev=[]
                    Forw=[]
                    namelist=[]
                    for i in range(len(names)):
                        if valsRev[i][0]==[] and valsFor[i][0]==[]:
                            print(" ")
                        else:
                            Rev.append(valsRev[i][0])
                            Forw.append(valsFor[i][0])
                            valstot.append(valsRev[i][0]+valsFor[i][0])
                            namelist.append(names[i])
                    
                    if self.boxplot.get()==1:
                        Rscsubfig.boxplot(valstot,0,'',labels=namelist)
                    
                    for i in range(len(namelist)):
                        y=Rev[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Rscsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                        y=Forw[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Rscsubfig.scatter(x,y,s=15,color='blue', alpha=0.5)  
                    if self.boxplot.get()==0:
                        span=range(1,len(namelist)+1)
                        plt.xticks(span,namelist)
                        Rscsubfig.set_xlim([0.5,span[-1]+0.5])
                    Rscsubfig.set_ylabel('Jmpp (mA/cm'+'\xb2'+')')
                    for item in ([Rscsubfig.title, Rscsubfig.xaxis.label, Rscsubfig.yaxis.label] +
                                 Rscsubfig.get_xticklabels() + Rscsubfig.get_yticklabels()):
                        item.set_fontsize(fontsizegroup)    
                    for tick in Rscsubfig.get_xticklabels():
                        tick.set_rotation(self.rotationGroupGraph.get())
                
                    
                self.GroupStatfig.annotate('Red=reverse; Blue=forward', xy=(0.7,1.05), xycoords='axes fraction', fontsize=7,
                            horizontalalignment='right', verticalalignment='bottom')
    
                plt.gcf().canvas.draw()
        except:
            pass
    
    def UpdateIVGraph(self):
        global DATA
        global IVlegendMod
        global titIV
        global DATAJVforexport
        global DATAJVtabforexport
        global takenforplot
        global IVlinestyle
        global colorstylelist
        #csfont = {'fontname':'Helvetica'}
        
        DATAJVforexport=[]
        DATAJVtabforexport=[]
        
        DATAx=copy.deepcopy(DATA)
        sampletotake=[]
        if takenforplot!=[]:
            for item in takenforplot:
                for item1 in range(len(DATAx)):
                    if item ==DATAx[item1]["SampleName"]:
                        sampletotake.append(item1)
                        break
        if self.CheckIVLog.get()!=1:
            if IVlegendMod!=[]:
                self.IVsubfig.clear()
                IVfig=self.IVsubfig
                color1=0
                for item in sampletotake:
                    x = DATAx[item]["IVData"][0]
                    y = DATAx[item]["IVData"][1]
                    
                    colx=["Voltage","mV",""]+x
                    coly=["Current density","ma/cm2",DATAx[item]["SampleName"]]+y
                    DATAJVforexport.append(colx)
                    DATAJVforexport.append(coly)
                    DATAJVtabforexport.append([DATAx[item]["SampleName"],'%.f' % float(DATAx[item]["Voc"]),'%.2f' % float(DATAx[item]["Jsc"]),'%.2f' % float(DATAx[item]["FF"]),'%.2f' % float(DATAx[item]["Eff"]),'%.2f' % float(DATAx[item]["Roc"]),'%.2f' % float(DATAx[item]["Rsc"]),'%.2f' % float(DATAx[item]["Vstart"]),'%.2f' % float(DATAx[item]["Vend"]),'%.2f' % float(DATAx[item]["CellSurface"])])
    
                    if self.CheckIVLegend.get()==1:
                        newlegend=1
                        for item1 in range(len(IVlegendMod)):
                            if IVlegendMod[item1][0]==DATAx[item]["SampleName"]:
                                try:
                                    IVfig.plot(x,y,label=IVlegendMod[item1][1],linestyle=IVlinestyle[item1][1],color=IVlinestyle[item1][2])
                                except IndexError:
                                    print("some indexerror... but just continue...")
                                newlegend=0
                                break
                        if newlegend:
                            try:
                                IVfig.plot(x,y,label=DATAx[item]["SampleName"],linestyle=IVlinestyle[item1][1],color=IVlinestyle[item1][2])
                                IVlegendMod.append([DATAx[item]["SampleName"],DATAx[item]["SampleName"]])
                                IVlinestyle.append([DATAx[item]["SampleName"],"-",colorstylelist[color1]])
                            except IndexError:
                                print("some indexerror... but just continue...")
                    else:
                        IVfig.plot(x,y,color=colorstylelist[color1])
                    color1=color1+1
            else:
                self.IVsubfig.clear()
                IVfig=self.IVsubfig
                color1=0
                for item in sampletotake:
                    x = DATAx[item]["IVData"][0]
                    y = DATAx[item]["IVData"][1]
                    
                    colx=["Voltage","mV",""]+x
                    coly=["Current density","ma/cm^2",DATAx[item]["SampleName"]]+y
                    DATAJVforexport.append(colx)
                    DATAJVforexport.append(coly)
                    DATAJVtabforexport.append([DATAx[item]["SampleName"],'%.f' % float(DATAx[item]["Voc"]),'%.2f' % float(DATAx[item]["Jsc"]),'%.2f' % float(DATAx[item]["FF"]),'%.2f' % float(DATAx[item]["Eff"]),'%.2f' % float(DATAx[item]["Roc"]),'%.2f' % float(DATAx[item]["Rsc"]),'%.2f' % float(DATAx[item]["Vstart"]),'%.2f' % float(DATAx[item]["Vend"]),'%.2f' % float(DATAx[item]["CellSurface"])])
    
                    
                    if self.CheckIVLegend.get()==1:
                        try:
                            IVfig.plot(x,y,label=DATAx[item]["SampleName"],color=colorstylelist[color1])
                            IVlegendMod.append([DATAx[item]["SampleName"],DATAx[item]["SampleName"]])
                            IVlinestyle.append([DATAx[item]["SampleName"],"-",colorstylelist[color1]])
                        except IndexError:
                            print("some indexerror... but just continue...")
                    else:
                        try:
                            IVfig.plot(x,y,color=colorstylelist[color1])
                        except IndexError:
                            print("some indexerror... but just continue...")
                    color1=color1+1
            
            self.IVsubfig.set_xlabel('Voltage (V)')#,**csfont)
            self.IVsubfig.set_ylabel('Current density (mA/cm'+'\xb2'+')')#,**csfont)
            self.IVsubfig.axhline(y=0, color='k')
            self.IVsubfig.axvline(x=0, color='k')
            self.IVsubfig.axis([self.IVminx.get(),self.IVmaxx.get(),self.IVminy.get(),self.IVmaxy.get()])
        else:
            if IVlegendMod!=[]:
                self.IVsubfig.clear()
                IVfig=self.IVsubfig
                color1=0
                for item in sampletotake:
                    x = DATAx[item]["IVData"][0]
                    y = DATAx[item]["IVData"][1]
                    y=[abs(item) for item in y]
                    
                    colx=["Voltage","mV",""]+x
                    coly=["Current density","ma/cm2",DATAx[item]["SampleName"]]+y
                    DATAJVforexport.append(colx)
                    DATAJVforexport.append(coly)
                    DATAJVtabforexport.append([DATAx[item]["SampleName"],'%.f' % float(DATAx[item]["Voc"]),'%.2f' % float(DATAx[item]["Jsc"]),'%.2f' % float(DATAx[item]["FF"]),'%.2f' % float(DATAx[item]["Eff"]),'%.2f' % float(DATAx[item]["Roc"]),'%.2f' % float(DATAx[item]["Rsc"]),'%.2f' % float(DATAx[item]["Vstart"]),'%.2f' % float(DATAx[item]["Vend"]),'%.2f' % float(DATAx[item]["CellSurface"])])
    
                    if self.CheckIVLegend.get()==1:
                        newlegend=1
                        for item1 in range(len(IVlegendMod)):
                            if IVlegendMod[item1][0]==DATAx[item]["SampleName"]:
                                try:
                                    IVfig.semilogy(x,y,label=IVlegendMod[item1][1],linestyle=IVlinestyle[item1][1],color=IVlinestyle[item1][2])
                                except IndexError:
                                    print("some indexerror... but just continue...")
                                newlegend=0
                                break
                        if newlegend:
                            try:
                                IVfig.semilogy(x,y,label=DATAx[item]["SampleName"],linestyle=IVlinestyle[item1][1],color=IVlinestyle[item1][2])
                                IVlegendMod.append([DATAx[item]["SampleName"],DATAx[item]["SampleName"]])
                                IVlinestyle.append([DATAx[item]["SampleName"],"-",colorstylelist[color1]])
                            except IndexError:
                                print("some indexerror... but just continue...")
                    else:
                        IVfig.semilogy(x,y,color=colorstylelist[color1])
                    color1=color1+1
            else:
                self.IVsubfig.clear()
                IVfig=self.IVsubfig
                color1=0
                for item in sampletotake:
                    x = DATAx[item]["IVData"][0]
                    y = DATAx[item]["IVData"][1]
                    y=[abs(item) for item in y]
                    
                    colx=["Voltage","mV",""]+x
                    coly=["Current density","ma/cm^2",DATAx[item]["SampleName"]]+y
                    DATAJVforexport.append(colx)
                    DATAJVforexport.append(coly)
                    DATAJVtabforexport.append([DATAx[item]["SampleName"],'%.f' % float(DATAx[item]["Voc"]),'%.2f' % float(DATAx[item]["Jsc"]),'%.2f' % float(DATAx[item]["FF"]),'%.2f' % float(DATAx[item]["Eff"]),'%.2f' % float(DATAx[item]["Roc"]),'%.2f' % float(DATAx[item]["Rsc"]),'%.2f' % float(DATAx[item]["Vstart"]),'%.2f' % float(DATAx[item]["Vend"]),'%.2f' % float(DATAx[item]["CellSurface"])])
    
                    
                    if self.CheckIVLegend.get()==1:
                        try:
                            IVfig.semilogy(x,y,label=DATAx[item]["SampleName"],color=colorstylelist[color1])
                            IVlegendMod.append([DATAx[item]["SampleName"],DATAx[item]["SampleName"]])
                            IVlinestyle.append([DATAx[item]["SampleName"],"-",colorstylelist[color1]])
                        except IndexError:
                            print("some indexerror... but just continue...")
                    else:
                        try:
                            IVfig.semilogy(x,y,color=colorstylelist[color1])
                        except IndexError:
                            print("some indexerror... but just continue...")
                    color1=color1+1
            
            self.IVsubfig.set_xlabel('Voltage (V)')#,**csfont)
            self.IVsubfig.set_ylabel('Current density (mA/cm'+'\xb2'+')')#,**csfont)
            self.IVsubfig.axhline(y=0, color='k')
            self.IVsubfig.axvline(x=0, color='k')  
            self.IVsubfig.axis([self.IVminx.get(),self.IVmaxx.get(),0,self.IVmaxy.get()])
            
            
        DATAJVforexport=map(list, six.moves.zip_longest(*DATAJVforexport, fillvalue=' '))
        DATAJVtabforexport.insert(0,[" ","Voc", "Jsc", "FF","Eff","Roc","Rsc","Vstart","Vend","Cellsurface"])

        if titIV:
            self.IVsubfig.set_title(self.titleIV.get())#,**csfont)
        
        if self.CheckIVLegend.get()==1:
            if self.IVlegpos1.get()==1:
                self.leg=IVfig.legend(loc=self.IVlegpos1.get())
            elif self.IVlegpos1.get()==2:
                self.leg=IVfig.legend(loc=self.IVlegpos1.get())
            elif self.IVlegpos1.get()==3:
                self.leg=IVfig.legend(loc=self.IVlegpos1.get())
            elif self.IVlegpos1.get()==4:
                self.leg=IVfig.legend(loc=self.IVlegpos1.get())
            elif self.IVlegpos1.get()==5:
                self.leg=IVfig.legend(bbox_to_anchor=(1, 1), loc='upper left', ncol=1)
            else:
                self.leg=IVfig.legend(loc=0)
        
        plt.gcf().canvas.draw()
    
    def UpdateMppGraph0(self):
        global takenforplotmpp
        global MPPlinestyle
        global MPPlegendMod
        global colorstylelist
        
        takenforplotmpp=[]
        for name, var in self.choicesmpp.items():
            takenforplotmpp.append(var.get())
        m=[]
        for i in range(len(takenforplotmpp)):
            if takenforplotmpp[i]==1:
                m.append(self.mppnames[i])
        takenforplotmpp=m
        if MPPlegendMod!=[]:
            for item in takenforplotmpp:
                founded=0
                for item1 in MPPlegendMod:
                    if item1[0]==item:
                        founded=1
                if founded==0:
                    MPPlegendMod.append([item,item])
                    MPPlinestyle.append([item,"-",colorstylelist[len(MPPlegendMod)]])
            
        self.UpdateMppGraph()
        
    def UpdateMppGraph(self):
        global DATAMPP
        global MPPlegendMod
        global titmpp
        global MPPlinestyle
        global colorstylelist
        global DATAmppforexport
        global takenforplotmpp
        
        DATAmppforexport=[]
        
        DATAx=copy.deepcopy(DATAMPP)
        
        
        sampletotake=[]
        if takenforplotmpp!=[]:
            for item in takenforplotmpp:
                for item1 in range(len(DATAx)):
                    if item ==DATAx[item1]["SampleName"]:
                        sampletotake.append(item1)
                        break
        
        if MPPlegendMod!=[]:
            self.mppsubfig.clear()
            mppfig=self.mppsubfig
            color=0
            for item in sampletotake:
                x = DATAx[item]["MppData"][2]
                y = DATAx[item]["MppData"][3]
                
                colx=["Time","s",""]+x
                coly=["Power","mW/cm2",DATAx[item]["SampleName"]]+y
                DATAmppforexport.append(colx)
                DATAmppforexport.append(coly)
                
                if self.CheckmppLegend.get()==1:
                    newlegend=1
                    for item1 in range(len(MPPlegendMod)):
                        if MPPlegendMod[item1][0]==DATAx[item]["SampleName"]:
                            mppfig.plot(x,y,label=MPPlegendMod[item1][1],linestyle=MPPlinestyle[item1][1],color=MPPlinestyle[item1][2])
                            newlegend=0
                            break
                    if newlegend:
                        mppfig.plot(x,y,label=DATAx[item]["SampleName"],linestyle=MPPlinestyle[item][1],color=MPPlinestyle[item][2])
                        MPPlegendMod.append([DATAx[item]["SampleName"],DATAx[item]["SampleName"]])
                        MPPlinestyle.append([DATAx[item]["SampleName"],"-",colorstylelist[color]])
                else:
                    mppfig.plot(x,y)
                color=color+1
        else:
            self.mppsubfig.clear()
            mppfig=self.mppsubfig
            color=0
            for i in range(len(sampletotake)):
                x = DATAx[sampletotake[i]]["MppData"][2]
                y = DATAx[sampletotake[i]]["MppData"][3]
                if self.CheckmppLegend.get()==1:
                    mppfig.plot(x,y,label=DATAx[sampletotake[i]]["SampleName"],color=colorstylelist[color])
                    MPPlegendMod.append([DATAx[sampletotake[i]]["SampleName"],DATAx[sampletotake[i]]["SampleName"]])
                    MPPlinestyle.append([DATAx[sampletotake[i]]["SampleName"],"-",colorstylelist[color]])
                else:
                    mppfig.plot(x,y,color=colorstylelist[color])
                color=color+1
        
        self.mppsubfig.set_ylabel('Power (mW/cm'+'\xb2'+')')
        self.mppsubfig.set_xlabel('Time (s)')
        
        if titmpp:
            self.mppsubfig.set_title(self.titlempp.get())
        
        if self.CheckmppLegend.get()==1:
            if self.mpplegpos1.get()==1:
                self.leg=mppfig.legend(loc=self.mpplegpos1.get())
            elif self.mpplegpos1.get()==2:
                self.leg=mppfig.legend(loc=self.mpplegpos1.get())
            elif self.mpplegpos1.get()==3:
                self.leg=mppfig.legend(loc=self.mpplegpos1.get())
            elif self.mpplegpos1.get()==4:
                self.leg=mppfig.legend(loc=self.mpplegpos1.get())
            elif self.mpplegpos1.get()==5:
                self.leg=mppfig.legend(bbox_to_anchor=(1, 1), loc='upper left', ncol=1)
            else:
                self.leg=mppfig.legend(loc=0)
        
        DATAmppforexport=map(list, six.moves.zip_longest(*DATAmppforexport, fillvalue=' '))

        self.mppsubfig.axis([self.mppminx.get(),self.mppmaxx.get(),self.mppminy.get(),self.mppmaxy.get()])
        plt.gcf().canvas.draw()

#%%######################################################################
        
    def getdatalistsfromIVHITfiles(self, file_path):
        print("importing HIT iv files")
        global DATA
        for k in range(len(file_path)):
            print(k)
            wb = xlrd.open_workbook(file_path[k])
            sheet_names = wb.sheet_names()
            for j in range(len(sheet_names)):
                partdict={}
                if 'Sheet' not in sheet_names[j]:
                    xlsheet = wb.sheet_by_index(j)
                    if xlsheet.cell(13,0).value=="Number of points":#epfl hit iv files
                        #AllNames.append(sheet_names[j])
                        partdict["SampleName"]=sheet_names[j]
                        print(partdict["SampleName"])
                        partdict["SampleName"]=partdict["SampleName"].replace("-","_")
                        partdict["DepID"]=partdict["SampleName"]
                        partdict["Cellletter"]='SingleEPFL'
                        partdict["CellNumber"]=4
                        
                        partdict["MeasDayTime"] = xlsheet.cell(0,0).value
                        partdict["CellSurface"]=xlsheet.cell(5,1).value
                        partdict["MeasComment"]=str(xlsheet.cell(6,1).value)
                          
                        partdict["ImaxComp"]=float(xlsheet.cell(9,1).value)
                        partdict["Isenserange"]=str(xlsheet.cell(10,1).value)
                        partdict["Vstart"]=float(xlsheet.cell(11,1).value)
                        partdict["Vend"]=float(xlsheet.cell(12,1).value)
                        partdict["NbPoints"]=float(xlsheet.cell(13,1).value)
                        partdict["Delay"]=float(xlsheet.cell(14,1).value)
                        partdict["IntegTime"]=float(xlsheet.cell(15,1).value)
                        
                        partdict["Operator"]=str(xlsheet.cell(3,1).value)
                        
                        partdict["RefNomCurr"]=float(xlsheet.cell(22,1).value)
                        partdict["RefMeasCurr"]=float(xlsheet.cell(23,1).value)
                        partdict["AirTemp"]=float(xlsheet.cell(26,1).value)
                        partdict["ChuckTemp"]=str(xlsheet.cell(27,1).value)
                        partdict["Illumination"]="Light"
                        partdict["Setup"]="HIT"
                        corrlign=0
                        partdict["Eff"]=float(xlsheet.cell(35-corrlign,1).value)
                        partdict["Voc"]=float(xlsheet.cell(35-corrlign,2).value)
                        partdict["Jsc"]=float(xlsheet.cell(35-corrlign,3).value)
                        partdict["FF"]=float(xlsheet.cell(35-corrlign,4).value)
                        partdict["Vmpp"]=float(xlsheet.cell(35-corrlign,5).value)
                        partdict["Jmpp"]=float(xlsheet.cell(35-corrlign,6).value)
                        partdict["Pmpp"]=float(xlsheet.cell(35-corrlign,7).value)
                        partdict["Rsc"]=float(xlsheet.cell(35-corrlign,8).value)
                        partdict["Roc"]=float(xlsheet.cell(35-corrlign,9).value)
                        partdict["VocFF"]=partdict["Voc"]*partdict["FF"]
                        partdict["RscJsc"]=partdict["Rsc"]*partdict["Jsc"]
                        
                        if abs(float(partdict["Vstart"]))>abs(float(partdict["Vend"])):
                            partdict["ScanDirection"]="Reverse"
                        else:
                            partdict["ScanDirection"]="Forward"
                        partdict["Group"]="Default group"
                        ivpartdat = [[],[]]#[voltage,current]
                        for item in range(37-corrlign,36-corrlign+int(partdict["NbPoints"]),1):
                            ivpartdat[0].append(float(xlsheet.cell(item,3).value))
                            ivpartdat[1].append(1000*float(xlsheet.cell(item,4).value)/partdict["CellSurface"])
                        partdict["IVData"]=ivpartdat
                        try:
                            if partdict["Illumination"]=="Light" and max(ivpartdat[0])>0.001*float(partdict["Voc"]):
                                f = interp1d(ivpartdat[0], ivpartdat[1], kind='cubic')
                                x2 = lambda x: f(x)
                                partdict["AreaJV"] = integrate.quad(x2,0,0.001*float(partdict["Voc"]))[0]
                            else:
                                partdict["AreaJV"] =""
                        except ValueError:
                            print("there is a ValueError on sample ",k)
                        
                        DATA.append(partdict)
                    elif xlsheet.cell(13,0).value=="Vend:":#CSEM iv files
                        #AllNames.append(sheet_names[j])
                        partdict["SampleName"]=sheet_names[j]
                        print(partdict["SampleName"])
                        partdict["SampleName"]=partdict["SampleName"].replace("-","_")
                        partdict["DepID"]=partdict["SampleName"]
                        partdict["Cellletter"]='SingleCSEM'
                        partdict["CellNumber"]=4
                        
                        partdict["MeasDayTime"] = xlsheet.cell(0,0).value
                        partdict["CellSurface"]=xlsheet.cell(5,1).value
                        partdict["MeasComment"]=str(xlsheet.cell(6,1).value)
                          
                        partdict["ImaxComp"]=""
                        partdict["Isenserange"]=str(xlsheet.cell(9,1).value)
                        partdict["Vstart"]=float(xlsheet.cell(12,1).value)
                        partdict["Vend"]=float(xlsheet.cell(13,1).value)
                        partdict["NbPoints"]=abs(partdict["Vend"]-partdict["Vstart"])/float(xlsheet.cell(10,1).value)
                        partdict["Delay"]=float(xlsheet.cell(14,1).value)
                        partdict["IntegTime"]=float(xlsheet.cell(15,1).value)
                        
                        partdict["Operator"]=str(xlsheet.cell(3,1).value)
                        
                        partdict["RefNomCurr"]=float(xlsheet.cell(22,1).value)
                        partdict["RefMeasCurr"]=float(xlsheet.cell(23,1).value)
                        partdict["AirTemp"]=float(xlsheet.cell(26,1).value)
                        partdict["ChuckTemp"]=str(xlsheet.cell(27,1).value)
                        partdict["Illumination"]="Light"
                        partdict["Setup"]="HIT"
                        corrlign=1    
                        partdict["Eff"]=float(xlsheet.cell(35-corrlign,1).value)
                        partdict["Voc"]=float(xlsheet.cell(35-corrlign,2).value)
                        partdict["Jsc"]=float(xlsheet.cell(35-corrlign,3).value)
                        partdict["FF"]=float(xlsheet.cell(35-corrlign,4).value)
                        partdict["Vmpp"]=float(xlsheet.cell(35-corrlign,5).value)
                        partdict["Jmpp"]=float(xlsheet.cell(35-corrlign,6).value)
                        partdict["Pmpp"]=float(xlsheet.cell(35-corrlign,7).value)
                        partdict["Rsc"]=float(xlsheet.cell(35-corrlign,8).value)
                        partdict["Roc"]=float(xlsheet.cell(35-corrlign,9).value)
                        partdict["VocFF"]=partdict["Voc"]*partdict["FF"]
                        partdict["RscJsc"]=partdict["Rsc"]*partdict["Jsc"]
                        
                        if abs(float(partdict["Vstart"]))>abs(float(partdict["Vend"])):
                            partdict["ScanDirection"]="Reverse"
                        else:
                            partdict["ScanDirection"]="Forward"
                        partdict["Group"]="Default group"
                        ivpartdat = [[],[]]#[voltage,current]
                        for item in range(37,36+int(partdict["NbPoints"]),1):
                            ivpartdat[0].append(float(xlsheet.cell(item,3).value))
                            ivpartdat[1].append(1000*float(xlsheet.cell(item,4).value)/partdict["CellSurface"])
                        partdict["IVData"]=ivpartdat
                        try:
                            if partdict["Illumination"]=="Light" and max(ivpartdat[0])>0.001*float(partdict["Voc"]):
                                f = interp1d(ivpartdat[0], ivpartdat[1], kind='cubic')
                                x2 = lambda x: f(x)
                                partdict["AreaJV"] = integrate.quad(x2,0,0.001*float(partdict["Voc"]))[0]
                            else:
                                partdict["AreaJV"] =""
                        except ValueError:
                            print("there is a ValueError on sample ",k)
                        
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
        
    def getdatalistsfromIVTFfiles(self, file_path):
        global DATA
        global DATAdark
        global DATAMPP
        global DATAFV
        
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
                elif "Mpp tracker" in filerawdata[item0]:
#                    for item1 in range(len(filerawdata)):
#                        if "% MEASURED Pmpptracker" in filerawdata[item0]:
                    filetype = 3
                    break
                elif "Fixed voltage" in filerawdata[item0]:
                    filetype = 4
                    break
                                
            if filetype ==1 or filetype==2: #J-V files and FRLOOP
                partdict = {}
                partdict["filepath"]=file_path[i]
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
                
                if partdict["Illumination"]=="Light":
                    DATA.append(partdict)
                else:
                    DATAdark.append(partdict)
                        
            elif filetype==3: #Mpp files
                partdict = {}
                partdict["filepath"]=file_path[i]
                partdict["MeasComment"]="-"
                for item in range(len(filerawdata)):
                    if "Measurement comment:" in filerawdata[item]:
                        partdict["MeasComment"]=filerawdata[item][21:-1]
                        break
                for item in range(len(filerawdata)):
                    if "Deposition ID:" in filerawdata[item]:
                        partdict["SampleName"]=filerawdata[item][15:-1]+"_"+filerawdata[item-1][19:-1]
                        partdict["DepID"]=filerawdata[item][15:-1]
                        partdict["DepID"]=partdict["DepID"].replace("-","_")
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
                    if "IV measurement time:" in filerawdata[item]:
                        partdict["MeasDayTime"]=filerawdata[item][22:-1]
                        break
                for item in range(len(filerawdata)):
                    if "Cell size [m2]:" in filerawdata[item]:
                        partdict["CellSurface"]=filerawdata[item][17:-1]
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
                    if "Vstep:" in filerawdata[item]:
                        partdict["Vstep"]=str(float(filerawdata[item][7:-1]))
                        break
                for item in range(len(filerawdata)):
                    if "Vstart:" in filerawdata[item]:
                        partdict["Vstart"]=str(float(filerawdata[item][7:-1]))
                        break
                for item in range(len(filerawdata)):
                    if "Vend:" in filerawdata[item]:
                        partdict["Vend"]=str(float(filerawdata[item][5:-1]))
                        break
                for item in range(len(filerawdata)):
                    if "Execution time:" in filerawdata[item]:
                        partdict["ExecTime"]=str(float(filerawdata[item][16:-1]))
                        break
                for item in range(len(filerawdata)):
                    if "User name:" in filerawdata[item]:
                        partdict["Operator"]=filerawdata[item][11:-1]
                        break
                for item in range(len(filerawdata)):
                    if "MEASURED Pmpptracker" in filerawdata[item]:
                        pos=item+2
                        break
                partdict["Group"]="Default group"
                mpppartdat = [[],[],[],[],[]]#[voltage,current,time,power,vstep]
                for item in range(pos,len(filerawdata),1):
                    mpppartdat[0].append(float(filerawdata[item].split("\t")[0]))
                    mpppartdat[1].append(float(filerawdata[item].split("\t")[1]))
                    mpppartdat[2].append(float(filerawdata[item].split("\t")[2]))
                    mpppartdat[3].append(float(filerawdata[item].split("\t")[3]))
                    mpppartdat[4].append(float(filerawdata[item].split("\t")[4]))
                partdict["PowerEnd"]=mpppartdat[3][-1]
                partdict["PowerAvg"]=sum(mpppartdat[3])/float(len(mpppartdat[3]))
                partdict["trackingduration"]=mpppartdat[2][-1]
                partdict["MppData"]=mpppartdat
                DATAMPP.append(partdict)
        
        
            elif filetype==4: #FV files
                partdict = {}
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
                            partdict["SampleName"]=filerawdata[item][15:-1]+"_"+filerawdata[item-1][19:-1]
                        partdict["DepID"]=filerawdata[item][15:-1]
                        break
                for item in range(len(filerawdata)):
                    if "IV measurement time:" in filerawdata[item]:
                        partdict["MeasDayTime"]=filerawdata[item][22:-1]
                        break
                for item in range(len(filerawdata)):
                    if "Cell size [m2]:" in filerawdata[item]:
                        partdict["CellSurface"]=filerawdata[item][17:-1]
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
                    if "Vstep:" in filerawdata[item]:
                        partdict["Vstep"]=str(float(filerawdata[item][7:-1]))
                        break
                for item in range(len(filerawdata)):
                    if "Vstart:" in filerawdata[item]:
                        partdict["Vstart"]=str(float(filerawdata[item][7:-1]))
                        break
                for item in range(len(filerawdata)):
                    if "Vend:" in filerawdata[item]:
                        partdict["Vend"]=str(float(filerawdata[item][5:-1]))
                        break
                for item in range(len(filerawdata)):
                    if "Number of points:" in filerawdata[item]:
                        partdict["NbCycle"]=float(filerawdata[item][17:-1])
                        break
                for item in range(len(filerawdata)):
                    if "Execution time:" in filerawdata[item]:
                        partdict["ExecTime"]=str(float(filerawdata[item][16:-1]))
                        break
                for item in range(len(filerawdata)):
                    if "Time at V=0:" in filerawdata[item]:
                        partdict["TimeatZero"]=str(float(filerawdata[item][13:-1]))
                        break
                for item in range(len(filerawdata)):
                    if "User name:" in filerawdata[item]:
                        partdict["Operator"]=filerawdata[item][11:-1]
                        break
                for item in range(len(filerawdata)):
                    if "MEASURED Fixed Voltage" in filerawdata[item]:
                        pos=item+2
                        break 
                partdict["Group"]="Default group"
                fvpartdat = [[],[],[],[]]#[voltage,current,power,time]
                for item in range(pos,len(filerawdata),1):
                    fvpartdat[0].append(float(filerawdata[item].split("\t")[0]))
                    fvpartdat[1].append(float(filerawdata[item].split("\t")[1]))
                    fvpartdat[2].append(abs(10*float(filerawdata[item].split("\t")[2])))
                    fvpartdat[3].append(float(filerawdata[item].split("\t")[3]))
                partdict["FVData"]=fvpartdat
                DATAFV.append(partdict)
            #self.bytes += self.bytestep
            #self.progress["value"] = self.bytes
        #change name of samples to have all different
        
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
        
        DATAFV = sorted(DATAFV, key=itemgetter('SampleName')) 
        names=[d["SampleName"] for d in DATAFV if "SampleName" in d]
        groupednames=[list(j) for i, j in groupby(names)]
        for item in range(len(groupednames)):
            if len(groupednames[item])!=1:
                for item0 in range(1,len(groupednames[item]),1):
                    groupednames[item][item0]+= "_"+str(item0)
        groupednames=list(chain.from_iterable(groupednames))
        for item in range(len(DATAFV)):
            DATAFV[item]['SampleName']=groupednames[item]
        
        DATAMPP = sorted(DATAMPP, key=itemgetter('SampleName')) 
        names=[d["SampleName"] for d in DATAMPP if "SampleName" in d]
        groupednames=[list(j) for i, j in groupby(names)]
        for item in range(len(groupednames)):
            if len(groupednames[item])!=1:
                for item0 in range(1,len(groupednames[item]),1):
                    groupednames[item][item0]+= "_"+str(item0)
        groupednames=list(chain.from_iterable(groupednames))
        for item in range(len(DATAMPP)):
            DATAMPP[item]['SampleName']=groupednames[item]
    
        
#%%######################################################################
        
    def GraphJVsave_as(self):
        global DATAJVforexport
        global DATAJVtabforexport
        try:
            if self.CheckIVLegend.get()==1:
                f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
                extent = self.IVsubfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                self.fig.savefig(f, dpi=300, bbox_inches=extent.expanded(3, 1.4),bbox_extra_artists=(self.leg,), transparent=True) 
            else:
                f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
                extent = self.IVsubfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                self.fig.savefig(f, dpi=300, bbox_inches=extent.expanded(3, 1.4), transparent=True) 

            DATAJVforexport1=[]
            for item in DATAJVforexport:
                line=""
                for item1 in item:
                    line=line+str(item1)+"\t"
                line=line[:-1]+"\n"
                DATAJVforexport1.append(line)
                
            file = open(str(f[:-4]+"_dat.txt"),'w')
            file.writelines("%s" % item for item in DATAJVforexport1)
            file.close()   
            
            DATAJVforexport1=[]
            for item in DATAJVtabforexport:
                line=""
                for item1 in item:
                    line=line+str(item1)+"\t"
                line=line[:-1]+"\n"
                DATAJVforexport1.append(line)
            file = open(str(f[:-4]+"_tab.txt"),'w')
            file.writelines("%s" % item for item in DATAJVforexport1)
            file.close()

        except:
            print("there is an exception")
        
        
    def GraphMPPsave_as(self):
        global DATAmppforexport
        try:
            if self.CheckmppLegend.get()==1:
                f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
                extent = self.mppsubfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                self.fig.savefig(f, dpi=300, bbox_inches=extent.expanded(3, 1.4),bbox_extra_artists=(self.leg,), transparent=True)
            else:
                f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
                extent = self.mppsubfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                self.fig.savefig(f, dpi=300, bbox_inches=extent.expanded(3, 1.4), transparent=True)
                
            DATAmppforexport1=[]            
            for item in DATAmppforexport:
                line=""
                for item1 in item:
                    line=line+str(item1)+"\t"
                line=line[:-1]+"\n"
                DATAmppforexport1.append(line)
                
            file = open(str(f[:-4]+"_dat.txt"),'w')
            file.writelines("%s" % item for item in DATAmppforexport1)
            file.close()
        
        except:
            print("there is an exception")    
    
    def GraphGroupsave_as(self):
        global DATAgroupforexport
        try:
            if self.Big4.get()==0:
                f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
                extent = self.GroupStatfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                self.fig.savefig(f, dpi=300, bbox_inches=extent.expanded(1.5, 2), transparent=True)
                
                DATAgroupforexport1=[]            
                for item in DATAgroupforexport:
                    line=""
                    for item1 in item:
                        line=line+str(item1)+"\t"
                    line=line[:-1]+"\n"
                    DATAgroupforexport1.append(line)
                
                file = open(str(f[:-4]+"_"+self.GroupChoice.get()+"dat.txt"),'w')
                file.writelines("%s" % item for item in DATAgroupforexport1)
                file.close()
            elif self.Big4.get()==1:
                
                f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
                self.GroupChoice.set("Eff")
                self.UpdateGroupGraph(1)
                extent = self.GroupStatfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                self.fig.savefig(f[:-4]+"_"+self.GroupChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.5, 1.5), transparent=True)
                
                DATAgroupforexport1=[]            
                for item in DATAgroupforexport:
                    line=""
                    for item1 in item:
                        line=line+str(item1)+"\t"
                    line=line[:-1]+"\n"
                    DATAgroupforexport1.append(line)
                
                file = open(str(f[:-4]+"_"+self.GroupChoice.get()+"dat.txt"),'w')
                file.writelines("%s" % item for item in DATAgroupforexport1)
                file.close()
                self.GroupChoice.set("Voc")
                self.UpdateGroupGraph(1)
                
                extent = self.GroupStatfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                self.fig.savefig(f[:-4]+"_"+self.GroupChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.5, 1.5), transparent=True)
                
                DATAgroupforexport1=[]            
                for item in DATAgroupforexport:
                    line=""
                    for item1 in item:
                        line=line+str(item1)+"\t"
                    line=line[:-1]+"\n"
                    DATAgroupforexport1.append(line)
                
                file = open(str(f[:-4]+"_"+self.GroupChoice.get()+"dat.txt"),'w')
                file.writelines("%s" % item for item in DATAgroupforexport1)
                file.close()
                self.GroupChoice.set("Jsc")
                self.UpdateGroupGraph(1)
                
                extent = self.GroupStatfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                self.fig.savefig(f[:-4]+"_"+self.GroupChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.5, 1.5), transparent=True)
                
                DATAgroupforexport1=[]            
                for item in DATAgroupforexport:
                    line=""
                    for item1 in item:
                        line=line+str(item1)+"\t"
                    line=line[:-1]+"\n"
                    DATAgroupforexport1.append(line)
                
                file = open(str(f[:-4]+"_"+self.GroupChoice.get()+"dat.txt"),'w')
                file.writelines("%s" % item for item in DATAgroupforexport1)
                file.close()
                self.GroupChoice.set("FF")
                self.UpdateGroupGraph(1)
                
                extent = self.GroupStatfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                self.fig.savefig(f[:-4]+"_"+self.GroupChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.5, 1.5), transparent=True)
                
                DATAgroupforexport1=[]            
                for item in DATAgroupforexport:
                    line=""
                    for item1 in item:
                        line=line+str(item1)+"\t"
                    line=line[:-1]+"\n"
                    DATAgroupforexport1.append(line)
                
                file = open(str(f[:-4]+"_"+self.GroupChoice.get()+"dat.txt"),'w')
                file.writelines("%s" % item for item in DATAgroupforexport1)
                file.close()
        except:
            print("there is an exception")  
            
    def full_extent(ax, pad=0.0):
        """Get the full extent of an axes, including axes labels, tick labels, and
        titles."""
        # For text objects, we need to draw the figure first, otherwise the extents
        # are undefined.
        ax.figure.canvas.draw()
        items = ax.get_xticklabels() + ax.get_yticklabels() 
        #    items += [ax, ax.title, ax.xaxis.label, ax.yaxis.label]
        items += [ax, ax.title]
        bbox = Bbox.union([item.get_window_extent() for item in items])

        return bbox.expanded(1.0 + pad, 1.0 + pad)      

#%%######################################################################

    def ExportAutoAnalysis(self):
        global DATA
        global DATAdark
        global DATAFV
        global DATAMPP
        global samplesgroups
           
        current_path = os.getcwd()
        folderName = filedialog.askdirectory(title = "choose a folder to export the auto-analysis results", initialdir=os.path.dirname(current_path))
        os.chdir(folderName)
        
        DATAx=copy.deepcopy(DATA)
        plt.close("all")
        sorted_datajv = sorted(DATAx, key=itemgetter('DepID')) 
        sorted_datampp = sorted(DATAMPP, key=itemgetter('DepID')) 
        sorted_datafv = sorted(DATAFV, key=itemgetter('DepID'))
        DATAbysubstrate=[] 
        DATAmppbysubstrate=[]
        DATAfvbysubstrate=[]
        DATAdarkbysubstrate=[] 
        bestEff=[]
        bestvocff =[]
        sorted_datadark = sorted(DATAdark, key=itemgetter('DepID'))
        try:
            batchname="P###"
            if "_" in DATAx[0]["DepID"]:
                batchname=DATAx[0]["DepID"].split("_")[0]
            elif "-" in DATAx[0]["DepID"]:
                batchname=DATAx[0]["DepID"].split("-")[0]
        except:
            print("there's an issue...")
        
        for key, group in groupby(sorted_datadark, key=lambda x:x['DepID']):
            substratpartdat=[key,list(group)]
            DATAdarkbysubstrate.append(copy.deepcopy(substratpartdat))
            try:
                if self.TxtforOrigin.get():
                    contenttxtfile=["","",""]
                    for item in range(len(substratpartdat[1])):
                        contenttxtfile[0] += "Voltage\t" + "Current density\t" 
                        contenttxtfile[1] += "mV\t" + "mA/cm2\t"
                        contenttxtfile[2] += " \t" + substratpartdat[1][item]["SampleName"] + '\t'
                    contenttxtfile[0]=contenttxtfile[0][:-1]+'\n'
                    contenttxtfile[1]=contenttxtfile[1][:-1]+'\n'
                    contenttxtfile[2]=contenttxtfile[2][:-1]+'\n'
                    #find max length of subjv lists => fill the others with blancks
                    lengthmax=max([len(substratpartdat[1][x]["IVData"][0]) for x in range(len(substratpartdat[1]))])
                    for item in range(len(substratpartdat[1])):
                        while (len(substratpartdat[1][item]["IVData"][0])<lengthmax):
                            substratpartdat[1][item]["IVData"][0].append('')   
                            substratpartdat[1][item]["IVData"][1].append('') 
                    #append them all in the content list
                    for item0 in range(lengthmax):
                        ligne=""
                        for item in range(len(substratpartdat[1])):
                            ligne += str(substratpartdat[1][item]["IVData"][0][item0]) +'\t' + str(substratpartdat[1][item]["IVData"][1][item0]) +'\t'   
                        ligne=ligne[:-1]+'\n'    
                        contenttxtfile.append(ligne)
                    #export it to txt files
                    file = open(str(substratpartdat[0]) + '_lowIllum.txt','w')
                    file.writelines("%s" % item for item in contenttxtfile)
                    file.close()
            except:
                print("there's an issue with creating JVdark txt files")
            try:
                if self.AutoGraphs.get():
                    plt.close("all")
                    fig, axs =plt.subplots(1,2)
                    x1=min(DATAdarkbysubstrate[-1][1][0]["IVData"][0])
                    x2=max(DATAdarkbysubstrate[-1][1][0]["IVData"][0])
                    y1=min(DATAdarkbysubstrate[-1][1][0]["IVData"][1])
                    if max(DATAdarkbysubstrate[-1][1][0]["IVData"][1])<10:
                        y2=max(DATAdarkbysubstrate[-1][1][0]["IVData"][1])
                    else:
                        y2=10
                    for item in range(len(substratpartdat[1])):
                        axs[0].plot(DATAdarkbysubstrate[-1][1][item]["IVData"][0],DATAdarkbysubstrate[-1][1][item]["IVData"][1], label=DATAdarkbysubstrate[-1][1][item]["SampleName"])
                        if min(DATAdarkbysubstrate[-1][1][item]["IVData"][0])<x1:
                            x1=copy.deepcopy(min(DATAdarkbysubstrate[-1][1][item]["IVData"][0]))
                        if max(DATAdarkbysubstrate[-1][1][item]["IVData"][0])>x2:
                            x2=copy.deepcopy(max(DATAdarkbysubstrate[-1][1][item]["IVData"][0]))
                        if min(DATAdarkbysubstrate[-1][1][item]["IVData"][1])<y1:
                            y1=copy.deepcopy(min(DATAdarkbysubstrate[-1][1][item]["IVData"][1]))
                        if max(DATAdarkbysubstrate[-1][1][item]["IVData"][1])>y2 and max(DATAdarkbysubstrate[-1][1][item]["IVData"][1])<10:
                            y2=copy.deepcopy(max(DATAdarkbysubstrate[-1][1][item]["IVData"][1]))
                        slist=DATAdarkbysubstrate[-1][1][item]
                    axs[0].set_title("Low Illumination: "+str(substratpartdat[0]))
                    axs[0].set_xlabel('Voltage (mV)')
                    axs[0].set_ylabel('Current density (mA/cm'+'\xb2'+')')
                    axs[0].axhline(y=0, color='k')
                    axs[0].axvline(x=0, color='k')
                    axs[0].axis([x1,x2,y1,y2])
                    for item in range(len(substratpartdat[1])):
                        axs[1].semilogy(DATAdarkbysubstrate[-1][1][item]["IVData"][0],list(map(abs, DATAdarkbysubstrate[-1][1][item]["IVData"][1])), label=DATAdarkbysubstrate[-1][1][item]["SampleName"])
                    axs[1].set_title("logscale")
                    axs[1].set_xlabel('Voltage (mV)')
                    axs[1].axhline(y=0, color='k')
                    axs[1].axvline(x=0, color='k')
                    box = axs[0].get_position()
                    axs[0].set_position([box.x0, box.y0, box.width, box.height])
                    box = axs[1].get_position()
                    axs[1].set_position([box.x0, box.y0, box.width, box.height])
                    lgd=axs[1].legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=1)
                    #axs[1].legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.2)
                    plt.savefig(str(substratpartdat[0])+'_lowIllum.png',dpi=300, bbox_extra_artists=(lgd,),bbox_inches="tight")
                    plt.close(fig) 
                    plt.close('all')
            except:
                print("there's an issue with creating JV lowillum graphs")
        
        try:
            for key, group in groupby(sorted_datampp, key=lambda x:x['DepID']):
                substratpartdat=[key,list(group)]
                DATAmppbysubstrate.append(copy.deepcopy(substratpartdat))
                for item0 in range(len(substratpartdat[1])):
                    if self.TxtforOrigin.get():
                        contenttxtfile=["Voltage\tCurrent density\tTime\tPmpp\tTime\tVstep\n","V\tmA/cm2\ts\tW/m2\ts\tV\n"]
                        for item in range(len(substratpartdat[1][item0]["MppData"][0])):
                            contenttxtfile.append(str(substratpartdat[1][item0]["MppData"][0][item])+"\t"+str(substratpartdat[1][item0]["MppData"][1][item])+"\t"+str(substratpartdat[1][item0]["MppData"][2][item])+"\t"+str(substratpartdat[1][item0]["MppData"][3][item])+"\t"+str(substratpartdat[1][item0]["MppData"][2][item])+"\t"+str(substratpartdat[1][item0]["MppData"][4][item])+"\n")
                        #export to txt files
                        file = open(str(substratpartdat[1][item0]["SampleName"]) + '_Pmpp.txt','w')
                        file.writelines("%s" % item for item in contenttxtfile)
                        file.close()
                    #export figures
                    if self.AutoGraphs.get():
                        plt.plot(substratpartdat[1][item0]["MppData"][2],substratpartdat[1][item0]["MppData"][3])
                        plt.xlabel('Time (s)')
                        plt.ylabel('Power (mW/cm'+'\xb2'+')')        
                        plt.savefig(str(substratpartdat[1][item0]["SampleName"]) + '_Pmpp.png',dpi=300)
                    plt.close('all')
        except:
            print("there's an issue with creating pmpp txt files")
            
        try:     
            for key, group in groupby(sorted_datafv, key=lambda x:x['DepID']):
                substratpartdat=[key,list(group)]
                DATAfvbysubstrate.append(copy.deepcopy(substratpartdat))
                for item0 in range(len(substratpartdat[1])):
                    if self.TxtforOrigin.get():
                        contenttxtfile=["Time\tVoltage\tCurrent density\tPower\n","s\tV\tmA/cm2\tmW/cm2\n"]
                        for item in range(len(substratpartdat[1][item0]["FVData"][0])):
                            contenttxtfile.append(str(substratpartdat[1][item0]["FVData"][3][item])+"\t"+str(substratpartdat[1][item0]["FVData"][0][item])+"\t"+str(substratpartdat[1][item0]["FVData"][1][item])+"\t"+str(substratpartdat[1][item0]["FVData"][2][item])+"\n")
                        #export to txt files
                        file = open(str(substratpartdat[1][item0]["SampleName"]) + '_FV.txt','w')
                        file.writelines("%s" % item for item in contenttxtfile)
                        file.close()
                    #export figures
                    if self.AutoGraphs.get():
                        plt.plot(substratpartdat[1][item0]["FVData"][3],substratpartdat[1][item0]["FVData"][2])
                        plt.xlabel('Time (s)')
                        plt.ylabel('Power (mW/cm'+'\xb2'+')')        
                        plt.savefig(str(substratpartdat[1][item0]["SampleName"]) + '_FV.png',dpi=300)
                    plt.close('all') 
        except:
            print("there's an issue with creating FV txt files")
            
        try:    
            for key, group in groupby(sorted_datajv, key=lambda x:x['DepID']):
                substratpartdat=[key,list(group)]
                DATAbysubstrate.append(copy.deepcopy(substratpartdat))
                if self.TxtforOrigin.get():
                    contenttxtfile=["","",""]
                    for item in range(len(substratpartdat[1])):
                        contenttxtfile[0] += "Voltage\t" + "Current density\t" 
                        contenttxtfile[1] += "mV\t" + "mA/cm2\t"
                        contenttxtfile[2] += " \t" + substratpartdat[1][item]["SampleName"] + '\t'
                    contenttxtfile[0]=contenttxtfile[0][:-1]+'\n'
                    contenttxtfile[1]=contenttxtfile[1][:-1]+'\n'
                    contenttxtfile[2]=contenttxtfile[2][:-1]+'\n'
                    #print(contenttxtfile)  
                    #find max length of subjv lists => fill the others with blancks
                    lengthmax=max([len(substratpartdat[1][x]["IVData"][0]) for x in range(len(substratpartdat[1]))])
                    for item in range(len(substratpartdat[1])):
                        while (len(substratpartdat[1][item]["IVData"][0])<lengthmax):
                            substratpartdat[1][item]["IVData"][0].append('')   
                            substratpartdat[1][item]["IVData"][1].append('') 
                    #append them all in the content list
                    for item0 in range(lengthmax):
                        ligne=""
                        for item in range(len(substratpartdat[1])):
                            ligne += str(substratpartdat[1][item]["IVData"][0][item0]) +'\t' + str(substratpartdat[1][item]["IVData"][1][item0]) +'\t'   
                        ligne=ligne[:-1]+'\n'    
                        contenttxtfile.append(ligne)
                    #export it to txt files
                    file = open(str(substratpartdat[0]) + '.txt','w')
                    file.writelines("%s" % item for item in contenttxtfile)
                    file.close()
                #graphs by substrate with JV table, separate graph and table production, then reassemble to export...
                if self.AutoGraphs.get():
                    collabel=("Voc","Jsc","FF","Eff","Roc","Rsc","Vstart","Vend","CellSurface")
                    nrows, ncols = len(substratpartdat[1])+1, len(collabel)
                    hcell, wcell = 0.3, 1.
                    hpad, wpad = 0, 0 
                    fig2=plt.figure(figsize=(ncols*wcell+wpad, nrows*hcell+hpad))
                    ax2 = fig2.add_subplot(111)
                    
                    fig1=plt.figure()
                    ax3 = fig1.add_subplot(111)
                    
                    x1=min(DATAbysubstrate[-1][1][0]["IVData"][0])
                    x2=max(DATAbysubstrate[-1][1][0]["IVData"][0])
                    y1=min(DATAbysubstrate[-1][1][0]["IVData"][1])
                    if max(DATAbysubstrate[-1][1][0]["IVData"][1])<10:
                        y2=max(DATAbysubstrate[-1][1][0]["IVData"][1])
                    else:
                        y2=10
                    tabledata=[]
                    rowlabel=[]
                    for item in range(len(substratpartdat[1])):
                        ax3.plot(DATAbysubstrate[-1][1][item]["IVData"][0],DATAbysubstrate[-1][1][item]["IVData"][1], label=DATAbysubstrate[-1][1][item]["SampleName"])
                        if min(DATAbysubstrate[-1][1][item]["IVData"][0])<x1:
                            x1=copy.deepcopy(min(DATAbysubstrate[-1][1][item]["IVData"][0]))
                        if max(DATAbysubstrate[-1][1][item]["IVData"][0])>x2:
                            x2=copy.deepcopy(max(DATAbysubstrate[-1][1][item]["IVData"][0]))
                        if min(DATAbysubstrate[-1][1][item]["IVData"][1])<y1:
                            y1=copy.deepcopy(min(DATAbysubstrate[-1][1][item]["IVData"][1]))
                        if max(DATAbysubstrate[-1][1][item]["IVData"][1])>y2 and max(DATAbysubstrate[-1][1][item]["IVData"][1])<10:
                            y2=copy.deepcopy(max(DATAbysubstrate[-1][1][item]["IVData"][1]))
                
                        slist=DATAbysubstrate[-1][1][item]
                        rowlabel.append(slist["SampleName"])
                        tabledata.append(['%.f' % float(slist["Voc"]),'%.2f' % float(slist["Jsc"]),'%.2f' % float(slist["FF"]),'%.2f' % float(slist["Eff"]),'%.2f' % float(slist["Roc"]),'%.2f' % float(slist["Rsc"]),'%.2f' % float(slist["Vstart"]),'%.2f' % float(slist["Vend"]),'%.2f' % float(slist["CellSurface"])])
                    
                    ax3.set_title(str(substratpartdat[0]))
                    ax3.set_xlabel('Voltage (mV)')
                    ax3.set_ylabel('Current density (mA/cm'+'\xb2'+')')
                    ax3.axhline(y=0, color='k')
                    ax3.axvline(x=0, color='k')
                    ax3.axis([x1,x2,y1,y2])
                
                    rowlabel=tuple(rowlabel)
                    the_table = ax2.table(cellText=tabledata,colLabels=collabel,rowLabels=rowlabel,loc='center')
                    the_table.set_fontsize(18)
                    ax2.axis('off')
                    fig2.savefig(str(substratpartdat[0])+'_table.png',dpi=300,bbox_inches="tight")
                    handles, labels = ax3.get_legend_handles_labels()
                    lgd = ax3.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5))
                    fig1.savefig(str(substratpartdat[0])+'.png',dpi=300, bbox_extra_artists=(lgd,),bbox_inches="tight")
                    
                    images = list(map(ImageTk.open, [str(substratpartdat[0])+'.png',str(substratpartdat[0])+'_table.png']))
                    widths, heights = zip(*(i.size for i in images))
                    total_width = max(widths)
                    max_height = sum(heights)
                    new_im = ImageTk.new('RGB', (total_width, max_height), (255, 255, 255))
                    new_im.paste(im=images[0],box=(0,0))
                    new_im.paste(im=images[1],box=(0,heights[0]))
                    new_im.save(str(substratpartdat[0])+'.png')
                    
                    os.remove(str(substratpartdat[0])+'_table.png')
                    plt.close(fig2)
                    plt.close(fig1)
                    plt.close('all')
                   
                    if DATAx[0]["Setup"]=="TFIV":
                        #graph best FR of this substrate
                        best = sorted(DATAbysubstrate[-1][1], key=itemgetter('VocFF'), reverse=True)
                        item=0
                        while item<len(best):
                            if float(best[item]["FF"])>10 and float(best[item]["Jsc"])<40:
                                bestvocff.append(copy.deepcopy(best[item]))
                                break
                            else:
                                item+=1
                        best = sorted(DATAbysubstrate[-1][1], key=itemgetter('Eff'), reverse=True)
                        item=0
                        while item<len(best):
                            if float(best[item]["FF"])>10 and float(best[item]["Jsc"])<40:
                                fig=plt.figure()
                                ax=fig.add_subplot(111)
                                bestEff.append(copy.deepcopy(best[item]))
                                if best[item]["ScanDirection"]=="Reverse":
                                    ax.plot(best[item]["IVData"][0],best[item]["IVData"][1],"r", label=best[item]["SampleName"])
                                    text = best[item]["ScanDirection"]+"; "+"Voc: " + '%.f' % float(best[item]["Voc"]) +" mV; " + "Jsc: " + '%.2f' % float(best[item]["Jsc"]) +" mA/cm2; " +"FF: " + '%.2f' % float(best[item]["FF"]) +" %; " +"Eff: " + '%.2f' % float(best[item]["Eff"]) +" %"
                                    ax.set_title('Best:'+ best[item]["SampleName"]+"\n"+text, fontsize = 10, color="r")
                                elif best[item]["ScanDirection"]=="Forward":
                                    ax.plot(best[item]["IVData"][0],best[item]["IVData"][1],"k", label=best[item]["SampleName"]) 
                                    text = best[item]["ScanDirection"]+"; "+"Voc: " + '%.f' % float(best[item]["Voc"]) +" mV; " + "Jsc: " + '%.2f' % float(best[item]["Jsc"]) +" mA/cm2; " +"FF: " + '%.2f' % float(best[item]["FF"]) +" %; " +"Eff: " + '%.2f' % float(best[item]["Eff"]) +" %"
                                    ax.set_title('Best:'+ best[item]["SampleName"]+"\n"+text, fontsize = 10, color="k")
                                pos=0
                                if best[item]["ScanDirection"]=="Reverse":
                                    for item0 in range(item+1,len(best),1):
                                        if best[item0]["ScanDirection"]=="Forward" and best[item]["CellNumber"]==best[item0]["CellNumber"]:
                                            #other=best[item0]
                                            pos=item0
                                            ax.plot(best[pos]["IVData"][0],best[pos]["IVData"][1],"k", label=best[pos]["SampleName"])
                                            ax.set_title('Best:'+ best[item]["SampleName"]+"-"+best[pos]["SampleName"]+"\n"+text, fontsize = 10, color="r")
                                            break
                                elif best[item]["ScanDirection"]=="Forward":
                                    for item0 in range(item+1,len(best),1):
                                        if best[item0]["ScanDirection"]=="Reverse" and best[item]["CellNumber"]==best[item0]["CellNumber"]:
                                            #other=best[item0]
                                            pos=item0
                                            ax.plot(best[pos]["IVData"][0],best[pos]["IVData"][1],"r", label=best[pos]["SampleName"])
                                            ax.set_title('Best:'+ best[item]["SampleName"]+"-"+best[pos]["SampleName"]+"\n"+text, fontsize = 10, color="k")
                                            break
                                
                                ax.set_xlabel('Voltage (mV)')
                                ax.set_ylabel('Current density (mA/cm'+'\xb2'+')')
                                ax.axhline(y=0, color='k')
                                ax.axvline(x=0, color='k')
                                
                                x1=min(best[item]["IVData"][0][0],best[pos]["IVData"][0][0])
                                x2=max(best[item]["IVData"][0][-1],best[pos]["IVData"][0][-1])
                                y1=1.1*min(best[item]["IVData"][1]+best[pos]["IVData"][1])
                                if max(best[item]["IVData"][1]+best[pos]["IVData"][1])>10:
                                    y2=10
                                else:
                                    y2=max(best[item]["IVData"][1]+best[pos]["IVData"][1])
                                ax.axis([x1,x2,y1,y2])
                                handles, labels = ax.get_legend_handles_labels()
                                lgd = ax.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5))
                                fig.savefig(str(substratpartdat[0])+'_BestRevForw.png',dpi=300, bbox_extra_artists=(lgd,),bbox_inches="tight")
                                plt.close('all')
                                break
                            else:
                                item+=1 
                    #specific power graph
                    for item in range(len(DATAmppbysubstrate)):
                        if substratpartdat[0]==DATAmppbysubstrate[item][0]:
                            for item0 in range(len(DATAmppbysubstrate[item][1])):
                                fig=plt.figure()
                                ax=fig.add_subplot(111)
                                for item1 in range(len(DATAbysubstrate[-1][1])):
                                    if DATAmppbysubstrate[item][1][item0]["CellNumber"]==DATAbysubstrate[-1][1][item1]["CellNumber"]:
                                        ax.plot(DATAbysubstrate[-1][1][item1]["IVData"][0],[-10*a*b for a,b in zip(DATAbysubstrate[-1][1][item1]["IVData"][0],DATAbysubstrate[-1][1][item1]["IVData"][1])])
                                ax.plot([abs(a) for a in DATAmppbysubstrate[item][1][item0]["MppData"][0]],DATAmppbysubstrate[item][1][item0]["MppData"][3])
                                ax.set_xlabel('Voltage (mV)')
                                ax.set_ylabel('Specific power (W/m$^2$)')
                                ax.axhline(y=0, color='k')
                                ax.axvline(x=0, color='k')
                                ax.set_xlim(left=0)
                                ax.set_ylim(bottom=0)
                                fig.savefig(DATAmppbysubstrate[item][1][item0]["SampleName"]+'_specpower.png',dpi=300,bbox_inches="tight")
                                plt.close("all")
                            break
        except:
            print("there's an issue with creating JV graph files")     
         
        if DATAx[0]["Setup"]=="TFIV":
            try:        
                if self.AutoGraphs.get():
                    #graph with all best efficient cells from all substrates
                    fig=plt.figure()
                    ax=fig.add_subplot(111)
                    bestEffsorted = sorted(bestEff, key=itemgetter('Eff'), reverse=True) 
                    tabledata=[]
                    rowlabel=[]
                    for item in range(len(bestEffsorted)):
                        ax.plot(bestEffsorted[item]["IVData"][0],bestEffsorted[item]["IVData"][1], label=bestEffsorted[item]["SampleName"]) 
                        rowlabel.append(bestEffsorted[item]["SampleName"])
                        tabledata.append(['%.f' % float(bestEffsorted[item]["Voc"]),'%.2f' % float(bestEffsorted[item]["Jsc"]),'%.2f' % float(bestEffsorted[item]["FF"]),'%.2f' % float(bestEffsorted[item]["Eff"]),'%.2f' % float(bestEffsorted[item]["Roc"]),'%.2f' % float(bestEffsorted[item]["Rsc"]),'%.2f' % float(bestEffsorted[item]["Vstart"]),'%.2f' % float(bestEffsorted[item]["Vend"]),'%.2f' % float(bestEffsorted[item]["CellSurface"])])
                    ax.set_xlabel('Voltage (mV)')
                    ax.set_ylabel('Current density (mA/cm'+'\xb2'+')')
                    ax.axhline(y=0, color='k')
                    ax.axvline(x=0, color='k')
                    x1=min(bestEffsorted[item]["IVData"][0])
                    x2=max(bestEffsorted[item]["IVData"][0])
                    y1=1.3*min(bestEffsorted[item]["IVData"][1])
                    if max(bestEffsorted[item]["IVData"][1])>10:
                        y2=10
                    else:
                        y2=max(bestEffsorted[item]["IVData"][1])
                    ax.axis([x1,x2,y1,y2])
                    handles, labels = ax.get_legend_handles_labels()
                    lgd = ax.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5))
                    fig.savefig(batchname+'_MostEfficientCells.png',dpi=300, bbox_extra_artists=(lgd,),bbox_inches="tight")
                    plt.close()
                    collabel=("Voc","Jsc","FF","Eff","Roc","Rsc","Vstart","Vend","CellSurface")
                    nrows, ncols = len(bestEffsorted)+1, len(collabel)
                    hcell, wcell = 0.3, 1.
                    hpad, wpad = 0, 0 
                    fig=plt.figure(figsize=(ncols*wcell+wpad, nrows*hcell+hpad))
                    ax = fig.add_subplot(111)
                    rowlabel=tuple(rowlabel)
                    the_table = ax.table(cellText=tabledata,colLabels=collabel,rowLabels=rowlabel,loc='center')
                    the_table.set_fontsize(18)
                    ax.axis('off')
                    fig.savefig('MostEfficientCellstable.png',dpi=300,bbox_inches="tight")
                    plt.close("all")
                    images = list(map(ImageTk.open, [batchname+'_MostEfficientCells.png','MostEfficientCellstable.png']))
                    widths, heights = zip(*(i.size for i in images))
                    total_width = max(widths)
                    max_height = sum(heights)
                    new_im = ImageTk.new('RGB', (total_width, max_height), (255, 255, 255))
                    new_im.paste(im=images[0],box=(0,0))
                    new_im.paste(im=images[1],box=(0,heights[0]))
                    new_im.save(batchname+'_MostEfficientCells.png')
                    os.remove('MostEfficientCellstable.png')
                    plt.close()
                    #graph with all best voc*FF cells from all substrates  
                    fig=plt.figure()
                    ax=fig.add_subplot(111)
                    bestvocffsorted = sorted(bestvocff, key=itemgetter('VocFF'), reverse=True) 
                    tabledata=[]
                    rowlabel=[]
                    for item in range(len(bestEffsorted)):
                        ax.plot(bestvocffsorted[item]["IVData"][0],bestvocffsorted[item]["IVData"][1], label=bestvocffsorted[item]["SampleName"]) 
                        rowlabel.append(bestvocffsorted[item]["SampleName"])
                        tabledata.append(['%.f' % float(bestvocffsorted[item]["Voc"]),'%.2f' % float(bestvocffsorted[item]["Jsc"]),'%.2f' % float(bestvocffsorted[item]["FF"]),'%.2f' % float(bestvocffsorted[item]["Eff"]),'%.2f' % float(bestvocffsorted[item]["Roc"]),'%.2f' % float(bestvocffsorted[item]["Rsc"]),'%.2f' % float(bestvocffsorted[item]["Vstart"]),'%.2f' % float(bestvocffsorted[item]["Vend"]),'%.2f' % float(bestvocffsorted[item]["CellSurface"])])
                    ax.set_xlabel('Voltage (mV)')
                    ax.set_ylabel('Current density (mA/cm'+'\xb2'+')')
                    ax.axhline(y=0, color='k')
                    ax.axvline(x=0, color='k')
                    x1=min(bestvocffsorted[item]["IVData"][0])
                    x2=max(bestvocffsorted[item]["IVData"][0])
                    y1=1.3*min(bestvocffsorted[item]["IVData"][1])
                    if max(bestvocffsorted[item]["IVData"][1])>10:
                        y2=10
                    else:
                        y2=max(bestvocffsorted[item]["IVData"][1])
                    ax.axis([x1,x2,y1,y2])
                    handles, labels = ax.get_legend_handles_labels()
                    lgd = ax.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5))
                    fig.savefig(batchname+'_bestvocff.png',dpi=300, bbox_extra_artists=(lgd,),bbox_inches="tight")
                    plt.close(fig)
                    collabel=("Voc","Jsc","FF","Eff","Roc","Rsc","Vstart","Vend","CellSurface")
                    nrows, ncols = len(bestvocffsorted)+1, len(collabel)
                    hcell, wcell = 0.3, 1.
                    hpad, wpad = 0, 0 
                    fig=plt.figure(figsize=(ncols*wcell+wpad, nrows*hcell+hpad))
                    ax = fig.add_subplot(111)
                    rowlabel=tuple(rowlabel)
                    the_table = ax.table(cellText=tabledata,colLabels=collabel,rowLabels=rowlabel,loc='center')
                    the_table.set_fontsize(18)
                    ax.axis('off')
                    fig.savefig('bestvocfftable.png',dpi=300,bbox_inches="tight")
                    plt.close(fig)
                    images = list(map(ImageTk.open, [batchname+'_bestvocff.png','bestvocfftable.png']))
                    widths, heights = zip(*(i.size for i in images))
                    total_width = max(widths)
                    max_height = sum(heights)
                    new_im = ImageTk.new('RGB', (total_width, max_height), (255, 255, 255))
                    new_im.paste(im=images[0],box=(0,0))
                    new_im.paste(im=images[1],box=(0,heights[0]))
                    new_im.save(batchname+'_bestvocff.png')
                    os.remove('bestvocfftable.png')
            except:
                print("there's an issue with creating Bestof graphs")
            
            
        if len(samplesgroups)>1:            
            grouplistdict=[]
            for item in range(len(samplesgroups)):
                groupdict={}
                groupdict["Group"]=samplesgroups[item]
                listofthegroup=[]
                listofthegroupNames=[]
                for item1 in range(len(DATAx)):
                    if DATAx[item1]["Group"]==groupdict["Group"]:
                        listofthegroup.append(DATAx[item1])
                        listofthegroupNames.append(DATAx[item1]['DepID']+'_'+DATAx[item1]['Cellletter'])
                groupdict["numbCell"]=len(list(set(listofthegroupNames)))
                listofthegroupRev=[]
                listofthegroupFor=[]
                for item1 in range(len(listofthegroup)):
                    if listofthegroup[item1]["ScanDirection"]=="Reverse":
                        listofthegroupRev.append(listofthegroup[item1])
                    else:
                        listofthegroupFor.append(listofthegroup[item1])
               
                groupdict["RevVoc"]=[x['Voc'] for x in listofthegroupRev if 'Voc' in x]
                groupdict["ForVoc"]=[x['Voc'] for x in listofthegroupFor if 'Voc' in x]
                groupdict["RevJsc"]=[x['Jsc'] for x in listofthegroupRev if 'Jsc' in x]
                groupdict["ForJsc"]=[x['Jsc'] for x in listofthegroupFor if 'Jsc' in x]
                groupdict["RevFF"]=[x['FF'] for x in listofthegroupRev if 'FF' in x]
                groupdict["ForFF"]=[x['FF'] for x in listofthegroupFor if 'FF' in x]
                groupdict["RevEff"]=[x['Eff'] for x in listofthegroupRev if 'Eff' in x]
                groupdict["ForEff"]=[x['Eff'] for x in listofthegroupFor if 'Eff' in x]
                
                grouplistdict.append(groupdict)
        
            
        #excel summary file with all data: tabs (rawdataLight, rawdatadark, besteff, bestvocff, pmpp, fixedvoltage)
        try:
            if self.CheckXlsxSum.get():   
                workbook = xlsxwriter.Workbook(batchname+'_Summary.xlsx')
                
                LandD=DATAx + DATAdark
                timeLandD =sorted(LandD, key=itemgetter('MeasDayTime')) 
                
                if len(samplesgroups)>1:
                    worksheet = workbook.add_worksheet("GroupStat")
                    summary=[]
                    for item in range(len(samplesgroups)):
                        ncell=1
                        if grouplistdict[item]["ForVoc"]!=[]:
                            lengthofgroup=len(grouplistdict[item]["ForVoc"])
                            summary.append([grouplistdict[item]["Group"],grouplistdict[item]["numbCell"],"Forward",lengthofgroup,sum(grouplistdict[item]["ForVoc"],0.0)/lengthofgroup,np.std(grouplistdict[item]["ForVoc"]),sum(grouplistdict[item]["ForJsc"],0.0)/lengthofgroup,np.std(grouplistdict[item]["ForJsc"]),sum(grouplistdict[item]["ForFF"],0.0)/lengthofgroup,np.std(grouplistdict[item]["ForFF"]),sum(grouplistdict[item]["ForEff"],0.0)/lengthofgroup,np.std(grouplistdict[item]["ForEff"])])
                            ncell=0
                        if grouplistdict[item]["RevVoc"]!=[]:  
                            if ncell==0:
                                lengthofgroup=len(grouplistdict[item]["RevVoc"])
                                summary.append([grouplistdict[item]["Group"]," ","Reverse",lengthofgroup,sum(grouplistdict[item]["RevVoc"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevVoc"]),sum(grouplistdict[item]["RevJsc"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevJsc"]),sum(grouplistdict[item]["RevFF"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevFF"]),sum(grouplistdict[item]["RevEff"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevEff"])])
                            else:
                                lengthofgroup=len(grouplistdict[item]["RevVoc"])
                                summary.append([grouplistdict[item]["Group"],grouplistdict[item]["numbCell"],"Reverse",lengthofgroup,sum(grouplistdict[item]["RevVoc"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevVoc"]),sum(grouplistdict[item]["RevJsc"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevJsc"]),sum(grouplistdict[item]["RevFF"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevFF"]),sum(grouplistdict[item]["RevEff"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevEff"])])
        
                    summary.insert(0, [" ", " "," ", "-", "mV","-","mA/cm2","-","%","-","%","-"])
                    summary.insert(0, ["Group","#Cells","Scan Dir.","#ofmeas", "Voc"," ","Jsc"," ","FF"," ","Eff"," "])
                    summary.insert(0, [" "," "," "," ", "Avg","StdDev","Avg","StdDev","Avg","StdDev","Avg","StdDev"])
                    for item in range(len(summary)):
                        for item0 in range(len(summary[item])):
                            worksheet.write(item,item0,summary[item][item0])
            
                if timeLandD!=[]:
                    worksheet = workbook.add_worksheet("AllJVrawdata")
                    summary=[]
                    for item in range(len(timeLandD)):
                        summary.append([timeLandD[item]["Group"],timeLandD[item]["SampleName"],timeLandD[item]["Cellletter"],timeLandD[item]["MeasDayTime"],timeLandD[item]["CellSurface"],str(timeLandD[item]["Voc"]),str(timeLandD[item]["Jsc"]),str(timeLandD[item]["FF"]),str(timeLandD[item]["Eff"]),str(timeLandD[item]["Pmpp"]),str(timeLandD[item]["Vmpp"]),str(timeLandD[item]["Jmpp"]),str(timeLandD[item]["Roc"]),str(timeLandD[item]["Rsc"]),str(timeLandD[item]["VocFF"]),str(timeLandD[item]["RscJsc"]),str(timeLandD[item]["NbPoints"]),timeLandD[item]["Delay"],timeLandD[item]["IntegTime"],timeLandD[item]["Vstart"],timeLandD[item]["Vend"],timeLandD[item]["Illumination"],timeLandD[item]["ScanDirection"],str('%.2f' % float(timeLandD[item]["ImaxComp"])),timeLandD[item]["Isenserange"],str(timeLandD[item]["AreaJV"]),timeLandD[item]["Operator"],timeLandD[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
                    summary.insert(0, ["-", "-", "-","-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
                    summary.insert(0, ["Group","Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
                    for item in range(len(summary)):
                        for item0 in range(len(summary[item])):
                            worksheet.write(item,item0,summary[item][item0])
                
                if DATAx!=[]:
                    worksheet = workbook.add_worksheet("rawdataLight")
                    summary=[]
                    for item in range(len(DATAx)):
                        summary.append([DATAx[item]["Group"],DATAx[item]["SampleName"],DATAx[item]["Cellletter"],DATAx[item]["MeasDayTime"],DATAx[item]["CellSurface"],str(DATAx[item]["Voc"]),str(DATAx[item]["Jsc"]),str(DATAx[item]["FF"]),str(DATAx[item]["Eff"]),str(DATAx[item]["Pmpp"]),str(DATAx[item]["Vmpp"]),str(DATAx[item]["Jmpp"]),str(DATAx[item]["Roc"]),str(DATAx[item]["Rsc"]),str(DATAx[item]["VocFF"]),str(DATAx[item]["RscJsc"]),str(DATAx[item]["NbPoints"]),str(DATAx[item]["Delay"]),str(DATAx[item]["IntegTime"]),str(DATAx[item]["Vstart"]),str(DATAx[item]["Vend"]),str(DATAx[item]["Illumination"]),str(DATAx[item]["ScanDirection"]),str('%.2f' % float(DATAx[item]["ImaxComp"])),str(DATAx[item]["Isenserange"]),str(DATAx[item]["AreaJV"]),DATAx[item]["Operator"],DATAx[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
                    summary.insert(0, ["-", "-", "-","-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
                    summary.insert(0, ["Group","Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
                    for item in range(len(summary)):
                        for item0 in range(len(summary[item])):
                            worksheet.write(item,item0,summary[item][item0])
                
                if DATAdark!=[]:
                    worksheet = workbook.add_worksheet("rawdatadark")
                    summary=[]
                    for item in range(len(DATAdark)):
                        summary.append([DATAdark[item]["Group"],DATAdark[item]["SampleName"],DATAdark[item]["Cellletter"],DATAdark[item]["MeasDayTime"],DATAdark[item]["CellSurface"],str(DATAdark[item]["Voc"]),str(DATAdark[item]["Jsc"]),str(DATAdark[item]["FF"]),str(DATAdark[item]["Eff"]),str(DATAdark[item]["Pmpp"]),str(DATAdark[item]["Vmpp"]),str(DATAdark[item]["Jmpp"]),str(DATAdark[item]["Roc"]),str(DATAdark[item]["Rsc"]),str(DATAdark[item]["VocFF"]),str(DATAdark[item]["RscJsc"]),str(DATAdark[item]["NbPoints"]),DATAdark[item]["Delay"],DATAdark[item]["IntegTime"],DATAdark[item]["Vstart"],DATAdark[item]["Vend"],DATAdark[item]["Illumination"],DATAdark[item]["ScanDirection"],str('%.2f' % float(DATAdark[item]["ImaxComp"])),DATAdark[item]["Isenserange"],str(DATAdark[item]["AreaJV"]),DATAdark[item]["Operator"],DATAdark[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
                    summary.insert(0, ["-", "-", "-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
                    summary.insert(0, ["Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
                    for item in range(len(summary)):
                        for item0 in range(len(summary[item])):
                            worksheet.write(item,item0,summary[item][item0])
                            
                sorted_bestEff= sorted(bestEff, key=itemgetter('Eff'), reverse=True) 
                if sorted_bestEff!=[]:        
                    worksheet = workbook.add_worksheet("besteff")
                    summary=[]
                    for item in range(len(sorted_bestEff)):
                        summary.append([sorted_bestEff[item]["Group"],sorted_bestEff[item]["SampleName"],sorted_bestEff[item]["Cellletter"],sorted_bestEff[item]["MeasDayTime"],sorted_bestEff[item]["CellSurface"],str(sorted_bestEff[item]["Voc"]),str(sorted_bestEff[item]["Jsc"]),str(sorted_bestEff[item]["FF"]),str(sorted_bestEff[item]["Eff"]),str(sorted_bestEff[item]["Pmpp"]),str(sorted_bestEff[item]["Vmpp"]),str(sorted_bestEff[item]["Jmpp"]),str(sorted_bestEff[item]["Roc"]),str(sorted_bestEff[item]["Rsc"]),str(sorted_bestEff[item]["VocFF"]),str(sorted_bestEff[item]["RscJsc"]),str(sorted_bestEff[item]["NbPoints"]),sorted_bestEff[item]["Delay"],sorted_bestEff[item]["IntegTime"],sorted_bestEff[item]["Vstart"],sorted_bestEff[item]["Vend"],sorted_bestEff[item]["Illumination"],sorted_bestEff[item]["ScanDirection"],str('%.2f' % float(sorted_bestEff[item]["ImaxComp"])),sorted_bestEff[item]["Isenserange"],str(sorted_bestEff[item]["AreaJV"]),sorted_bestEff[item]["Operator"],sorted_bestEff[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
                    summary.insert(0, ["-", "-", "-", "-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
                    summary.insert(0, ["Group","Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
                    for item in range(len(summary)):
                        for item0 in range(len(summary[item])):
                            worksheet.write(item,item0,summary[item][item0])
                sorted_bestvocff= sorted(bestvocff, key=itemgetter('VocFF'), reverse=True) 
                if sorted_bestvocff!=[]: 
                    worksheet = workbook.add_worksheet("bestvocff")
                    summary=[]
                    for item in range(len(sorted_bestvocff)):
                        summary.append([sorted_bestvocff[item]["Group"], sorted_bestvocff[item]["SampleName"],sorted_bestvocff[item]["Cellletter"],sorted_bestvocff[item]["MeasDayTime"],sorted_bestvocff[item]["CellSurface"],str(sorted_bestvocff[item]["Voc"]),str(sorted_bestvocff[item]["Jsc"]),str(sorted_bestvocff[item]["FF"]),str(sorted_bestvocff[item]["Eff"]),str(sorted_bestvocff[item]["Pmpp"]),str(sorted_bestvocff[item]["Vmpp"]),str(sorted_bestvocff[item]["Jmpp"]),str(sorted_bestvocff[item]["Roc"]),str(sorted_bestvocff[item]["Rsc"]),str(sorted_bestvocff[item]["VocFF"]),str(sorted_bestvocff[item]["RscJsc"]),str(sorted_bestvocff[item]["NbPoints"]),sorted_bestvocff[item]["Delay"],sorted_bestvocff[item]["IntegTime"],sorted_bestvocff[item]["Vstart"],sorted_bestvocff[item]["Vend"],sorted_bestvocff[item]["Illumination"],sorted_bestvocff[item]["ScanDirection"],str('%.2f' % float(sorted_bestvocff[item]["ImaxComp"])),sorted_bestvocff[item]["Isenserange"],str(sorted_bestvocff[item]["AreaJV"]),sorted_bestvocff[item]["Operator"],sorted_bestvocff[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
                    summary.insert(0, ["-", "-", "-","-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
                    summary.insert(0, ["Group","Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
                    for item in range(len(summary)):
                        for item0 in range(len(summary[item])):
                            worksheet.write(item,item0,summary[item][item0])
                
                if DATAMPP!=[]: 
                    worksheet = workbook.add_worksheet("Pmpp")
                    summary=[]
                    for item in range(len(DATAMPP)):
                        summary.append([DATAMPP[item]["Group"],DATAMPP[item]["SampleName"],DATAMPP[item]["Cellletter"],DATAMPP[item]["MeasDayTime"],float('%.2f' % float(DATAMPP[item]["CellSurface"])),DATAMPP[item]["Delay"],DATAMPP[item]["IntegTime"],float(DATAMPP[item]["Vstep"]),float(DATAMPP[item]["Vstart"]),float('%.1f' % float(DATAMPP[item]["MppData"][2][-1])),DATAMPP[item]["Operator"],DATAMPP[item]["MeasComment"]])
                    summary.insert(0, ["Group","Sample Name", "Cell","MeasDayTime","Cell Surface","Delay","IntegTime","Vstep","Vstart","ExecTime","Operator","MeasComment"])
                    for item in range(len(summary)):
                        for item0 in range(len(summary[item])):
                            worksheet.write(item,item0,summary[item][item0])
                
                if DATAFV!=[]: 
                    worksheet = workbook.add_worksheet("fixedvoltage")
                    summary=[]
                    for item in range(len(DATAFV)):
                        summary.append([DATAFV[item]["Group"],DATAFV[item]["SampleName"],DATAFV[item]["Cellletter"],DATAFV[item]["MeasDayTime"],float('%.2f' % float(DATAFV[item]["CellSurface"])),DATAFV[item]["Delay"],DATAFV[item]["IntegTime"],DATAFV[item]["NbCycle"],float(DATAFV[item]["Vstep"]),float(DATAFV[item]["ExecTime"]),float(DATAFV[item]["TimeatZero"]),DATAFV[item]["Operator"],DATAFV[item]["MeasComment"]])
                    summary.insert(0, ["Group", "Sample Name", "Cell","MeasDayTime","Cell Surface","Delay","IntegTime","NbCycle","Initial voltage step", "Time at voltage bias", "Time at zero", "Operator","MeasComment"])
                    for item in range(len(summary)):
                        for item0 in range(len(summary[item])):
                            worksheet.write(item,item0,summary[item][item0])
                        
                if LandD!=[]:            
                    sorted_dataall = sorted(LandD, key=itemgetter('DepID')) 
                    for key, group in groupby(sorted_dataall, key=lambda x:x['DepID']):
                        partdat=list(group)
                        worksheet = workbook.add_worksheet(key)
                        summary=[]
                        for item in range(len(partdat)):
                            summary.append([partdat[item]["Group"],partdat[item]["SampleName"],partdat[item]["Cellletter"],partdat[item]["MeasDayTime"],partdat[item]["CellSurface"],str(partdat[item]["Voc"]),str(partdat[item]["Jsc"]),str(partdat[item]["FF"]),str(partdat[item]["Eff"]),str(partdat[item]["Pmpp"]),str(partdat[item]["Vmpp"]),str(partdat[item]["Jmpp"]),str(partdat[item]["Roc"]),str(partdat[item]["Rsc"]),str(partdat[item]["VocFF"]),str(partdat[item]["RscJsc"]),str(partdat[item]["NbPoints"]),partdat[item]["Delay"],partdat[item]["IntegTime"],partdat[item]["Vstart"],partdat[item]["Vend"],partdat[item]["Illumination"],partdat[item]["ScanDirection"],str('%.2f' % float(partdat[item]["ImaxComp"])),partdat[item]["Isenserange"],str(partdat[item]["AreaJV"]),partdat[item]["Operator"],partdat[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
                        summary.insert(0, ["-", "-", "-","-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
                        summary.insert(0, ["Group", "Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
                        for item in range(len(summary)):
                            for item0 in range(len(summary[item])):
                                worksheet.write(item,item0,summary[item][item0])
                                
                workbook.close()
        except:
            print("there's an issue with creating excel summary file")
            
        try:
            #stat graphs
            if self.AutoGraphs.get():
                #group
                plt.close("all")
                
                if len(samplesgroups)>1:
                    fig = plt.figure()
                    Effsubfig = fig.add_subplot(224) 
                    names=samplesgroups
                    valsRev=[]
                    for item in names:
                        valsRev.append([i["RevEff"] for i in grouplistdict if i["Group"]==item and "RevEff" in i])
                    valsFor=[]
                    for item in names:
                        valsFor.append([i["ForEff"] for i in grouplistdict if i["Group"]==item and "ForEff" in i])
                        
                    valstot=[]
                    Rev=[]
                    Forw=[]
                    namelist=[]
                    for i in range(len(names)):
                        if valsRev[i][0]==[] and valsFor[i][0]==[]:
                            print(" ")
                        else:
                            Rev.append(valsRev[i][0])
                            Forw.append(valsFor[i][0])
                            valstot.append(valsRev[i][0]+valsFor[i][0])
                            namelist.append(names[i])
                    
                    Effsubfig.boxplot(valstot,0,'',labels=namelist)
                    
                    for i in range(len(namelist)):
                        y=Rev[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Effsubfig.scatter(x,y,s=5,color='red', alpha=0.5)
                        y=Forw[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Effsubfig.scatter(x,y,s=5,color='blue', alpha=0.5)  
                    
                    #Effsubfig.set_xlabel('Red=reverse; Blue=forward')
                    
                    Effsubfig.set_ylabel('Efficiency (%)')
                    for item in ([Effsubfig.title, Effsubfig.xaxis.label, Effsubfig.yaxis.label] +
                                 Effsubfig.get_xticklabels() + Effsubfig.get_yticklabels()):
                        item.set_fontsize(4)
                    
                    Vocsubfig = fig.add_subplot(221) 
                    names=samplesgroups
                    valsRev=[]
                    for item in names:
                        valsRev.append([i["RevVoc"] for i in grouplistdict if i["Group"]==item and "RevVoc" in i])
                    valsFor=[]
                    for item in names:
                        valsFor.append([i["ForVoc"] for i in grouplistdict if i["Group"]==item and "ForVoc" in i])
                        
                    valstot=[]
                    Rev=[]
                    Forw=[]
                    namelist=[]
                    for i in range(len(names)):
                        if valsRev[i][0]==[] and valsFor[i][0]==[]:
                            print(" ")
                        else:
                            Rev.append(valsRev[i][0])
                            Forw.append(valsFor[i][0])
                            valstot.append(valsRev[i][0]+valsFor[i][0])
                            namelist.append(names[i])
                    
                    Vocsubfig.boxplot(valstot,0,'',labels=namelist)
                    
                    for i in range(len(namelist)):
                        y=Rev[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Vocsubfig.scatter(x,y,s=5,color='red', alpha=0.5)
                        y=Forw[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Vocsubfig.scatter(x,y,s=5,color='blue', alpha=0.5)  
                    
                    #Vocsubfig.set_xlabel('Red=reverse; Blue=forward')
                    
                    Vocsubfig.set_ylabel('Voc (mV)')
                    for item in ([Vocsubfig.title, Vocsubfig.xaxis.label, Vocsubfig.yaxis.label] +
                                 Vocsubfig.get_xticklabels() + Vocsubfig.get_yticklabels()):
                        item.set_fontsize(4)
                        
                    Jscsubfig = fig.add_subplot(222) 
                    names=samplesgroups
                    valsRev=[]
                    for item in names:
                        valsRev.append([i["RevJsc"] for i in grouplistdict if i["Group"]==item and "RevJsc" in i])
                    valsFor=[]
                    for item in names:
                        valsFor.append([i["ForJsc"] for i in grouplistdict if i["Group"]==item and "ForJsc" in i])
                        
                    valstot=[]
                    Rev=[]
                    Forw=[]
                    namelist=[]
                    for i in range(len(names)):
                        if valsRev[i][0]==[] and valsFor[i][0]==[]:
                            print(" ")
                        else:
                            Rev.append(valsRev[i][0])
                            Forw.append(valsFor[i][0])
                            valstot.append(valsRev[i][0]+valsFor[i][0])
                            namelist.append(names[i])
                    
                    Jscsubfig.boxplot(valstot,0,'',labels=namelist)
                    
                    for i in range(len(namelist)):
                        y=Rev[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Jscsubfig.scatter(x,y,s=5,color='red', alpha=0.5)
                        y=Forw[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Jscsubfig.scatter(x,y,s=5,color='blue', alpha=0.5)  
                    
                    #Jscsubfig.set_xlabel('Red=reverse; Blue=forward')
                    
                    Jscsubfig.set_ylabel('Jsc (mA/cm'+'\xb2'+')')
                    for item in ([Jscsubfig.title, Jscsubfig.xaxis.label, Jscsubfig.yaxis.label] +
                                 Jscsubfig.get_xticklabels() + Jscsubfig.get_yticklabels()):
                        item.set_fontsize(4)
                    
                    FFsubfig = fig.add_subplot(223) 
                    names=samplesgroups
                    valsRev=[]
                    for item in names:
                        valsRev.append([i["RevFF"] for i in grouplistdict if i["Group"]==item and "RevFF" in i])
                    valsFor=[]
                    for item in names:
                        valsFor.append([i["ForFF"] for i in grouplistdict if i["Group"]==item and "ForFF" in i])
                        
                    valstot=[]
                    Rev=[]
                    Forw=[]
                    namelist=[]
                    for i in range(len(names)):
                        if valsRev[i][0]==[] and valsFor[i][0]==[]:
                            print(" ")
                        else:
                            Rev.append(valsRev[i][0])
                            Forw.append(valsFor[i][0])
                            valstot.append(valsRev[i][0]+valsFor[i][0])
                            namelist.append(names[i])
                    
                    FFsubfig.boxplot(valstot,0,'',labels=namelist)
                    
                    for i in range(len(namelist)):
                        y=Rev[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            FFsubfig.scatter(x,y,s=5,color='red', alpha=0.5)
                        y=Forw[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            FFsubfig.scatter(x,y,s=5,color='blue', alpha=0.5)  
                    
                    #FFsubfig.set_xlabel('Red=reverse; Blue=forward')
                    
                    FFsubfig.set_ylabel('FF (%)')
                    for item in ([FFsubfig.title, FFsubfig.xaxis.label, FFsubfig.yaxis.label] +
                                 FFsubfig.get_xticklabels() + FFsubfig.get_yticklabels()):
                        item.set_fontsize(4)
                        
                    FFsubfig.annotate('Red=reverse; Blue=forward', xy=(1.3,-0.2), xycoords='axes fraction', fontsize=4,
                                horizontalalignment='right', verticalalignment='bottom')
                    annotation="#ofCells: "
                    for item in range(len(samplesgroups)):
                        if samplesgroups[item] in namelist:
                            annotation+=samplesgroups[item]+"=>"+str(grouplistdict[item]["numbCell"])+"; "
                    FFsubfig.annotate(annotation, xy=(1.3,-0.3), xycoords='axes fraction', fontsize=4,
                                horizontalalignment='right', verticalalignment='bottom')
                    
                    fig.subplots_adjust(wspace=.25)
                    fig.savefig(batchname+'_StatGroupgraph.png',dpi=300,bbox_inches="tight")
                    
                    
                    
                    plt.close("all")
                
                
                #time
                if DATAx[0]["Setup"]=="TFIV":
                    time=[float(i["MeasDayTime"].split()[1].split(':')[0])+ float(i["MeasDayTime"].split()[1].split(':')[1])/60 + float(i["MeasDayTime"].split()[1].split(':')[2])/3600 for i in DATAx]
                    Voct=[i["Voc"] for i in DATAx]
                    Jsct=[i["Jsc"] for i in DATAx]
                    FFt=[i["FF"] for i in DATAx]
                    Efft=[i["Eff"] for i in DATAx]
                    
                    fig = plt.figure()
                    Vocsubfig = fig.add_subplot(221) 
                    Vocsubfig.scatter(time, Voct, s=5, c='k', alpha=0.5)
                    Vocsubfig.set_ylabel('Voc (mV)')
                    for item in ([Vocsubfig.title, Vocsubfig.xaxis.label, Vocsubfig.yaxis.label] +
                                 Vocsubfig.get_xticklabels() + Vocsubfig.get_yticklabels()):
                        item.set_fontsize(8)
                    plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                    Vocsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                    
                    Jscsubfig = fig.add_subplot(222) 
                    Jscsubfig.scatter(time, Jsct, s=5, c='k', alpha=0.5)
                    Jscsubfig.set_ylabel('Jsc (mA/cm'+'\xb2'+')')
                    for item in ([Jscsubfig.title, Jscsubfig.xaxis.label, Jscsubfig.yaxis.label] +
                                 Jscsubfig.get_xticklabels() + Jscsubfig.get_yticklabels()):
                        item.set_fontsize(8)
                    plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                    Jscsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                    
                    FFsubfig = fig.add_subplot(223) 
                    FFsubfig.scatter(time, FFt, s=5, c='k', alpha=0.5)
                    FFsubfig.set_xlabel('Time')
                    FFsubfig.set_ylabel('FF (%)')
                    for item in ([FFsubfig.title, FFsubfig.xaxis.label, FFsubfig.yaxis.label] +
                                 FFsubfig.get_xticklabels() + FFsubfig.get_yticklabels()):
                        item.set_fontsize(8)
                    plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                    FFsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                    
                    Effsubfig = fig.add_subplot(224) 
                    Effsubfig.scatter(time, Efft, s=5, c='k', alpha=0.5)
                    Effsubfig.set_xlabel('Time')
                    Effsubfig.set_ylabel('Eff (%)')
                    for item in ([Effsubfig.title, Effsubfig.xaxis.label, Effsubfig.yaxis.label] +
                                 Effsubfig.get_xticklabels() + Effsubfig.get_yticklabels()):
                        item.set_fontsize(8)
                    plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                    Effsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                    
                    fig.subplots_adjust(wspace=.25)
                    fig.savefig(batchname+'_StatTimegraph.png',dpi=300,bbox_inches="tight")
                    plt.close("all")
                
                
                #Resistances
                
                Rsclist=[float(i["Rsc"]) for i in DATAx]
                Roclist=[float(i["Roc"]) for i in DATAx]
                Voct=[i["Voc"] for i in DATAx]
                Jsct=[i["Jsc"] for i in DATAx]
                FFt=[i["FF"] for i in DATAx]
                Efft=[i["Eff"] for i in DATAx]
                
                
                fig = plt.figure()
                Vocsubfig = fig.add_subplot(221) 
                Vocsubfig.scatter(Rsclist, Voct, s=5, c='k', alpha=0.5)
                Vocsubfig.set_ylabel('Voc (mV)')
                for item in ([Vocsubfig.title, Vocsubfig.xaxis.label, Vocsubfig.yaxis.label] +
                             Vocsubfig.get_xticklabels() + Vocsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                Vocsubfig.set_xlim(left=0)
                Vocsubfig.set_ylim(bottom=0)
                Vocsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                
                Jscsubfig = fig.add_subplot(222) 
                Jscsubfig.scatter(Rsclist, Jsct, s=5, c='k', alpha=0.5)
                Jscsubfig.set_ylabel('Jsc (mA/cm'+'\xb2'+')')
                for item in ([Jscsubfig.title, Jscsubfig.xaxis.label, Jscsubfig.yaxis.label] +
                             Jscsubfig.get_xticklabels() + Jscsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                Jscsubfig.set_xlim(left=0)
                Jscsubfig.set_ylim(bottom=0)
                Jscsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                FFsubfig = fig.add_subplot(223) 
                FFsubfig.scatter(Rsclist, FFt, s=5, c='k', alpha=0.5)
                FFsubfig.set_xlabel('Rsc')
                FFsubfig.set_ylabel('FF (%)')
                for item in ([FFsubfig.title, FFsubfig.xaxis.label, FFsubfig.yaxis.label] +
                             FFsubfig.get_xticklabels() + FFsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                FFsubfig.set_xlim(left=0)
                FFsubfig.set_ylim(bottom=0)
                FFsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                Effsubfig = fig.add_subplot(224) 
                Effsubfig.scatter(Rsclist, Efft, s=5, c='k', alpha=0.5)
                Effsubfig.set_xlabel('Rsc')
                Effsubfig.set_ylabel('Eff (%)')
                for item in ([Effsubfig.title, Effsubfig.xaxis.label, Effsubfig.yaxis.label] +
                             Effsubfig.get_xticklabels() + Effsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                Effsubfig.set_xlim(left=0)
                Effsubfig.set_ylim(bottom=0)
                Effsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                fig.subplots_adjust(wspace=.3)
                fig.savefig(batchname+'_StatRscgraph.png',dpi=300,bbox_inches="tight")
                plt.close("all")
                
                
                fig = plt.figure()
                Vocsubfig = fig.add_subplot(221) 
                Vocsubfig.scatter(Roclist, Voct, s=5, c='k', alpha=0.5)
                Vocsubfig.set_ylabel('Voc (mV)')
                for item in ([Vocsubfig.title, Vocsubfig.xaxis.label, Vocsubfig.yaxis.label] +
                             Vocsubfig.get_xticklabels() + Vocsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                Vocsubfig.set_xlim(left=0)
                Vocsubfig.set_ylim(bottom=0)
                Vocsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                Jscsubfig = fig.add_subplot(222) 
                Jscsubfig.scatter(Roclist, Jsct, s=5, c='k', alpha=0.5)
                Jscsubfig.set_ylabel('Jsc (mA/cm'+'\xb2'+')')
                for item in ([Jscsubfig.title, Jscsubfig.xaxis.label, Jscsubfig.yaxis.label] +
                             Jscsubfig.get_xticklabels() + Jscsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                Jscsubfig.set_xlim(left=0)
                Jscsubfig.set_ylim(bottom=0)
                Jscsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                FFsubfig = fig.add_subplot(223) 
                FFsubfig.scatter(Roclist, FFt, s=5, c='k', alpha=0.5)
                FFsubfig.set_xlabel('Roc')
                FFsubfig.set_ylabel('FF (%)')
                for item in ([FFsubfig.title, FFsubfig.xaxis.label, FFsubfig.yaxis.label] +
                             FFsubfig.get_xticklabels() + FFsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                FFsubfig.set_xlim(left=0)
                FFsubfig.set_ylim(bottom=0)
                FFsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                Effsubfig = fig.add_subplot(224) 
                Effsubfig.scatter(Roclist, Efft, s=5, c='k', alpha=0.5)
                Effsubfig.set_xlabel('Roc')
                Effsubfig.set_ylabel('Eff (%)')
                for item in ([Effsubfig.title, Effsubfig.xaxis.label, Effsubfig.yaxis.label] +
                             Effsubfig.get_xticklabels() + Effsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                Effsubfig.set_xlim(left=0)
                Effsubfig.set_ylim(bottom=0)
                Effsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                fig.subplots_adjust(wspace=.3)
                fig.savefig(batchname+'_StatRocgraph.png',dpi=300,bbox_inches="tight")
                plt.close("all")
                
                
                #stat graph with diff colors for ABC and Forw Rev, by substrate
                #get substrate number without run number
                if DATAx[0]["Setup"]=="TFIV":
                    try:
                        fig = plt.figure()
                        
                        VocAFy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward"]
                        VocAFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward"]
                        
                        VocBFy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward"]
                        VocBFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward"]
                        
                        VocCFy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward"]
                        VocCFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward"]
                        
                        VocSFy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='Single' and i["ScanDirection"]=="Forward"]
                        VocSFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='S' and i["ScanDirection"]=="Forward"]
                        
                        VocARy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse"]
                        VocARx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse"]
                        
                        VocBRy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse"]
                        VocBRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse"]
                        
                        VocCRy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse"]
                        VocCRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse"]
                        
                        VocSRy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='Single' and i["ScanDirection"]=="Reverse"]
                        VocSRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='S' and i["ScanDirection"]=="Reverse"]
                        
                        Vocsubfig = fig.add_subplot(221) 
                        Vocsubfig.scatter(VocAFx, VocAFy, s=5, facecolors='none', edgecolors='r', lw=0.5)
                        Vocsubfig.scatter(VocBFx, VocBFy, s=5, facecolors='none', edgecolors='g', lw=0.5)
                        Vocsubfig.scatter(VocCFx, VocCFy, s=5, facecolors='none', edgecolors='b', lw=0.5)
                        Vocsubfig.scatter(VocARx, VocARy, s=5, edgecolors='r', lw=0.5)
                        Vocsubfig.scatter(VocBRx, VocBRy, s=5, edgecolors='g', lw=0.5)
                        Vocsubfig.scatter(VocCRx, VocCRy, s=5, edgecolors='b', lw=0.5)
                        Vocsubfig.scatter(VocSFx, VocSFy, s=5, facecolors='none', edgecolors='k', lw=0.5)
                        Vocsubfig.scatter(VocSRx, VocSRy, s=5, edgecolors='k', lw=0.5)
                        Vocsubfig.set_ylabel('Voc (mV)')
                        Vocsubfig.set_xlabel("Sample #")
                        for item in ([Vocsubfig.title, Vocsubfig.xaxis.label, Vocsubfig.yaxis.label] +
                                     Vocsubfig.get_xticklabels() + Vocsubfig.get_yticklabels()):
                            item.set_fontsize(4)
                        Vocsubfig.set_ylim(bottom=0)
                        Vocsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                        
                        Vocsubfig.set_xticks(np.arange(float(min(VocAFx+VocBFx+VocCFx+VocSFx+VocARx+VocBRx+VocCRx+VocSRx))-0.5,float(max(VocAFx+VocBFx+VocCFx+VocSFx+VocARx+VocBRx+VocCRx+VocSRx))+0.5,1), minor=True)
                        #Vocsubfig.set_xticks(np.arange(float(min(VocAFx))-0.5,float(max(VocAFx))+0.5,1), minor=True)
                        Vocsubfig.xaxis.grid(False, which='major')
                        Vocsubfig.xaxis.grid(True, which='minor', color='k', linestyle='-', alpha=0.2)
                        
                        Vocsubfig.axis([float(min(VocAFx+VocBFx+VocCFx+VocSFx+VocARx+VocBRx+VocCRx+VocSRx))-0.5,float(max(VocAFx+VocBFx+VocCFx+VocSFx+VocARx+VocBRx+VocCRx+VocSRx))+0.5,0.5*float(min(VocAFy+VocBFy+VocCFy+VocSFy+VocARy+VocBRy+VocCRy+VocSRy)),1.1*float(max(VocAFy+VocBFy+VocCFy+VocSFy+VocARy+VocBRy+VocCRy+VocSRy))])
                        for axis in ['top','bottom','left','right']:
                          Vocsubfig.spines[axis].set_linewidth(0.5)
                        Vocsubfig.tick_params(axis='x', which='both',bottom='off', top='off')
                        
                        
                        
                        JscAFy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward"]
                        JscAFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward"]
                        
                        JscBFy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward"]
                        JscBFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward"]
                        
                        JscCFy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward"]
                        JscCFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward"]
                        
                        JscSFy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='Single' and i["ScanDirection"]=="Forward"]
                        JscSFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='S' and i["ScanDirection"]=="Forward"]
                        
                        JscARy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse"]
                        JscARx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse"]
                        
                        JscBRy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse"]
                        JscBRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse"]
                        
                        JscCRy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse"]
                        JscCRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse"]
                        
                        JscSRy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='Single' and i["ScanDirection"]=="Reverse"]
                        JscSRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='S' and i["ScanDirection"]=="Reverse"]
                        
                        
                        Jscsubfig = fig.add_subplot(222) 
                        Jscsubfig.scatter(JscAFx, JscAFy, s=5, facecolors='none', edgecolors='r', lw=0.5)
                        Jscsubfig.scatter(JscBFx, JscBFy, s=5, facecolors='none', edgecolors='g', lw=0.5)
                        Jscsubfig.scatter(JscCFx, JscCFy, s=5, facecolors='none', edgecolors='b', lw=0.5)
                        Jscsubfig.scatter(JscARx, JscARy, s=5, edgecolors='r', lw=0.5)
                        Jscsubfig.scatter(JscBRx, JscBRy, s=5, edgecolors='g', lw=0.5)
                        Jscsubfig.scatter(JscCRx, JscCRy, s=5, edgecolors='b', lw=0.5)
                        Jscsubfig.scatter(JscSFx, JscSFy, s=5, facecolors='none', edgecolors='k', lw=0.5)
                        Jscsubfig.scatter(JscSRx, JscSRy, s=5, edgecolors='k', lw=0.5)
                        Jscsubfig.set_ylabel('Jsc (mA/cm'+'\xb2'+')')
                        Jscsubfig.set_xlabel("Sample #")
                        for item in ([Jscsubfig.title, Jscsubfig.xaxis.label, Jscsubfig.yaxis.label] +
                                     Jscsubfig.get_xticklabels() + Jscsubfig.get_yticklabels()):
                            item.set_fontsize(4)
                        Jscsubfig.set_ylim(bottom=0)
                        Jscsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                        
                        Jscsubfig.set_xticks(np.arange(float(min(JscAFx+JscBFx+JscCFx+JscSFx+JscARx+JscBRx+JscCRx+JscSRx))-0.5,float(max(JscAFx+JscBFx+JscCFx+JscSFx+JscARx+JscBRx+JscCRx+JscSRx))+0.5,1), minor=True)
                        #Jscsubfig.set_xticks(np.arange(float(min(JscAFx))-0.5,float(max(JscAFx))+0.5,1), minor=True)
                        Jscsubfig.xaxis.grid(False, which='major')
                        Jscsubfig.xaxis.grid(True, which='minor', color='k', linestyle='-', alpha=0.2)
                        
                        Jscsubfig.axis([float(min(JscAFx+JscBFx+JscCFx+JscSFx+JscARx+JscBRx+JscCRx+JscSRx))-0.5,float(max(JscAFx+JscBFx+JscCFx+JscSFx+JscARx+JscBRx+JscCRx+JscSRx))+0.5,0.5*float(min(JscAFy+JscBFy+JscCFy+JscSFy+JscARy+JscBRy+JscCRy+JscSRy)),1.1*float(max(JscAFy+JscBFy+JscCFy+JscSFy+JscARy+JscBRy+JscCRy+JscSRy))])
                        for axis in ['top','bottom','left','right']:
                          Jscsubfig.spines[axis].set_linewidth(0.5)
                        Jscsubfig.tick_params(axis='x', which='both',bottom='off', top='off')
                        
                        
                        FFAFy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward"]
                        FFAFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward"]
                        
                        FFBFy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward"]
                        FFBFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward"]
                        
                        FFCFy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward"]
                        FFCFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward"]
                        
                        FFSFy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='Single' and i["ScanDirection"]=="Forward"]
                        FFSFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='S' and i["ScanDirection"]=="Forward"]
                        
                        FFARy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse"]
                        FFARx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse"]
                        
                        FFBRy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse"]
                        FFBRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse"]
                        
                        FFCRy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse"]
                        FFCRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse"]
                        
                        FFSRy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='Single' and i["ScanDirection"]=="Reverse"]
                        FFSRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='S' and i["ScanDirection"]=="Reverse"]
                        
                        
                        FFsubfig = fig.add_subplot(223) 
                        FFsubfig.scatter(FFAFx, FFAFy, s=5, facecolors='none', edgecolors='r', lw=0.5)
                        FFsubfig.scatter(FFBFx, FFBFy, s=5, facecolors='none', edgecolors='g', lw=0.5)
                        FFsubfig.scatter(FFCFx, FFCFy, s=5, facecolors='none', edgecolors='b', lw=0.5)
                        FFsubfig.scatter(FFARx, FFARy, s=5, edgecolors='r', lw=0.5)
                        FFsubfig.scatter(FFBRx, FFBRy, s=5, edgecolors='g', lw=0.5)
                        FFsubfig.scatter(FFCRx, FFCRy, s=5, edgecolors='b', lw=0.5)
                        FFsubfig.scatter(FFSFx, FFSFy, s=5, facecolors='none', edgecolors='k', lw=0.5)
                        FFsubfig.scatter(FFSRx, FFSRy, s=5, edgecolors='k', lw=0.5)
                        FFsubfig.set_ylabel('FF (%)')
                        FFsubfig.set_xlabel("Sample #")
                        for item in ([FFsubfig.title, FFsubfig.xaxis.label, FFsubfig.yaxis.label] +
                                     FFsubfig.get_xticklabels() + FFsubfig.get_yticklabels()):
                            item.set_fontsize(4)
                        FFsubfig.set_ylim(bottom=0)
                        FFsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                        
                        FFsubfig.set_xticks(np.arange(float(min(FFAFx+FFBFx+FFCFx+FFSFx+FFARx+FFBRx+FFCRx+FFSRx))-0.5,float(max(FFAFx+FFBFx+FFCFx+FFSFx+FFARx+FFBRx+FFCRx+FFSRx))+0.5,1), minor=True)
                        #FFsubfig.set_xticks(np.arange(float(min(FFAFx))-0.5,float(max(FFAFx))+0.5,1), minor=True)
                        FFsubfig.xaxis.grid(False, which='major')
                        FFsubfig.xaxis.grid(True, which='minor', color='k', linestyle='-', alpha=0.2)
                        
                        FFsubfig.axis([float(min(FFAFx+FFBFx+FFCFx+FFSFx+FFARx+FFBRx+FFCRx+FFSRx))-0.5,float(max(FFAFx+FFBFx+FFCFx+FFSFx+FFARx+FFBRx+FFCRx+FFSRx))+0.5,0.5*float(min(FFAFy+FFBFy+FFCFy+FFSFy+FFARy+FFBRy+FFCRy+FFSRy)),1.1*float(max(FFAFy+FFBFy+FFCFy+FFSFy+FFARy+FFBRy+FFCRy+FFSRy))])
                        for axis in ['top','bottom','left','right']:
                          FFsubfig.spines[axis].set_linewidth(0.5)
                        FFsubfig.tick_params(axis='x', which='both',bottom='off', top='off')
                        
                        
                        EffAFy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward"]
                        EffAFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward"]
                        
                        EffBFy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward"]
                        EffBFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward"]
                        
                        EffCFy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward"]
                        EffCFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward"]
                        
                        EffSFy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='Single' and i["ScanDirection"]=="Forward"]
                        EffSFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='S' and i["ScanDirection"]=="Forward"]
                        
                        EffARy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse"]
                        EffARx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse"]
                        
                        EffBRy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse"]
                        EffBRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse"]
                        
                        EffCRy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse"]
                        EffCRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse"]
                        
                        EffSRy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='Single' and i["ScanDirection"]=="Reverse"]
                        EffSRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='S' and i["ScanDirection"]=="Reverse"]
                        
                        
                        Effsubfig = fig.add_subplot(224) 
                        Effsubfig.scatter(EffAFx, EffAFy, s=5, facecolors='none', edgecolors='r', lw=0.5)
                        Effsubfig.scatter(EffBFx, EffBFy, s=5, facecolors='none', edgecolors='g', lw=0.5)
                        Effsubfig.scatter(EffCFx, EffCFy, s=5, facecolors='none', edgecolors='b', lw=0.5)
                        Effsubfig.scatter(EffARx, EffARy, s=5, edgecolors='r', lw=0.5)
                        Effsubfig.scatter(EffBRx, EffBRy, s=5, edgecolors='g', lw=0.5)
                        Effsubfig.scatter(EffCRx, EffCRy, s=5, edgecolors='b', lw=0.5)
                        Effsubfig.scatter(EffSFx, EffSFy, s=5, facecolors='none', edgecolors='k', lw=0.5)
                        Effsubfig.scatter(EffSRx, EffSRy, s=5, edgecolors='k', lw=0.5)
                        Effsubfig.set_ylabel('Eff (%)')
                        Effsubfig.set_xlabel("Sample #")
                        for item in ([Effsubfig.title, Effsubfig.xaxis.label, Effsubfig.yaxis.label] +
                                     Effsubfig.get_xticklabels() + Effsubfig.get_yticklabels()):
                            item.set_fontsize(4)
                        Effsubfig.set_ylim(bottom=0)
                        Effsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                        
                        Effsubfig.set_xticks(np.arange(float(min(EffAFx+EffBFx+EffCFx+EffSFx+EffARx+EffBRx+EffCRx+EffSRx))-0.5,float(max(EffAFx+EffBFx+EffCFx+EffSFx+EffARx+EffBRx+EffCRx+EffSRx))+0.5,1), minor=True)
                        Effsubfig.xaxis.grid(False, which='major')
                        Effsubfig.xaxis.grid(True, which='minor', color='k', linestyle='-', alpha=0.2)
                        
                        Effsubfig.axis([float(min(EffAFx+EffBFx+EffCFx+EffSFx+EffARx+EffBRx+EffCRx+EffSRx))-0.5,float(max(EffAFx+EffBFx+EffCFx+EffSFx+EffARx+EffBRx+EffCRx+EffSRx))+0.5,0.5*float(min(EffAFy+EffBFy+EffCFy+EffSFy+EffARy+EffBRy+EffCRy+EffSRy)),1.1*float(max(EffAFy+EffBFy+EffCFy+EffSFy+EffARy+EffBRy+EffCRy+EffSRy))])
                        for axis in ['top','bottom','left','right']:
                          Effsubfig.spines[axis].set_linewidth(0.5)
                        Effsubfig.tick_params(axis='x', which='both',bottom='off', top='off')
                        
                        
                        FFsubfig.annotate('Red=A; Green=B; Blue=C; Black=S; empty=Forward; full=Reverse;', xy=(1.55,-0.2), xycoords='axes fraction', fontsize=4,
                                        horizontalalignment='right', verticalalignment='bottom')
                        
                        fig.savefig(batchname+'_StatJVgraph.png',dpi=300,bbox_inches="tight")
                        plt.close("all")
                    except IndexError:
                        print("indexerror: list index out of range... it's probably an issue with sample names...")
        except:
            print("there's an issue with creating one of the stat graph")
        plt.close("all")
        
        self.window.destroy()
        self.destroy()
        self.__init__()
        
        if DATAx!=[]:          
            self.UpdateIVGraph()
        
        if DATAMPP!=[]:
#            print("il y a des mpp")
            self.mppnames = ()
            self.mppnames=self.SampleMppNames(DATAMPP)
            self.mppmenu = tk.Menu(self.mppmenubutton, tearoff=False)
            self.mppmenubutton.configure(menu=self.mppmenu)
            self.choicesmpp = {}
            for choice in range(len(self.mppnames)):
                self.choicesmpp[choice] = tk.IntVar(value=0)
                self.mppmenu.add_checkbutton(label=self.mppnames[choice], variable=self.choicesmpp[choice], 
                                     onvalue=1, offvalue=0, command = self.UpdateMppGraph0)
            self.UpdateMppGraph0() 
        self.UpdateGroupGraph(1)
        self.updateTable()
        
#%%######################################################################
        
    def CreateWindowExportAA(self):
        self.window = tk.Toplevel()
        self.window.wm_title("Export Auto-Analysis")
        center(self.window)
        self.window.geometry("360x100")
        self.windowRef.destroy()
        self.CheckXlsxSum = IntVar()
        legend=Checkbutton(self.window,text='Xlsx Summary',variable=self.CheckXlsxSum, 
                           onvalue=1,offvalue=0,height=1, width=10)
        legend.grid(row=0, column=0, columnspan=10)
        self.CheckXlsxSum.set(1)
        self.AutoGraphs = IntVar()
        legend=Checkbutton(self.window,text='Auto-Graphs',variable=self.AutoGraphs, 
                           onvalue=1,offvalue=0,height=1, width=10)
        legend.grid(row=0, column=11, columnspan=10)
        self.AutoGraphs.set(1)
        self.TxtforOrigin = IntVar()
        legend=Checkbutton(self.window,text='Txt for Origin',variable=self.TxtforOrigin, 
                           onvalue=1,offvalue=0,height=1, width=10)
        legend.grid(row=0, column=23, columnspan=10)
        self.TxtforOrigin.set(1)
        
        label = tk.Label(self.window, text="...this window will be automatically shut down when the task is completed...", font=("Helvetica", 6))
        label.grid(row=2, column=0,columnspan=30)
        
        self.ExportAll = Button(self.window, text="Start Auto-Analysis",
                            command = self.ExportAutoAnalysis)
        self.ExportAll.grid(row=1, column=0, columnspan=30,rowspan=1) 
     
        
    def AskforRefcells(self):
        global DATA
        
        self.windowRef = tk.Toplevel()
        self.windowRef.wm_title("Save .iv or load to DB?")
        center(self.windowRef)
        self.windowRef.geometry("290x100")
        
        if DATA!=[]:
            Button(self.windowRef, text="save all .iv",
                                command =self.SaveAllrawdatafiles).pack()
            Button(self.windowRef, text="save to database",
                                command =self.WriteJVtoDatabase).pack()
            Button(self.windowRef, text="No! take me to the autoanalysis!",
                                command = self.CreateWindowExportAA).pack()
    
    def WriteJVtoDatabase(self):
        global DATA, DATAdark, DATAMPP
        print("writting...")
        
        #connection to DB
        path =filedialog.askopenfilenames(title="Please select the DB file")[0]
        self.db_conn=sqlite3.connect(path)
        self.theCursor=self.db_conn.cursor()
       
        #for light&dark data
        print("JVs...")
        allDATA=DATA+DATAdark
        for i in range(len(allDATA)):
            batchname=allDATA[i]["DepID"].split("_")[0]
            self.theCursor.execute("SELECT id FROM batch WHERE batchname=?",(batchname,))
            batch_id_exists = self.theCursor.fetchone()[0]
            self.theCursor.execute("SELECT id FROM samples WHERE samplename=?",(allDATA[i]["DepID"],))            
            sample_id_exists = self.theCursor.fetchone()[0]
            
#            print(allDATA[i]["Cellletter"])
            
            self.theCursor.execute("SELECT id FROM cells WHERE samples_id=? AND batch_id=?",(sample_id_exists,batch_id_exists))            
            cellletter_id_exists = self.theCursor.fetchall()
            if len(cellletter_id_exists)>1:
                self.theCursor.execute("SELECT id FROM cells WHERE cellname=? AND samples_id=? AND batch_id=?",(allDATA[i]["Cellletter"],sample_id_exists,batch_id_exists))            
                cellletter_id_exists = self.theCursor.fetchone()[0]
#                print(cellletter_id_exists)
            else:
                cellletter_id_exists=cellletter_id_exists[0][0]
            print(cellletter_id_exists)
            if batch_id_exists and sample_id_exists and cellletter_id_exists:
                try:
                    self.db_conn.execute("""INSERT INTO JVmeas (
                                    DateTimeJV,
                                    Eff,
                                    Voc,
                                    Jsc,
                                    FF,
                                    Vmpp,
                                    Jmpp,
                                    Pmpp,
                                    Roc,
                                    Rsc,
                                    ScanDirect,
                                    Delay,
                                    IntegTime,
                                    CellArea,
                                    Vstart,
                                    Vend,
                                    Setup,
                                    NbPoints,
                                    ImaxComp,
                                    Isenserange,
                                    Operator,
                                    GroupJV,
                                    IlluminationIntensity,
                                    commentJV,
                                    linktorawdata,
                                    samples_id,
                                    batch_id,
                                    cells_id
                                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                                (    allDATA[i]["MeasDayTime"],
                                     allDATA[i]["Eff"],
                                     allDATA[i]["Voc"],
                                     allDATA[i]["Jsc"],
                                     allDATA[i]["FF"],
                                     allDATA[i]["Vmpp"],
                                     allDATA[i]["Jmpp"],
                                     allDATA[i]["Pmpp"],
                                     allDATA[i]["Roc"],
                                     allDATA[i]["Rsc"],
                                     allDATA[i]["ScanDirection"],
                                     allDATA[i]["Delay"],
                                     allDATA[i]["IntegTime"],
                                     allDATA[i]["CellSurface"],
                                     allDATA[i]["Vstart"],
                                     allDATA[i]["Vend"],
                                     allDATA[i]["Setup"],
                                     allDATA[i]["NbPoints"],
                                     allDATA[i]["ImaxComp"],
                                     allDATA[i]["Isenserange"],
                                     allDATA[i]["Operator"],
                                     allDATA[i]["Group"],
                                     allDATA[i]["Illumination"],
                                     allDATA[i]["MeasComment"],
                                     allDATA[i]["filepath"],
                                     sample_id_exists,
                                     batch_id_exists,
                                     cellletter_id_exists))
    
                    self.db_conn.commit()
                except sqlite3.IntegrityError:
                    print("the file already exists in the DB")
        
        #for mpp data
        
        print("mpps...")
        for i in range(len(DATAMPP)):
            batchname=DATAMPP[i]["DepID"].split("_")[0]
            self.theCursor.execute("SELECT id FROM batch WHERE batchname=?",(batchname,))
            batch_id_exists = self.theCursor.fetchone()[0]
#            print(batch_id_exists)
            self.theCursor.execute("SELECT id FROM samples WHERE samplename=?",(DATAMPP[i]["DepID"],))            
            sample_id_exists = self.theCursor.fetchone()[0]
#            print(sample_id_exists)
            self.theCursor.execute("SELECT id FROM cells WHERE samples_id=? AND batch_id=?",(sample_id_exists,batch_id_exists))            
            cellletter_id_exists = self.theCursor.fetchall()
            if len(cellletter_id_exists)>1:
                self.theCursor.execute("SELECT id FROM cells WHERE cellname=? AND samples_id=? AND batch_id=?",(DATAMPP[i]["Cellletter"],sample_id_exists,batch_id_exists))            
                cellletter_id_exists = self.theCursor.fetchone()[0]
            else:
                cellletter_id_exists=cellletter_id_exists[0][0]
            print(cellletter_id_exists)
            if batch_id_exists and sample_id_exists and cellletter_id_exists:
                try:
                    self.db_conn.execute("""INSERT INTO MPPmeas (
                            linktorawdata,
                            commentmpp,
                            DateTimeMPP,
                            CellArea,
                            Vstep,
                            Vstart,
                            Operator,
                            TrackingDuration,
                            PowerEnd,
                            PowerAvg,
                            samples_id,
                            batch_id,
                            cells_id
                            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (   DATAMPP[i]["filepath"],
                            DATAMPP[i]["MeasComment"],
                            DATAMPP[i]["MeasDayTime"],
                            DATAMPP[i]["CellSurface"],
                            DATAMPP[i]["Vstep"],
                            DATAMPP[i]["Vstart"],
                            DATAMPP[i]["Operator"],
                            DATAMPP[i]["trackingduration"],
                            DATAMPP[i]["PowerEnd"], 
                            DATAMPP[i]["PowerAvg"], 
                            sample_id_exists,
                            batch_id_exists,
                            cellletter_id_exists))
                    self.db_conn.commit()
                except sqlite3.IntegrityError:
                    print("the file already exists in the DB")
#                print("done")
        
        #disconnect from DB
        self.theCursor.close()
        self.db_conn.close()
        
        #exit window
        print("it's in the DB!")
        messagebox.askokcancel("", "it's all in the DB!")
        self.windowRef.destroy()
        self.CreateWindowExportAA()

    
    def SaveReferenceCells(self):
        global DATA
        
        takenforexport=[]
        for name, var in self.choicesRef.items():
            takenforexport.append(var.get())
        #print(takenforexport)
        m=[]
        indices=[]
        for i in range(len(takenforexport)):
            if takenforexport[i]==1:
                indices.append(i)
                m.append(self.listofsamples[i])
            else:
                m.append("999")
        #print(indices)

        pathtofolder="//sti1files.epfl.ch/pv-lab/pvlab-commun/Groupe-Perovskite/Experiments/CellParametersFollowUP/"
        
        for item in indices:
            pathtosave=pathtofolder+self.RefCelltype.get()+"/"+m[item]+".iv"
            shutil.copy(DATA[item]["filepath"], pathtosave)
        
        
        self.CreateWindowExportAA()
    
    def SaveAllrawdatafiles(self):
        global DATA
        
        current_path = os.getcwd()
        folderName = filedialog.askdirectory(title = "choose a folder to export the .iv files", initialdir=os.path.dirname(current_path))
        os.chdir(folderName)
        
        for item in DATA:
            datetime=item["MeasDayTime"]
            datetime=datetime.replace(':','')
            datetime=datetime.replace('-','')
            datetime=datetime.replace('.','')
            datetime=datetime.replace(' ','')
            shutil.copy(item["filepath"], item["SampleName"]+'_'+datetime+'.iv')
        self.CreateWindowExportAA()
    

    def SaveSession(self):
        global DATA, DATAMPP, DATAdark, DATAFV, IVlegendMod, MPPlegendMod
        global testdata, DATAJVforexport, DATAJVtabforexport, DATAmppforexport, DATAgroupforexport
        global takenforplot, IVlinestyle, MPPlinestyle, samplesgroups
        global listofanswer, listoflinestyle, listofcolorstyle
        
        directory = filedialog.askdirectory()
        if not os.path.exists(directory):
            os.makedirs(directory)
            os.chdir(directory)
        else :
            os.chdir(directory)
        
        pickle.dump(DATA,open('DATA.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAdark,open('DATAdark.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAMPP,open('DATAMPP.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAMPP,open('DATAFV.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)        
        pickle.dump(IVlegendMod,open('IVlegendMod.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(MPPlegendMod,open('MPPlegendMod.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)

        pickle.dump(testdata,open('testdata.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAJVforexport,open('DATAJVforexport.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAJVtabforexport,open('DATAJVtabforexport.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAmppforexport,open('DATAmppforexport.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)        
        pickle.dump(DATAgroupforexport,open('DATAgroupforexport.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)

        pickle.dump(takenforplot,open('takenforplot.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(IVlinestyle,open('IVlinestyle.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(MPPlinestyle,open('MPPlinestyle.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(samplesgroups,open('samplesgroups.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL) 
        
        pickle.dump(listofanswer,open('listofanswer.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(listoflinestyle,open('listoflinestyle.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(listofcolorstyle,open('listofcolorstyle.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL) 
        
        print("dumped")
        """
        try:
            self.dumpfilename = filedialog.asksaveasfilename(defaultextension=".pkl")
            dill.dump_session(self.dumpfilename)
        except:
            print("there is an exception")
        """
        
        
    def LoadSession(self):
        global DATA, DATAMPP, DATAdark, DATAFV, IVlegendMod, MPPlegendMod
        global testdata, DATAJVforexport, DATAJVtabforexport, DATAmppforexport, DATAgroupforexport
        global takenforplot, IVlinestyle, MPPlinestyle, samplesgroups
        global listofanswer, listoflinestyle, listofcolorstyle
        

        try:
            path = filedialog.askdirectory()
            os.chdir(path)
        except:
            print("there is an exception")
        
        DATA = pickle.load(open('DATA.pkl','rb'))
        DATAdark = pickle.load(open('DATAdark.pkl','rb'))
        DATAMPP = pickle.load(open('DATAMPP.pkl','rb'))
        DATAFV = pickle.load(open('DATAFV.pkl','rb'))
        IVlegendMod = pickle.load(open('IVlegendMod.pkl','rb'))
        MPPlegendMod = pickle.load(open('MPPlegendMod.pkl','rb'))
        testdata = pickle.load(open('testdata.pkl','rb'))
        DATAJVforexport = pickle.load(open('DATAJVforexport.pkl','rb'))
        DATAJVtabforexport = pickle.load(open('DATAJVtabforexport.pkl','rb'))
        DATAmppforexport = pickle.load(open('DATAmppforexport.pkl','rb'))
        DATAgroupforexport = pickle.load(open('DATAgroupforexport.pkl','rb'))
        takenforplot = pickle.load(open('takenforplot.pkl','rb'))
        IVlinestyle = pickle.load(open('IVlinestyle.pkl','rb'))
        MPPlinestyle = pickle.load(open('MPPlinestyle.pkl','rb'))
        samplesgroups = pickle.load(open('samplesgroups.pkl','rb'))
        listofanswer = pickle.load(open('listofanswer.pkl','rb'))
        listoflinestyle = pickle.load(open('listoflinestyle.pkl','rb'))
        listofcolorstyle = pickle.load(open('listofcolorstyle.pkl','rb'))
        
        """
        try:
            self.dumpfilename = filedialog.asksaveasfilename(defaultextension=".pkl")
            dill.load_session(self.dumpfilename)
        except:
            print("there is an exception")
        """
        print("loaded")
        if DATA!=[]:
            self.UpdateIVGraph()
            self.updateTable()
            
        if DATAMPP!=[]:
            #print("il y a des mpp")
            self.mppnames = ()
            self.mppnames=self.SampleMppNames(DATAMPP)
            self.mppmenu = tk.Menu(self.mppmenubutton, tearoff=False)
            self.mppmenubutton.configure(menu=self.mppmenu)
            self.choicesmpp = {}
            for choice in range(len(self.mppnames)):
                self.choicesmpp[choice] = tk.IntVar(value=0)
                self.mppmenu.add_checkbutton(label=self.mppnames[choice], variable=self.choicesmpp[choice], 
                                     onvalue=1, offvalue=0, command = self.UpdateMppGraph)
            self.UpdateMppGraph

#%%######################################################################
    
    def GiveIVatitle(self):
        self.window = tk.Toplevel()
        self.window.wm_title("Change title of IV graph")
        center(self.window)
        self.window.geometry("325x55")
        self.titleIV = tk.StringVar()
        entry=Entry(self.window, textvariable=self.titleIV,width=40)
        entry.grid(row=0,column=0,columnspan=1)
        self.addtitlebutton = Button(self.window, text="Update",
                            command = self.giveivatitleupdate)
        self.addtitlebutton.grid(row=1, column=0, columnspan=1)
    def giveivatitleupdate(self): 
        global titIV
        titIV=1
        self.UpdateIVGraph()
        
    
    ################
    class PopulateListofSampleStyling(tk.Frame):
        def __init__(self, root):
    
            tk.Frame.__init__(self, root)
            self.canvas0 = tk.Canvas(root, borderwidth=0, background="#ffffff")
            self.frame = tk.Frame(self.canvas0, background="#ffffff")
            self.vsb = tk.Scrollbar(root, orient="vertical", command=self.canvas0.yview)
            self.canvas0.configure(yscrollcommand=self.vsb.set)
    
            self.vsb.pack(side="right", fill="y")
            self.canvas0.pack(side="left", fill="both", expand=True)
            self.canvas0.create_window((4,4), window=self.frame, anchor="nw", 
                                      tags="self.frame")
    
            self.frame.bind("<Configure>", self.onFrameConfigure)
    
            self.populate()
    
        def populate(self):
            global DATA
            global takenforplot
            global IVlegendMod
            global IVlinestyle
            global colorstylelist
            global listofanswer
            global listoflinestyle
            global listofcolorstyle
            
            listofanswer=[]
            listoflinestyle=[]
            listofcolorstyle=[]
            
            for item in range(len(IVlegendMod)):
                listofanswer.append(IVlegendMod[item][1])
            
            for item in range(len(IVlinestyle)):
                listoflinestyle.append(IVlinestyle[item][1])
                listofcolorstyle.append(IVlinestyle[item][2])
            rowpos=1
            
            for itemm in takenforplot:
                for rowitem in range(len(IVlegendMod)):
                    if IVlegendMod[rowitem][0] == itemm:
                        label=tk.Label(self.frame,text=IVlegendMod[rowitem][0],fg='black',background='white')
                        label.grid(row=rowpos,column=0, columnspan=1)
                        textinit = tk.StringVar()
                        #self.listofanswer.append(Entry(self.window,textvariable=textinit))
                        listofanswer[rowitem]=Entry(self.frame,textvariable=textinit)
                        textinit.set(IVlegendMod[rowitem][1])
                        listofanswer[rowitem].grid(row=rowpos,column=1, columnspan=2)
            
                        linestylelist = ["-","--","-.",":"]
                        listoflinestyle[rowitem]=tk.StringVar()
                        listoflinestyle[rowitem].set(IVlinestyle[rowitem][1]) # default choice
                        self.dropJVstyle=OptionMenu(self.frame, listoflinestyle[rowitem], *linestylelist, command=())
                        self.dropJVstyle.grid(row=rowpos, column=4, columnspan=2)

                        self.positioncolor=rowitem
                        JVcolstyle=Button(self.frame, text='Select Color', foreground=listofcolorstyle[rowitem], command=partial(self.getColor,rowitem))
                        JVcolstyle.grid(row=rowpos, column=6, columnspan=2)

                        rowpos=rowpos+1
        
        def getColor(self,rowitem):
            global listofcolorstyle
            color = colorchooser.askcolor() 
            listofcolorstyle[rowitem]=color[1]
            
            
        def onFrameConfigure(self, event):
            '''Reset the scroll region to encompass the inner frame'''
            self.canvas0.configure(scrollregion=self.canvas0.bbox("all"))
            
            
    class Drag_and_Drop_Listbox(tk.Listbox):
        #A tk listbox with drag'n'drop reordering of entries.
        def __init__(self, master, **kw):
            #kw['selectmode'] = tk.MULTIPLE
            kw['selectmode'] = tk.SINGLE
            kw['activestyle'] = 'none'
            tk.Listbox.__init__(self, master, kw)
            self.bind('<Button-1>', self.getState, add='+')
            self.bind('<Button-1>', self.setCurrent, add='+')
            self.bind('<B1-Motion>', self.shiftSelection)
            self.curIndex = None
            self.curState = None
        def setCurrent(self, event):
            ''' gets the current index of the clicked item in the listbox '''
            self.curIndex = self.nearest(event.y)
        def getState(self, event):
            ''' checks if the clicked item in listbox is selected '''
            #i = self.nearest(event.y)
            #self.curState = self.selection_includes(i)
            self.curState = 1
        def shiftSelection(self, event):
            ''' shifts item up or down in listbox '''
            i = self.nearest(event.y)
            if self.curState == 1:
              self.selection_set(self.curIndex)
            else:
              self.selection_clear(self.curIndex)
            if i < self.curIndex:
              # Moves up
              x = self.get(i)
              selected = self.selection_includes(i)
              self.delete(i)
              self.insert(i+1, x)
              if selected:
                self.selection_set(i+1)
              self.curIndex = i
            elif i > self.curIndex:
              # Moves down
              x = self.get(i)
              selected = self.selection_includes(i)
              self.delete(i)
              self.insert(i-1, x)
              if selected:
                self.selection_set(i-1)
              self.curIndex = i
              

    def reorder(self): 
        global takenforplot
        self.reorderwindow = tk.Tk()
        center(self.reorderwindow)
        self.listbox = self.Drag_and_Drop_Listbox(self.reorderwindow)
        for name in takenforplot:
          self.listbox.insert(tk.END, name)
          self.listbox.selection_set(0)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(self.listbox, orient="vertical")
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        printbut = tk.Button(self.reorderwindow, text="reorder",
                                    command = self.printlist)
        printbut.pack()
        self.reorderwindow.mainloop()    
            
    def printlist(self):
        global takenforplot
        takenforplot=list(self.listbox.get(0,tk.END))
        self.UpdateIVLegMod()
        self.reorderwindow.destroy()
            
            
    def ChangeLegendIVgraph(self):
        
        if self.CheckIVLegend.get()==1:
            self.window = tk.Toplevel()
            self.window.wm_title("Change Legends")
            center(self.window)
            self.window.geometry("450x350")
            self.changeIVlegend = Button(self.window, text="Update",
                                command = self.UpdateIVLegMod)
            self.changeIVlegend.pack()
            self.changeIVorder = Button(self.window, text="Reorder",
                                command = self.reorder)
            self.changeIVorder.pack()
            
            
            self.PopulateListofSampleStyling(self.window).pack(side="top", fill="both", expand=True)
    
    def UpdateIVLegMod(self):
        global IVlegendMod
        global IVlinestyle
        global listofanswer
        global listoflinestyle
        global listofcolorstyle
        
                
        leglist=[]
        for e in listofanswer:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        
        for item in range(len(IVlegendMod)):
            IVlegendMod[item][1]=leglist[item]
        
        leglist=[]
        for e in listoflinestyle:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        #leglist=[e.get() for e in self.listoflinestyle]
        for item in range(len(IVlinestyle)):
            IVlinestyle[item][1]=leglist[item]
        
        leglist=[]
        for e in listofcolorstyle:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        #leglist=[e.get() for e in self.listofcolorstyle]
        for item in range(len(IVlinestyle)):
            IVlinestyle[item][2]=leglist[item]
        
        self.UpdateIVGraph()
        self.window.destroy()
        self.ChangeLegendIVgraph()
    ################
    
    class PopulateListofSampleStylingMPP(tk.Frame):
        def __init__(self, root):
    
            tk.Frame.__init__(self, root)
            self.canvas0 = tk.Canvas(root, borderwidth=0, background="#ffffff")
            self.frame = tk.Frame(self.canvas0, background="#ffffff")
            self.vsb = tk.Scrollbar(root, orient="vertical", command=self.canvas0.yview)
            self.canvas0.configure(yscrollcommand=self.vsb.set)
    
            self.vsb.pack(side="right", fill="y")
            self.canvas0.pack(side="left", fill="both", expand=True)
            self.canvas0.create_window((4,4), window=self.frame, anchor="nw", 
                                      tags="self.frame")
    
            self.frame.bind("<Configure>", self.onFrameConfigure)
    
            self.populate()
    
        def populate(self):
            global DATAMPP
            global takenforplotmpp
            global MPPlegendMod
            global MPPlinestyle
            global colorstylelist
            global listofanswer
            global listoflinestyle
            global listofcolorstyle
            
            listofanswer=[]
            listoflinestyle=[]
            listofcolorstyle=[]
            
            for item in range(len(MPPlegendMod)):
                listofanswer.append(MPPlegendMod[item][1])
            
            for item in range(len(MPPlinestyle)):
                listoflinestyle.append(MPPlinestyle[item][1])
                listofcolorstyle.append(MPPlinestyle[item][2])
            rowpos=1
            
            for itemm in takenforplotmpp:
                for rowitem in range(len(MPPlegendMod)):
                    if MPPlegendMod[rowitem][0] == itemm:
                        label=tk.Label(self.frame,text=MPPlegendMod[rowitem][0],fg='black',background='white')
                        label.grid(row=rowpos,column=0, columnspan=1)
                        textinit = tk.StringVar()
                        #self.listofanswer.append(Entry(self.window,textvariable=textinit))
                        listofanswer[rowitem]=Entry(self.frame,textvariable=textinit)
                        textinit.set(MPPlegendMod[rowitem][1])
                        listofanswer[rowitem].grid(row=rowpos,column=1, columnspan=2)
            
                        linestylelist = ["-","--","-.",":"]
                        listoflinestyle[rowitem]=tk.StringVar()
                        listoflinestyle[rowitem].set(MPPlinestyle[rowitem][1]) # default choice
                        self.dropMPPstyle=OptionMenu(self.frame, listoflinestyle[rowitem], *linestylelist, command=())
                        self.dropMPPstyle.grid(row=rowpos, column=4, columnspan=2)

                        self.positioncolor=rowitem
                        Button(self.frame, text='Select Color', foreground=listofcolorstyle[rowitem], command=partial(self.getColor,rowitem)).grid(row=rowpos, column=6, columnspan=2)

                        rowpos=rowpos+1
        
        def getColor(self,rowitem):
            global listofcolorstyle
            color = colorchooser.askcolor()
            listofcolorstyle[rowitem]=color[1]
            
            
        def onFrameConfigure(self, event):
            '''Reset the scroll region to encompass the inner frame'''
            self.canvas0.configure(scrollregion=self.canvas0.bbox("all"))

    def reordermpp(self): 
        global takenforplotmpp

        self.reorderwindow = tk.Tk()
        center(self.reorderwindow)
        self.listbox = self.Drag_and_Drop_Listbox(self.reorderwindow)
        for name in takenforplotmpp:
          self.listbox.insert(tk.END, name)
          self.listbox.selection_set(0)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(self.listbox, orient="vertical")
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        Button(self.reorderwindow, text="reorder",command = self.printlistmpp).pack()
        self.reorderwindow.mainloop()    
            
    def printlistmpp(self):
        global takenforplotmpp
        takenforplotmpp=list(self.listbox.get(0,tk.END))
        self.UpdateMPPLegMod()
        self.reorderwindow.destroy()
            
    def ChangeLegendMPPgraph(self):
        global takenforplotmpp
        global MPPlegendMod
        
        if self.CheckmppLegend.get()==1:
            
            self.window = tk.Toplevel()
            self.window.wm_title("Change Legends")
            center(self.window)
            self.window.geometry("400x300")
            Button(self.window, text="Update",command = self.UpdateMPPLegMod).pack()
            Button(self.window, text="Reorder",command = self.reordermpp).pack()
            
            self.PopulateListofSampleStylingMPP(self.window).pack(side="top", fill="both", expand=True)
        
       
    def UpdateMPPLegMod(self):
        global MPPlegendMod
        global MPPlinestyle
        global listofanswer
        global listoflinestyle
        global listofcolorstyle


        leglist=[]
        for e in listofanswer:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        
        for item in range(len(MPPlegendMod)):
            MPPlegendMod[item][1]=leglist[item]

        leglist=[]
        for e in listoflinestyle:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        #leglist=[e.get() for e in self.listoflinestyle]
        for item in range(len(MPPlinestyle)):
            MPPlinestyle[item][1]=leglist[item]
        
        leglist=[]
        for e in listofcolorstyle:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        #leglist=[e.get() for e in self.listofcolorstyle]
        for item in range(len(MPPlinestyle)):
            MPPlinestyle[item][2]=leglist[item]
        
        self.UpdateMppGraph()
        self.window.destroy()
        self.ChangeLegendMPPgraph()
        
    
    def GiveMPPatitle(self):
        self.window = tk.Toplevel()
        self.window.wm_title("Change title of Mpp graph")
        center(self.window)
        self.window.geometry("325x55")
        self.titlempp = tk.StringVar()
        entry=Entry(self.window, textvariable=self.titlempp,width=40)
        entry.grid(row=0,column=0,columnspan=1)
        self.addtitlebutton = Button(self.window, text="Update",
                            command = self.givemppatitleupdate)
        self.addtitlebutton.grid(row=1, column=0, columnspan=1)
    def givemppatitleupdate(self): 
        global titmpp
        titmpp=1
        self.UpdateMppGraph()
 
#########################################################
#########################################################       
    #Change cell area
    class PopulateListofSampleChangeArea(tk.Frame):
        def __init__(self, root):
    
            tk.Frame.__init__(self, root)
            self.canvas0 = tk.Canvas(root, borderwidth=0, background="#ffffff")
            self.frame = tk.Frame(self.canvas0, background="#ffffff")
            self.vsb = tk.Scrollbar(root, orient="vertical", command=self.canvas0.yview)
            self.canvas0.configure(yscrollcommand=self.vsb.set)
    
            self.vsb.pack(side="right", fill="y")
            self.canvas0.pack(side="left", fill="both", expand=True)
            self.canvas0.create_window((4,4), window=self.frame, anchor="nw", 
                                      tags="self.frame")
    
            self.frame.bind("<Configure>", self.onFrameConfigure)
    
            self.populate()
    
        def populate(self):
            global DATA
            global listofanswer
            
            listofanswer=[]
            
            
            for item in range(len(DATA)):
                listofanswer.append(DATA[item]["CellSurface"])
                
            rowpos=1
            
            for rowitem in range(len(DATA)):
                label=tk.Label(self.frame,text=DATA[rowitem]["SampleName"],fg='black',background='white')
                label.grid(row=rowpos,column=0, columnspan=1)
                textinit = tk.StringVar()
                #self.listofanswer.append(Entry(self.window,textvariable=textinit))
                listofanswer[rowitem]=Entry(self.frame,textvariable=textinit)
                textinit.set(DATA[rowitem]["CellSurface"])
                listofanswer[rowitem].grid(row=rowpos,column=1, columnspan=2)
                label=tk.Label(self.frame,text=DATA[rowitem]["Jsc"],fg='black',background='white')
                label.grid(row=rowpos,column=3, columnspan=1)
                rowpos=rowpos+1
            
        def onFrameConfigure(self, event):
            '''Reset the scroll region to encompass the inner frame'''
            self.canvas0.configure(scrollregion=self.canvas0.bbox("all"))  
            
    def changecellarea(self):
        global DATA
        
        if DATA!=[]:
            self.window = tk.Toplevel()
            self.window.wm_title("Change the cell area")
            center(self.window)
            self.window.geometry("360x100")
            Button(self.window, text="Update",command = self.UpdateChangeArea).pack()
            
            self.PopulateListofSampleChangeArea(self.window).pack(side="top", fill="both", expand=True)

    def UpdateChangeArea(self):
        global listofanswer
        global DATA
        
        leglist=[]
        for e in listofanswer:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        
        for item in range(len(DATA)):
            DATA[item]["Jsc"]=float(DATA[item]["Jsc"])*float(DATA[item]["CellSurface"])/float(leglist[item]) 
            DATA[item]["Jmpp"]=float(DATA[item]["Jmpp"])*float(DATA[item]["CellSurface"])/float(leglist[item]) 
            DATA[item]["Pmpp"]=float(DATA[item]["Pmpp"])*float(DATA[item]["CellSurface"])/float(leglist[item])
            DATA[item]["Eff"]=float(DATA[item]["Eff"])*float(DATA[item]["CellSurface"])/float(leglist[item])
            newCurrent=[]
            for i in range(len(DATA[item]["IVData"][1])):
                newCurrent.append(DATA[item]["IVData"][1][i]*float(DATA[item]["CellSurface"])/float(leglist[item]))
            DATA[item]["IVData"][1]=copy.deepcopy(newCurrent)
            
        #change also the rawdata file, use the filepath to access it. 
#        old file is renamed with _old
#        new file has original name and saved at same place so that all links are still valid
        
        for item0 in range(len(DATA)):
            newarea=float(leglist[item0])
            oldcellarea=DATA[item0]["CellSurface"]
            file_path=DATA[item0]["filepath"]
            
            filetoread = open(file_path,"r")
            filerawdata = filetoread.readlines()
            
            for item in range(len(filerawdata)):
                if "Cell size [m2]:" in filerawdata[item]:
                    oldcellarea=copy.deepcopy(float(filerawdata[item][17:-1]))
                    filerawdata[item]=filerawdata[item][:17]+str(newarea)+"\n"
                    break
            for item in range(len(filerawdata)):
                if "Jsc [A/m2]:" in filerawdata[item]:
                    filerawdata[item]=filerawdata[item][:19]+str(float(filerawdata[item][19:-1])*oldcellarea/newarea)+"\n"
                    break   
            for item in range(len(filerawdata)):
                if "Efficiency [.]:" in filerawdata[item]:
                    filerawdata[item]=filerawdata[item][:19]+str(float(filerawdata[item][19:-1])*oldcellarea/newarea)+"\n"
                    break
            for item in range(len(filerawdata)):
                if "Pmpp [W/m2]:" in filerawdata[item]:
                    filerawdata[item]=filerawdata[item][:19]+str(float(filerawdata[item][19:-1])*oldcellarea/newarea)+"\n"
                    break
            for item in range(len(filerawdata)):
                if "Jmpp [A]:" in filerawdata[item]:
                    filerawdata[item]=filerawdata[item][:10]+str(float(filerawdata[item][10:-1])*oldcellarea/newarea)+"\n"
                    break
            for item in range(len(filerawdata)):
                if "MEASURED IV DATA" in filerawdata[item]:
                        pos=item+2
                        break
                elif "MEASURED IV FRLOOP DATA" in filerawdata[item]:
                        pos=item+2
                        break
            for item in range(pos,len(filerawdata),1):
                filerawdata[item]=filerawdata[item].split("\t")[0]+"\t"+filerawdata[item].split("\t")[1]+"\t"+filerawdata[item].split("\t")[2]+"\t"+str(float(filerawdata[item].split("\t")[3][:-1])*oldcellarea/newarea)+"\n"

            file = open(file_path,'w')
            file.writelines("%s" % item for item in filerawdata)
            file.close()
            DATA[item0]["CellSurface"]=newarea
        
        self.window.destroy()
        self.updateTable()
        self.UpdateIVGraph()
        
#########################################################
#########################################################        
           
    class TableBuilder(Frame):
        def __init__(self, parent):
            Frame.__init__(self, parent)
            self.parent=parent
            self.initialize_user_interface()
    
        def initialize_user_interface(self):
            global DATA
            global testdata
            testdata=[]
            #self.parent.grid_rowconfigure(0,weight=1)
            #self.parent.grid_columnconfigure(0,weight=1)
            self.parent.config(background="white")
                      
            for item in range(len(DATA)):
                testdata.append([DATA[item]["Group"],DATA[item]["SampleName"],float('%.2f' % float(DATA[item]["CellSurface"])),DATA[item]["ScanDirection"],float('%.2f' % float(DATA[item]["Jsc"])),float('%.2f' % float(DATA[item]["Voc"])),float('%.2f' % float(DATA[item]["FF"])),float('%.2f' % float(DATA[item]["Eff"])),float('%.2f' % float(DATA[item]["Roc"])),float('%.2f' % float(DATA[item]["Rsc"])),float('%.2f' % float(DATA[item]["Vmpp"])),float('%.2f' % float(DATA[item]["Jmpp"]))])
                
            self.tableheaders=('Group','Sample','Area','Scan direct.','Jsc','Voc','FF','Eff.','Roc','Rsc','Vmpp','Jmpp')
                        
            # Set the treeview
            self.tree = Treeview( self.parent, columns=self.tableheaders, show="headings")
            
            for col in self.tableheaders:
                self.tree.heading(col, text=col.title(), command=lambda c=col: self.sortby(self.tree, c, 0))
                #self.tree.column(col,stretch=tkinter.YES)
                self.tree.column(col, width=int(round(1.3*tkFont.Font().measure(col.title()))), anchor='n')   
                #print(int(round(1.2*tkFont.Font().measure(col.title()))))
            
            self.deletetabelem = Button(self.parent, text = "Delete table elements", command = self.deletedatatreeview)
            self.deletetabelem.grid(row = 0, column = 1, columnspan=1)
            self.plotfromtable = Button(self.parent, text="Plot",command = self.plottingfromTable,fg='black')
            self.plotfromtable.grid(row=0, column=9, columnspan=1,rowspan=1)
            self.groupbutton = Button(self.parent, text="Group",command = self.groupfromTable,fg='black')
            self.groupbutton.grid(row=0, column=10, columnspan=1,rowspan=1)
            
            vsb = Scrollbar(orient="vertical", command=self.tree.yview)
            #hsb = ttk.Scrollbar(orient="horizontal",command=self.tree.xview)
            self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=())
            self.tree.grid(row=1,column=0, columnspan=15,rowspan=10, sticky='nsew', in_=self.parent)
            #vsb.grid(column=11, row=1,rowspan=10, sticky='ns', in_=self.parent)
            #hsb.grid(column=0, row=11, sticky='ew', in_=self.parent)
            self.treeview = self.tree
            
            self.insert_data(testdata)
        
        def deletedatatreeview(self):
            global DATA
            try:
                for j in range(len(self.treeview.selection())):
                    selected_item = self.treeview.selection()[j] ## get selected item
                    for i in range(len(DATA)):
                        if DATA[i]["SampleName"]==self.treeview.item(selected_item)["values"][1]:
                            DATA.pop(i)
                            break
                selected_items = self.treeview.selection()
                for item in selected_items:
                    self.treeview.delete(item)
            except IndexError:
                print("you didn't select an element in the table")

        def insert_data(self, testdata):
            for item in testdata:
                self.treeview.insert('', 'end', values=item)
                
                #for ix, val in enumerate(item):
                #    col_w = tkFont.Font().measure(val)
                #    if tkFont.Font().measure(self.tableheaders[ix].title())<col_w:
                #        self.tree.column(self.tableheaders[ix], width=col_w)
                
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
        
        def plottingfromTable(self):
            global takenforplot
            
            totake=self.treeview.selection()
            takenforplot=[str(self.treeview.item(item)["values"][1]) for item in totake]
            
        def groupfromTable(self):
            global samplesgroups
            
            self.window = tk.Toplevel()
            self.window.wm_title("Group samples")
            center(self.window)
            self.window.geometry("580x120")
             
            label=tk.Label(self.window,text="                ")
            label.grid(row=0,column=0, columnspan=8)
            label=tk.Label(self.window,text="  ")
            label.grid(row=0,column=0, rowspan=8)
            
            self.groupupdate = Button(self.window, text="new group",
                                command = self.validategroup)
            self.groupupdate.grid(row=1, column=1, columnspan=3)
            
            self.newgroup = tk.StringVar()
            self.newgroup.set(samplesgroups[0])
            entry=Entry(self.window, textvariable=self.newgroup,width=13)
            entry.grid(row=2,column=1,columnspan=3)
            
            label=tk.Label(self.window,text="      or      ")
            label.grid(row=1,column=5, columnspan=1)
            
            self.groupupdate = Button(self.window, text="existing group",
                                command = self.validategroup)
            self.groupupdate.grid(row=1, column=6, columnspan=3)
            
            self.groupchoice=tk.StringVar()
            self.groupchoice.set(samplesgroups[0]) # default choice
            self.dropgroupchoice=OptionMenu(self.window, self.groupchoice, *samplesgroups, command=())
            self.dropgroupchoice.grid(row=2, column=6, columnspan=3)
            
            label=tk.Label(self.window,text="      or      ")
            label.grid(row=1,column=9, columnspan=1)
            
            self.groupdel = Button(self.window, text="delete group",
                                command = self.deletegroup)
            self.groupdel.grid(row=1, column=10, columnspan=3)
            
            self.groupdellist=tk.StringVar()
            self.groupdellist.set(samplesgroups[0]) # default choice
            self.dropgroupchoice=OptionMenu(self.window, self.groupdellist, *samplesgroups, command=())
            self.dropgroupchoice.grid(row=2, column=10, columnspan=3)
            
            label=tk.Label(self.window,text="      or      ")
            label.grid(row=1,column=15, columnspan=1)
            
            self.groupOrder = Button(self.window, text="reorder group",
                                command = self.reordergroup)
            self.groupOrder.grid(row=1, column=20, columnspan=3)
        
        class Drag_and_Drop_Listbox(tk.Listbox):
            #A tk listbox with drag'n'drop reordering of entries.
            def __init__(self, master, **kw):
                #kw['selectmode'] = tk.MULTIPLE
                kw['selectmode'] = tk.SINGLE
                kw['activestyle'] = 'none'
                tk.Listbox.__init__(self, master, kw)
                self.bind('<Button-1>', self.getState, add='+')
                self.bind('<Button-1>', self.setCurrent, add='+')
                self.bind('<B1-Motion>', self.shiftSelection)
                self.curIndex = None
                self.curState = None
            def setCurrent(self, event):
                ''' gets the current index of the clicked item in the listbox '''
                self.curIndex = self.nearest(event.y)
            def getState(self, event):
                ''' checks if the clicked item in listbox is selected '''
                #i = self.nearest(event.y)
                #self.curState = self.selection_includes(i)
                self.curState = 1
            def shiftSelection(self, event):
                ''' shifts item up or down in listbox '''
                i = self.nearest(event.y)
                if self.curState == 1:
                  self.selection_set(self.curIndex)
                else:
                  self.selection_clear(self.curIndex)
                if i < self.curIndex:
                  # Moves up
                  x = self.get(i)
                  selected = self.selection_includes(i)
                  self.delete(i)
                  self.insert(i+1, x)
                  if selected:
                    self.selection_set(i+1)
                  self.curIndex = i
                elif i > self.curIndex:
                  # Moves down
                  x = self.get(i)
                  selected = self.selection_includes(i)
                  self.delete(i)
                  self.insert(i-1, x)
                  if selected:
                    self.selection_set(i-1)
                  self.curIndex = i
        
        def reordergroup(self):
            global samplesgroups
            
            self.reorderwindow = tk.Tk()
            center(self.reorderwindow)
            self.listbox = self.Drag_and_Drop_Listbox(self.reorderwindow)
            for name in range(1,len(samplesgroups)):
              self.listbox.insert(tk.END, samplesgroups[name])
              self.listbox.selection_set(0)
            self.listbox.pack(fill=tk.BOTH, expand=True)
            scrollbar = tk.Scrollbar(self.listbox, orient="vertical")
            scrollbar.config(command=self.listbox.yview)
            scrollbar.pack(side="right", fill="y")
            
            self.listbox.config(yscrollcommand=scrollbar.set)
            
            printbut = tk.Button(self.reorderwindow, text="reorder",
                                        command = self.printlist)
            printbut.pack()
            self.reorderwindow.mainloop()    
            
            #print(samplesgroups)
            
        def printlist(self):
            global samplesgroups
            samplesgroups=list(self.listbox.get(0,tk.END))
            samplesgroups=["Default group"]+ samplesgroups
            #self.UpdateIVLegMod()
            self.reorderwindow.destroy()
            self.window.destroy()
            #self.groupfromTable()
        
        def validategroup(self):
            global takenforplot
            global samplesgroups
            global DATA
            
            totake=self.treeview.selection()
            takenforplot=[str(self.treeview.item(item)["values"][1]) for item in totake]

            if self.newgroup.get() != samplesgroups[0] and totake!=():
                if self.newgroup.get() not in samplesgroups:
                    samplesgroups.append(self.newgroup.get())
                for item in range(len(takenforplot)):
                    for item1 in range(len(DATA)):
                        if takenforplot[item]==DATA[item1]["SampleName"]:
                            DATA[item1]["Group"]=self.newgroup.get()
                            break
            elif totake!=():
                for item in range(len(takenforplot)):
                    for item1 in range(len(DATA)):
                        if takenforplot[item]==DATA[item1]["SampleName"]:
                            DATA[item1]["Group"]=self.groupchoice.get()
                            break
            self.initialize_user_interface()
            self.window.destroy()
            
        def deletegroup(self):
            global samplesgroups
            global DATA
            
            if self.groupdellist.get()!="Default group":
                while self.groupdellist.get() in samplesgroups: samplesgroups.remove(self.groupdellist.get()) 
            
            for i in range(len(DATA)):
                if DATA[i]["Group"]==self.groupdellist.get():
                    DATA[i]["Group"]="Default group"
            self.initialize_user_interface()
            self.window.destroy()
        
    def SampleMppNames(self, DATAx):
        Names = list(self.mppnames)
        for item in range(len(DATAx)):
            Names.append(DATAx[item]["SampleName"])
        return tuple(Names)
    
#%%######################################################################
        
if __name__ == '__main__':
    app = IVApp()
    app.mainloop()
    