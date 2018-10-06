#! python3

import os, datetime

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
import sqlite3

#import THEANALYSER_pyth36 as analyserMain

"""
TODOLIST

- calculation of jsc difference, from txt files

- DB batch and samplename: might fail if user did not follow exactly the pattern. put some safety 
when there are several tabs, numbers are added to the tab names => don't use that as batch and samplename



"""
#%%

LARGE_FONT= ("Verdana", 12)

echarge = 1.60218e-19
planck = 6.62607e-34
lightspeed = 299792458

file = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'spectratxtfiles','AM15G.txt'))
am15g = file.readlines()
file.close()
dataWave = []
dataInt = []
for i in range(len(am15g)):
    pos = am15g[i].find('\t')
    dataWave.append(float(am15g[i][:pos]))
    dataInt.append(float(am15g[i][pos+1:-1]))
  
SpectIntensFct = interp1d(dataWave,dataInt)

def modification_date(path_to_file):
    return datetime.datetime.fromtimestamp(os.path.getmtime(path_to_file)).strftime("%Y-%m-%d %H:%M:%S")

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

titEQE=0
EQElegendMod=[]
DATAFORGRAPH=[]
DATAforexport=[]
takenforplot=[]
listofanswer=[]
listoflinestyle=[]
listofcolorstyle=[]
colorstylelist = ['black', 'red', 'blue', 'brown', 'green','cyan','magenta','olive','navy','orange','gray','aliceblue','antiquewhite','aqua','aquamarine','azure','beige','bisque','blanchedalmond','blue','blueviolet','brown','burlywood','cadetblue','chartreuse','chocolate','coral','cornflowerblue','cornsilk','crimson','darkblue','darkcyan','darkgoldenrod','darkgray','darkgreen','darkkhaki','darkmagenta','darkolivegreen','darkorange','darkorchid','darkred','darksalmon','darkseagreen','darkslateblue','darkslategray','darkturquoise','darkviolet','deeppink','deepskyblue','dimgray','dodgerblue','firebrick','floralwhite','forestgreen','fuchsia','gainsboro','ghostwhite','gold','goldenrod','greenyellow','honeydew','hotpink','indianred','indigo','ivory','khaki','lavender','lavenderblush','lawngreen','lemonchiffon','lightblue','lightcoral','lightcyan','lightgoldenrodyellow','lightgreen','lightgray','lightpink','lightsalmon','lightseagreen','lightskyblue','lightslategray','lightsteelblue','lightyellow','lime','limegreen','linen','magenta','maroon','mediumaquamarine','mediumblue','mediumorchid','mediumpurple','mediumseagreen','mediumslateblue','mediumspringgreen','mediumturquoise','mediumvioletred','midnightblue','mintcream','mistyrose','moccasin','navajowhite','navy','oldlace','olive','olivedrab','orange','orangered','orchid','palegoldenrod','palegreen','paleturquoise','palevioletred','papayawhip','peachpuff','peru','pink','plum','powderblue','purple','red','rosybrown','royalblue','saddlebrown','salmon','sandybrown','seagreen','seashell','sienna','silver','skyblue','slateblue','slategray','snow','springgreen','steelblue','tan','teal','thistle','tomato','turquoise','violet','wheat','white','whitesmoke','yellow','yellowgreen']


#%%###############################################################################             
    
class EQEApp(Toplevel):

    def __init__(self, *args, **kwargs):
        
        Toplevel.__init__(self, *args, **kwargs)
        Toplevel.wm_title(self, "EQEApp")
        Toplevel.config(self,background="white")
        self.wm_geometry("550x550")
        center(self)
        self.initUI()


    def initUI(self):
        self.master.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.canvas0 = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.superframe=Frame(self.canvas0,background="#ffffff")
        self.canvas0.pack(side="left", fill="both", expand=True)
        
        label = tk.Label(self.canvas0, text="EQE DATA Analyzer", font=LARGE_FONT, bg="black",fg="white")
        label.pack(fill=tk.X,expand=0)
        
        frame1=Frame(self.canvas0,borderwidth=0,  bg="white")
        frame1.pack(fill=tk.BOTH,expand=1)
        frame1.bind("<Configure>", self.onFrameConfigure)
        self.fig1 = plt.figure(figsize=(3, 2))
        canvas = FigureCanvasTkAgg(self.fig1, frame1)
        canvas.get_tk_widget().pack(fill=tk.BOTH,expand=1)
        self.EQEgraph = plt.subplot2grid((1, 5), (0, 0), colspan=3)
        self.toolbar = NavigationToolbar2TkAgg(canvas, frame1)
        self.toolbar.update()
        canvas._tkcanvas.pack(fill = BOTH, expand = 1) 
        
        
        frame2=Frame(self.canvas0,borderwidth=0,  bg="white")
        frame2.pack(fill=tk.X,expand=0)
        
        frame21=Frame(frame2,borderwidth=0,  bg="white")
        frame21.pack(side=tk.LEFT,fill=tk.X,expand=1)
        
        frame211=Frame(frame21,borderwidth=0,  bg="white")
        frame211.pack(fill=tk.X,expand=1)
        self.importdat = Button(frame211, text="Import DATA",
                            command = self.onOpenEQE)
        self.importdat.pack(side=tk.LEFT,expand=1)
        self.update = Button(frame211, text="Update Graph",
                            command = self.UpdateEQEGraph, width=15)
        self.update.pack(side=tk.LEFT,expand=1)
        self.CalculateCurrent = Button(frame211, text="Calc. current",
                            command = self.CalcCurrent)
        self.CalculateCurrent.pack(side=tk.LEFT,expand=1)
        
        frame212=Frame(frame21,borderwidth=0,  bg="white")
        frame212.pack(fill=tk.X,expand=1)
        self.exportgraph = Button(frame212, text="Export this graph",
                            command = self.ExportEQEGraph)
        self.exportgraph.pack(side=tk.LEFT,expand=1)
        self.exportdat = Button(frame212, text="Export All DATA",
                            command = self.sortandexportEQEdat)
        self.exportdat.pack(side=tk.LEFT,expand=1)
        self.changeEQElegend = Button(frame212, text="change legend",
                            command = self.ChangeLegendEQEgraph)
        self.changeEQElegend.pack(side=tk.LEFT,expand=1)
        
        frame213=Frame(frame21,borderwidth=0,  bg="white")
        frame213.pack(fill=tk.X,expand=1)
        
        frame2131=Frame(frame213,borderwidth=0,  bg="white")
        frame2131.pack(side=tk.LEFT,fill=tk.X,expand=1)
        frame21311=Frame(frame2131,borderwidth=0,  bg="white")
        frame21311.pack(fill=tk.X,expand=1)
        frame21312=Frame(frame2131,borderwidth=0,  bg="white")
        frame21312.pack(fill=tk.X,expand=1)
        frame21313=Frame(frame2131,borderwidth=0,  bg="white")
        frame21313.pack(fill=tk.X,expand=1)
        frame21314=Frame(frame2131,borderwidth=0,  bg="white")
        frame21314.pack(fill=tk.X,expand=1)
        frame21315=Frame(frame2131,borderwidth=0,  bg="white")
        frame21315.pack(fill=tk.X,expand=1)
        
        self.minx = tk.DoubleVar()
        Entry(frame21311, textvariable=self.minx,width=5).pack(side=tk.LEFT,fill=tk.X,expand=1)
        tk.Label(frame21312, text="Min X", bg="white").pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.minx.set(320)
        self.maxx = tk.DoubleVar()
        Entry(frame21311, textvariable=self.maxx,width=5).pack(side=tk.LEFT,fill=tk.X,expand=1)
        tk.Label(frame21312, text="Max X", bg="white").pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.maxx.set(1180)
        self.miny = tk.DoubleVar()
        Entry(frame21311, textvariable=self.miny,width=5).pack(side=tk.LEFT,fill=tk.X,expand=1)
        tk.Label(frame21312, text="Min Y", bg="white").pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.miny.set(0)
        self.maxy = tk.DoubleVar()
        Entry(frame21311, textvariable=self.maxy,width=5).pack(side=tk.LEFT,fill=tk.X,expand=1)
        tk.Label(frame21312, text="Max Y", bg="white").pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.maxy.set(1)
        
        self.CheckLegend = IntVar()
        legend=Checkbutton(frame21313,text='Legend',variable=self.CheckLegend, 
                           onvalue=1,offvalue=0,height=1, width=10, command = self.UpdateEQEGraph, bg="white")
        legend.pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.CheckLegJsc = IntVar()
        legendJsc=Checkbutton(frame21313,text='Jsc',variable=self.CheckLegJsc, 
                           onvalue=1,offvalue=0,height=1, width=10, command = self.UpdateEQEGraph, bg="white")
        legendJsc.pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.CheckLegEg = IntVar()
        legendEg=Checkbutton(frame21313,text='Eg',variable=self.CheckLegEg, 
                           onvalue=1,offvalue=0,height=1, width=10, command = self.UpdateEQEGraph, bg="white")
        legendEg.pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.CheckAutoscale = IntVar()
        Autoscale=Checkbutton(frame21314,text='autoscale',variable=self.CheckAutoscale, 
                           onvalue=1,offvalue=0,height=1, width=10, command = self.UpdateEQEGraph, bg="white")
        Autoscale.pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.CheckTangent = IntVar()
        legend=Checkbutton(frame21314,text='showSecretEg',variable=self.CheckTangent, 
                           onvalue=1,offvalue=0,height=1, width=10, command = self.UpdateEQEGraph, bg="white")
        legend.pack(side=tk.LEFT,fill=tk.X,expand=1)
        
        Ytype = ["linear","log","Tauc","NormalizedByAll","NormalizedBySingle"]
        self.YtypeChoice=StringVar()
        self.YtypeChoice.set("linear") # default choice
        self.dropMenuFrame = OptionMenu(frame21314, self.YtypeChoice, *Ytype, command=self.choiceYtype)
        self.dropMenuFrame.pack(side=tk.LEFT,fill=tk.X,expand=1)
        
        self.EQEDBbut = Button(frame21315, text="SaveToDB",
                            command = self.WriteEQEtoDatabase)
        self.EQEDBbut.pack(side=tk.RIGHT)
        
        
        frame2132=Frame(frame213,borderwidth=0,  bg="white")
        frame2132.pack(side=tk.RIGHT, fill=tk.X,expand=1)
        frame21321=Frame(frame2132,borderwidth=0,  bg="white")
        frame21321.pack(fill=tk.X,expand=1)
        frame21322=Frame(frame2132,borderwidth=0,  bg="white")
        frame21322.pack(fill=tk.X,expand=1)
        frame21323=Frame(frame2132,borderwidth=0,  bg="white")
        frame21323.pack(fill=tk.X,expand=1)
        
        self.pos1 = IntVar()
        pos=Checkbutton(frame21321,text=None,variable=self.pos1, 
                           onvalue=1,offvalue=0,height=1, width=1, command = self.UpdateEQEGraph, bg="white")
        pos.pack(side=tk.LEFT,fill=tk.X,expand=1)
        #self.pos2 = IntVar()
        pos=Checkbutton(frame21321,text=None,variable=self.pos1, 
                           onvalue=2,offvalue=0,height=1, width=1, command = self.UpdateEQEGraph, bg="white")
        pos.pack(side=tk.LEFT,fill=tk.X,expand=1)
        #self.pos3 = IntVar()
        pos=Checkbutton(frame21322,text=None,variable=self.pos1, 
                           onvalue=3,offvalue=0,height=1, width=1, command = self.UpdateEQEGraph, bg="white")
        pos.pack(side=tk.LEFT,fill=tk.X,expand=1)
        #self.pos4 = IntVar()
        pos=Checkbutton(frame21322,text=None,variable=self.pos1, 
                           onvalue=4,offvalue=0,height=1, width=1, command = self.UpdateEQEGraph, bg="white")
        pos.pack(side=tk.LEFT,fill=tk.X,expand=1)       
        #self.pos5 = IntVar()
        pos=Checkbutton(frame21323,text=None,variable=self.pos1, 
                           onvalue=5,offvalue=0,height=1, width=1, command = self.UpdateEQEGraph, bg="white")
        pos.pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.EQEtitle = Button(frame21323, text="Title",
                            command = self.GiveEQEatitle)
        self.EQEtitle.pack(side=tk.LEFT,fill=tk.X,expand=1)
        
        
        self.frame22=Frame(frame2,borderwidth=0,  bg="white")
        self.frame22.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
        self.frame221=Frame(self.frame22,borderwidth=0,  bg="white")
        self.frame221.pack(fill=tk.BOTH,expand=1)
#        Button(self.frame22, text="DeleteParam",
#               command = self.deleteparameterfromlist).pack(fill=tk.X,expand=0)
#        self.listboxsamples=Listbox(self.frame22,width=20, height=5, selectmode=tk.EXTENDED)
#        self.listboxsamples.pack(side="left", fill=tk.BOTH, expand=1)
#        scrollbar = tk.Scrollbar(self.frame22, orient="vertical")
#        scrollbar.config(command=self.listboxsamples.yview)
#        scrollbar.pack(side="right", fill="y")
#        self.listboxsamples.config(yscrollcommand=scrollbar.set)

        self.SelectData()
        
        frame23=Frame(frame2,borderwidth=0,  bg="white")
        frame23.pack(side=tk.RIGHT,fill=tk.X,expand=0)
        label = tk.Label(frame23, text="  ", font=LARGE_FONT, bg="white")
        label.pack(fill=tk.X,expand=0)
        
        frame3=Frame(self.canvas0,borderwidth=0,  bg="white")
        frame3.pack(fill=tk.X,expand=0)
        label = tk.Label(frame3, text="  ", font=LARGE_FONT, bg="white")
        label.pack(fill=tk.X,expand=0)
        
        
#%%        
#    def deleteparameterfromlist(self):
#        global DATAFORGRAPH
#        selection = self.listboxsamples.curselection()        
#        self.names = ()
#        nameslist=list(self.SampleNames(DATAFORGRAPH))
#        pos = 0
#        for i in selection :
#            idx = int(i) - pos
#            value=self.listboxsamples.get(i)
#            ind = nameslist.index(value)        
#            del(nameslist[ind])
#            del(DATAFORGRAPH[ind])
#            self.listboxsamples.delete( idx,idx )
#            pos = pos + 1
#        self.names=self.SampleNames(DATAFORGRAPH)
#        self.UpdateEQEGraph()

    def on_closing(self):
        global titEQE
        global EQElegendMod
        global DATAFORGRAPH
        global DATAforexport
        global takenforplot
        global listofanswer
        global listoflinestyle
        global listofcolorstyle
        global colorstylelist
        
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            titEQE=0
            EQElegendMod=[]
            DATAFORGRAPH=[]
            DATAforexport=[]
            takenforplot=[]
            listofanswer=[]
            listoflinestyle=[]
            listofcolorstyle=[]
            colorstylelist = ['black', 'red', 'blue', 'brown', 'green','cyan','magenta','olive','navy','orange','gray','aliceblue','antiquewhite','aqua','aquamarine','azure','beige','bisque','blanchedalmond','blue','blueviolet','brown','burlywood','cadetblue','chartreuse','chocolate','coral','cornflowerblue','cornsilk','crimson','darkblue','darkcyan','darkgoldenrod','darkgray','darkgreen','darkkhaki','darkmagenta','darkolivegreen','darkorange','darkorchid','darkred','darksalmon','darkseagreen','darkslateblue','darkslategray','darkturquoise','darkviolet','deeppink','deepskyblue','dimgray','dodgerblue','firebrick','floralwhite','forestgreen','fuchsia','gainsboro','ghostwhite','gold','goldenrod','greenyellow','honeydew','hotpink','indianred','indigo','ivory','khaki','lavender','lavenderblush','lawngreen','lemonchiffon','lightblue','lightcoral','lightcyan','lightgoldenrodyellow','lightgreen','lightgray','lightpink','lightsalmon','lightseagreen','lightskyblue','lightslategray','lightsteelblue','lightyellow','lime','limegreen','linen','magenta','maroon','mediumaquamarine','mediumblue','mediumorchid','mediumpurple','mediumseagreen','mediumslateblue','mediumspringgreen','mediumturquoise','mediumvioletred','midnightblue','mintcream','mistyrose','moccasin','navajowhite','navy','oldlace','olive','olivedrab','orange','orangered','orchid','palegoldenrod','palegreen','paleturquoise','palevioletred','papayawhip','peachpuff','peru','pink','plum','powderblue','purple','red','rosybrown','royalblue','saddlebrown','salmon','sandybrown','seagreen','seashell','sienna','silver','skyblue','slateblue','slategray','snow','springgreen','steelblue','tan','teal','thistle','tomato','turquoise','violet','wheat','white','whitesmoke','yellow','yellowgreen']
            plt.close()
            self.destroy()
            self.master.deiconify()
            
    def choiceYtype(self,a):
        self.UpdateEQEGraph()
    def onFrameConfigure(self, event):
        #self.canvas0.configure(scrollregion=self.canvas0.bbox("all"))
        self.canvas0.configure(scrollregion=(0,0,500,500))
    
    def onOpenEQE(self):
        global DATAFORGRAPH
        self.GetEQEDATA()
        self.SelectData()
        
    def ncolumneqe(self, n):
        twocolumneqe = [['Wavelength','EQE'],['nm','-']]
        for i in range(1,n-1):
            twocolumneqe[0].append('EQE')
            twocolumneqe[1].append('-')
        return twocolumneqe
    
    def AM15GParticlesinnm(self, x):
        return (x*10**(-9))*SpectIntensFct(x)/(planck*lightspeed)
    
#%%###########        
    def GetEQEDATA(self):
        global DATAFORGRAPH
        global colorstylelist
        
        file_path = filedialog.askopenfilenames()
#        print(file_path[0])
#        print(modification_date(file_path[0]))
#        
#        print(os.path.basename(file_path[0].split('.')[0]))
#        print("")
        
        
        directory = str(Path(file_path[0]).parent.parent)+'\\resultFilesEQE'
        
#        print(directory)
        if not os.path.exists(directory):
            os.makedirs(directory)
            os.chdir(directory)
        else :
            os.chdir(directory)
        
       
        DATA=[] # [{'Name':, 'Jsc':, 'Eg':, 'NbColumn':, 'DATA': [[wavelength],[eqe],[eqe]...]}]
        AllNames = []
        
        print(len(file_path))
        
        for k in range(len(file_path)):
#            samplename=os.path.basename(file_path[k].split('.')[0]).replace('-','_')  
            samplename=file_path[k].replace('\\','/') 
            samplename=samplename.split('/')[-1].replace('-','_').split('.')[0]
            
            print(samplename)
            batchnumb=samplename.split('_')[0]
            samplenumb=samplename.split('_')[1]
            
            wb = xlrd.open_workbook(file_path[k])
            sheet_names = wb.sheet_names()
            print('Sample: %2f' % float(k+1))    
            for j in range(len(sheet_names)):
                if 'Sheet' not in sheet_names[j]:
                    AllNames.append(sheet_names[j])
                    print(sheet_names[j])
                    xlsheet = wb.sheet_by_index(j)
                    cell1 = xlsheet.cell(0,0).value
                    rownb = cell1[cell1.index('(')+1:cell1.index('x')-1]
                    columnnb = cell1[cell1.index('x')+2:cell1.index(')')]
                    comment = xlsheet.cell(1,0).value
                    datetime=modification_date(file_path[k])
                    datadict = {'dateTime': datetime, 'filepath':file_path[k],'Name': sheet_names[j],'Jsc':[],'Eg':[],
                                'EgTauc':[],'lnDat':[],'EgLn':[],'EuLn':[],'stderrEgLn':[],'NbColumn':columnnb, 
                                'DATA': [],'tangent': [],'tangentLn': [], 'comment': comment, 'Vbias':[],'filterbias':[],'ledbias':[],
                                'batchnumb': batchnumb, 'samplenumb': samplenumb}   
                    for i in range(int(columnnb)):
                        partdat = []
                        for h in range(3,int(rownb)+3,1):
                            partdat.append(xlsheet.cell(h,i).value)
                        datadict['DATA'].append(partdat)

#                    try:
                    for i in range(1,int(columnnb),1):
                        cell1 = xlsheet.cell(2,i).value
                        datadict['Vbias'].append(cell1[cell1.index('=')+2:cell1.index(',')])
                        datadict['filterbias'].append(cell1[cell1.index(',')+2:cell1.index('L')-2])
                        datadict['ledbias'].append(cell1[cell1.index('#')+2:cell1.index('J')-2])
#                            print(datadict['Vbias'])
                        #jsc calculation
                        x = datadict['DATA'][0]
                        y = datadict['DATA'][i]
                        if len(x)>3:
                            spl = UnivariateSpline(x, y, s=0)
                            f = interp1d(x, y, kind='cubic')
                            x2 = lambda x: self.AM15GParticlesinnm(x)*f(x)
                            integral = echarge/10*integrate.quad(x2,datadict['DATA'][0][0],datadict['DATA'][0][-1])[0]
                            datadict['Jsc'].append(integral)
                            #Eg calculation from linear normal curve
                            splder = spl.derivative(n=1)
                            splderlist = []
                            newx=[]
                            for item in x :
                                if item >400:
                                    splderlist.append(splder(item))
                                    newx.append(item)
                            minder=splderlist.index(min(splderlist))
                            xhighslope = newx[minder]
                            yhighslope = spl(newx[minder]).tolist()
                            yprimehighslope = splder(newx[minder]).tolist()
                            Eg= 1239.8/(xhighslope - yhighslope/yprimehighslope)
                            datadict['Eg'].append(Eg)
                            datadict['tangent'].append([yprimehighslope, yhighslope-yprimehighslope*xhighslope])#[pente,ordonnee a l'origine]

                            #Eg calculation from ln(EQE) curve
                            xE=[]
                            yln=[]
                            for xi in range(len(x)):
                                if y[xi]>0:
                                    xE.append(1239.8/x[xi])
                                    yln.append(math.log(100*y[xi]))

                            datadict['lnDat'].append([xE,yln])
                            
                            xErestricted=[]
                            ylnrestricted=[]
                            
                            for xi in range(len(xE)-1,-1,-1):
                                if yln[xi]<3 and yln[xi]>-2:
                                    xErestricted.append(xE[xi])
                                    ylnrestricted.append(yln[xi])
                            xErestricted.append(999)
                            ylnrestricted.append(999)
                            xErestricted2=[]
                            ylnrestricted2=[]
                            for xi in range(len(xErestricted)-1):
                                xErestricted2.append(xErestricted[xi])
                                ylnrestricted2.append(ylnrestricted[xi])
                                if abs(xErestricted[xi]-xErestricted[xi+1])>0.3:
                                    break
                            if len(xErestricted2)>1:
                                slope, intercept, r_value, p_value, std_err = stats.linregress(xErestricted2,ylnrestricted2)
                                                                
                                datadict['EgLn'].append(-intercept/slope)
                                datadict['EuLn'].append(1000/slope)#Eu calculation from ln(EQE) curve slope at band edge
                                datadict['tangentLn'].append([slope, intercept,xErestricted2,ylnrestricted2])#[pente,ordonnee a l'origine]
                                datadict['stderrEgLn'].append([std_err,len(xErestricted2)])
                            else:
                                print("EgLn not found enough points...")
                                datadict['EgLn'].append(999)
                                datadict['EuLn'].append(999)#Eu calculation from ln(EQE) curve slope at band edge
                                datadict['tangentLn'].append([999, 999,[999],[999]])#[pente,ordonnee a l'origine]
                                datadict['stderrEgLn'].append([999,999])
                            
                            #Tauc plots
                            try:
                                xtauc=[1239.8/xm for xm in x]
                                ytauc=[((math.log(1-y[m]))**2)*(xtauc[m]**2) for m in range(len(y)) ]
                                xtauc=xtauc[::-1]
                                ytauc=ytauc[::-1]
                                spl = UnivariateSpline(xtauc, ytauc, s=0)
                                splder = spl.derivative(n=1)
                                splderlist = []
                                newx=[]
                                for item in xtauc :
                                    if item <2:
                                        splderlist.append(splder(item))
                                        newx.append(item)
                                
                                maxder=splderlist.index(max(splderlist))
                                xhighslope = newx[maxder]
                                yhighslope = spl(newx[maxder]).tolist()
                                yprimehighslope = splder(newx[maxder]).tolist()
                                Eg= (xhighslope - yhighslope/yprimehighslope)
                                
                                m=yprimehighslope
                                h=yhighslope-yprimehighslope*xhighslope
                                x2=Eg
                                x=np.linspace(x2,x2+0.1,10)
                                y=eval('m*x+h')
                                datadict['EgTauc'].append([Eg,xtauc,ytauc,m,h])
                            except:
                                datadict['EgTauc'].append([999,[],[],999,999])
                                                        
                        else:
                            datadict['EgTauc'].append([999,[],[],999,999])
                            datadict['Jsc'].append(999)
                            datadict['Eg'].append(999)
                            datadict['tangent'].append([999, 999])#[pente,ordonnee a l'origine]
                            datadict['EgLn'].append(999)
                            datadict['EuLn'].append(999)#Eu calculation from ln(EQE) curve slope at band edge
                            datadict['tangentLn'].append([999, 999,[999],[999]])#[pente,ordonnee a l'origine]
                            datadict['stderrEgLn'].append([999,999])
                            datadict['lnDat'].append([[999],[999]])
    
#                    except:
#                        print("some error with m>k in Spline...")
                    DATA.append(datadict)

        print(len(DATA))
        self.DATA=DATA
        DATAforgraph=[] # [0 samplenameshort, 1 jsc, 2 dataWave, 3 dataInt, 4 Eg, 5 NameMod, 6 Name_Jsc, 7 Name_Eg, 8 Name_Jsc_Eg, 9 linestyle, 10 linecolor, 11 slope, 12 h, 13 slopeLn, 14 hln, 
                            #15 dataEnergyLn, 16 dataIntLn, 17 ptstgtLnX, 18 ptstgtLnY, 19 EgTauc, 20 xtauc, 21 ytauc, 22 mtauc, 23 htauc, 24 Name_Egln, 25 Name_Jsc_Egln, 26 Name_Egtauc, 27 Name_Jsc_Egtauc ]
        for i in range(len(DATA)):
            for j in range(len(DATA[i]['Jsc'])):
                DATAforgraph.append([DATA[i]['Name']+'_'+str(j),DATA[i]['Jsc'][j],DATA[i]['DATA'][0],DATA[i]['DATA'][j+1],
                                     DATA[i]['Eg'][j],DATA[i]['Name']+'_'+str(j),DATA[i]['Name']+'_'+str(j)+'_'+'Jsc: %.2f' % DATA[i]['Jsc'][j],
                                     DATA[i]['Name']+'_'+str(j)+'_'+'Eg: %.2f' % DATA[i]['Eg'][j],DATA[i]['Name']+'_'+str(j)+'_'+'Jsc: %.2f' % DATA[i]['Jsc'][j]+'_'+'Eg: %.2f' % DATA[i]['Eg'][j],
                                     '-',colorstylelist[i],DATA[i]['tangent'][j][0],DATA[i]['tangent'][j][1],DATA[i]['tangentLn'][j][0],DATA[i]['tangentLn'][j][1],DATA[i]['lnDat'][j][0],DATA[i]['lnDat'][j][1],
                                     DATA[i]['tangentLn'][j][2],DATA[i]['tangentLn'][j][3],DATA[i]['EgTauc'][j][0],DATA[i]['EgTauc'][j][1],DATA[i]['EgTauc'][j][2],DATA[i]['EgTauc'][j][3],DATA[i]['EgTauc'][j][4],
                                     DATA[i]['Name']+'_'+str(j)+'_'+'Eg: %.2f' % DATA[i]['EgLn'][j],DATA[i]['Name']+'_'+str(j)+'_'+'Jsc: %.2f' % DATA[i]['Jsc'][j]+'_'+'Eg: %.2f' % DATA[i]['EgLn'][j],
                                     DATA[i]['Name']+'_'+str(j)+'_'+'Eg: %.2f' % DATA[i]['EgTauc'][j][0],DATA[i]['Name']+'_'+str(j)+'_'+'Jsc: %.2f' % DATA[i]['Jsc'][j]+'_'+'Eg: %.2f' % DATA[i]['EgTauc'][j][0]
                                     ])
        DATAFORGRAPH = DATAforgraph
        print("It's done")
#        self.initlistbox()
        
#%%#############        
    def initlistbox(self):
        self.names = ()
        self.names=self.SampleNames(DATAFORGRAPH)
        for item in self.names:
            self.listboxsamples.insert(tk.END,item)
        
    def sortandexportEQEdat(self):
        global DATAFORGRAPH
        DATA=self.DATA
        
#        selectedtoexport=list(self.listboxsamples.curselection())
##        print(selectedtoexport)
#        selectedtoexport=[self.listboxsamples.get(i) for i in selectedtoexport]
##        print(selectedtoexport)

        
        #creating excel summary file
        Summary = []
        for i in range(len(DATA)):
            for j in range(len(DATA[i]['Jsc'])):
#                print(DATA[i]['Name']+'_'+str(j)+'_'+ '%.2f' % DATA[i]['Jsc'][j])
#                if DATA[i]['Name']+'_'+str(j)+'_'+ '%.2f' % DATA[i]['Jsc'][j] in selectedtoexport:
                Summary.append([DATA[i]['Name'],DATA[i]['Jsc'][j],DATA[i]['Eg'][j],DATA[i]['EgLn'][j],
                                DATA[i]['EuLn'][j],DATA[i]['stderrEgLn'][j][0],DATA[i]['stderrEgLn'][j][1],
                                DATA[i]['EgTauc'][j][0],DATA[i]['comment'],DATA[i]['Vbias'][j],
                                DATA[i]['filterbias'][j],DATA[i]['ledbias'][j],DATA[i]['dateTime']])
        Summary.insert(0,['Sample Name','Jsc','Eg','EgLn','EuLn','stderrEgLn','nbptsEgLn','EgTauc','comment','Vbias','filterbias','ledbias','datetimeMod'])
        workbook = xlsxwriter.Workbook('Summary.xlsx')
        worksheet = workbook.add_worksheet()
        row=0
        for name, jsc, eg, egln, euln, stderr, nbptEgLn, EgTauc, comment, Vbias, filterbias, ledbias, dateandtime in Summary:
            worksheet.write(row, 0, name)
            if jsc!=999:
                worksheet.write(row, 1, jsc)
            else:
                worksheet.write(row, 1, ' ')
            if eg!=999:
                worksheet.write(row, 2, eg)
            else:
                worksheet.write(row, 2, ' ')
            if egln!=999:
                worksheet.write(row, 3, egln)
            else:
                worksheet.write(row, 3, ' ')
            if euln!=999:
                worksheet.write(row, 4, euln)
            else:
                worksheet.write(row, 4, ' ')
            if stderr!=999:
                worksheet.write(row, 5, stderr)
            else:
                worksheet.write(row, 5, ' ')
            if nbptEgLn!=999:
                worksheet.write(row, 6, nbptEgLn)
            else:
                worksheet.write(row, 6, ' ')
            if EgTauc!=999:
                worksheet.write(row, 7, EgTauc)
            else:
                worksheet.write(row, 7, ' ')
            worksheet.write(row, 8, comment)
            worksheet.write(row, 9, Vbias)
            worksheet.write(row, 10, filterbias)
            worksheet.write(row, 11, ledbias)
            worksheet.write(row, 12, dateandtime)
            row += 1
        workbook.close()
        
        #creating text files with eqe data and currents
        for i in range(len(DATA)):
            listeqe=self.ncolumneqe(int(DATA[i]['NbColumn']))
            listeqe += np.asarray(DATA[i]['DATA']).T.tolist()
            content1=[]
            for j in range(len(listeqe)):
                strr=''
                for k in range(len(listeqe[j])):
                    strr = strr + str(listeqe[j][k])+'\t'
                strr = strr[:-1]+'\n'
                content1.append(strr)
            
            namerow =DATA[i]['Name']+'\t'
            for k in range(len(DATA[i]['Jsc'])):
                namerow +='J = '+'%.2f' % DATA[i]['Jsc'][k]+' mA/cm2\t'
            namerow=namerow[:-1]+'\n'   
            content1.insert(2,namerow)    
                
            file = open(DATA[i]['Name'] + '.txt','w')
            file.writelines("%s" % item for item in content1)
            file.close()
        
        #creating graphs
        plt.clf()
        for i in range(len(DATA)):
            for k in range(1,int(DATA[i]['NbColumn']),1):
                x=DATA[i]['DATA'][0]
                plt.plot(x,DATA[i]['DATA'][k])
                plt.axis([x[0],x[-1],0,1])
            plt.xlabel('Wavelength (nm)')
            plt.ylabel('EQE (-)')
            text='Jsc= '
            for m in range(len(DATA[i]['Jsc'])):
                text += '%.2f' % DATA[i]['Jsc'][m]+ '; '
            text+='Eg= '
            for m in range(len(DATA[i]['Eg'])):
                text += '%.2f' % DATA[i]['Eg'][m]+ '; '
            text=text[:-2]
            plt.annotate(DATA[i]['Name']+' - '+text, xy=(0.1,1.01), xycoords='axes fraction', fontsize=12,
                                                horizontalalignment='left', verticalalignment='bottom')
            plt.savefig(DATA[i]['Name']+'.png')
            plt.clf()
        
        plt.close()
        self.destroy()
        self.__init__()
        self.UpdateEQEGraph()
#        self.initlistbox()
     
    def WriteEQEtoDatabase(self):
        DATA=self.DATA 
        
        #connection to DB
        path =filedialog.askopenfilenames(title="Please select the DB file")[0]
        self.db_conn=sqlite3.connect(path)
        self.theCursor=self.db_conn.cursor()
        
        self.theCursor.execute("SELECT batchname FROM batch")
        batchnamesdb=self.theCursor.fetchall()
        print(batchnamesdb)
        self.theCursor.execute("SELECT samplename FROM samples")
        batchnamesdb=self.theCursor.fetchall()
        print(batchnamesdb)
        
        print("EQEs...")
        
        #only take samles highlighted in table (same process as for plotting)
        for i in range(len(DATA)):
            batchname=DATA[i]["batchnumb"]
            samplenumber=DATA[i]["samplenumb"]
            samplenumber = batchname+'_'+samplenumber
            print(samplenumber)
            
            self.theCursor.execute("SELECT id FROM batch WHERE batchname=?",(batchname,))
            batch_id_exists = self.theCursor.fetchone()[0]
            self.theCursor.execute("SELECT id FROM samples WHERE samplename=?",(samplenumber,))            
            sample_id_exists = self.theCursor.fetchone()[0]
            self.theCursor.execute("SELECT id FROM cells WHERE samples_id=? AND batch_id=?",(sample_id_exists, batch_id_exists))            
            cellletter_id_exists = self.theCursor.fetchall()[0][0]
            print(cellletter_id_exists)

            if batch_id_exists and sample_id_exists and cellletter_id_exists:
                for j in range(len(DATA[i]['Jsc'])):
                    uniquedatentry=DATA[i]['Name']+str(DATA[i]['dateTime'])+str(DATA[i]['Jsc'][j])
                    uniquedatentry=uniquedatentry.replace(' ','')
                    uniquedatentry=uniquedatentry.replace(':','')
                    uniquedatentry=uniquedatentry.replace('.','')
                    uniquedatentry=uniquedatentry.replace('-','')
                    uniquedatentry=uniquedatentry.replace('_','')
                    try:
                        self.db_conn.execute("""INSERT INTO eqemeas (
                                EQEmeasname,
                                EQEmeasnameDateTimeEQEJsc,
                                commenteqe,
                                DateTimeEQE,
                                Vbias,
                                filter,
                                LEDbias,
                                integJsc,
                                Eg,
                                EgTauc,
                                EgLn,
                                linktofile,
                                samples_id,
                                batch_id,
                                cells_id
                            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (DATA[i]['Name'],
                             uniquedatentry,
                             DATA[i]['comment'],
                             DATA[i]['dateTime'],
                             DATA[i]['Vbias'][j],
                             DATA[i]['filterbias'][j],
                             DATA[i]['ledbias'][j],
                             DATA[i]['Jsc'][j],
                             DATA[i]['Eg'][j],
                             DATA[i]['EgTauc'][j][0],
                             DATA[i]['EgLn'][j],
                             DATA[i]['filepath'],
                             sample_id_exists,
                             batch_id_exists,
                             cellletter_id_exists))
                        self.db_conn.commit()
                    except sqlite3.IntegrityError:
                        print("the file already exists in the DB")
        
        #disconnect from DB
        self.theCursor.close()
        self.db_conn.close()
        
        #exit window
        print("it's in the DB!")
        messagebox.showinfo("Information","it's in the DB!")
        
#%%#############         
    def SampleNames(self, DATAx):#for DATAFORGRAPH
        Names = list(self.names)
        for item in range(len(DATAx)):
            Names.append(DATAx[item][0]+'_'+ '%.2f' % DATAx[item][1])
        return tuple(Names)
    
    def UpdateEQEGraph(self):
        global titEQE
        global takenforplot
        global DATAFORGRAPH
        global DATAforexport
        global colorstylelist
        
#        takenforplot=list(self.listboxsamples.curselection())
        
        DATAx=DATAFORGRAPH
        
        sampletotake=[]
        DATAforexport=[]
        
        if takenforplot!=[]:
            sampletotake=takenforplot
            #print(sampletotake)
        
        if self.YtypeChoice.get()=="linear":
            self.EQEgraph.clear()
            EQEfig=self.EQEgraph
            for i in range(len(sampletotake)):
                x = DATAx[sampletotake[i]][2]
                y = DATAx[sampletotake[i]][3]
                
                colx=["Wavelength","nm"," "]+x
                coly=["EQE","-",DATAx[sampletotake[i]][5]]+y
                DATAforexport.append(colx)
                DATAforexport.append(coly)
                
                if self.CheckLegend.get()==1:
                    if self.CheckLegJsc.get()==0 and self.CheckLegEg.get()==0:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][5],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                    elif self.CheckLegJsc.get()==1 and self.CheckLegEg.get()==0:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][6],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                    elif self.CheckLegJsc.get()==0 and self.CheckLegEg.get()==1:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][7],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                    elif self.CheckLegJsc.get()==1 and self.CheckLegEg.get()==1:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][8],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                else:
                    EQEfig.plot(x,y,linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                
                if self.CheckTangent.get()==1:
                    m=DATAx[sampletotake[i]][11]
                    h=DATAx[sampletotake[i]][12]
                    x2=1239.8/DATAx[sampletotake[i]][4]
                    x=np.linspace(x2-100,x2,10)
                    #x=np.array(range(int(round(x2-100)),int(round(x2))))
                    y=eval('m*x+h')
                    EQEfig.plot(x,y)
                        
            self.EQEgraph.set_ylabel('EQE (-)', fontsize=14)
            self.EQEgraph.set_xlabel('Wavelength (nm)', fontsize=14)
            if titEQE:
                self.EQEgraph.set_title(self.titleEQE.get())
            if self.CheckLegend.get()==1:
                if self.pos1.get()==5:
                    self.leg=EQEfig.legend(bbox_to_anchor=(1, 0.5), loc=2, ncol=1)
                elif self.pos1.get()==1 or self.pos1.get()==2  or self.pos1.get()==3 or self.pos1.get()==4:   
                    self.leg=EQEfig.legend(loc=self.pos1.get())
                else:
                    self.leg=EQEfig.legend(loc=0)
            self.EQEgraph.axis([self.minx.get(),self.maxx.get(),self.miny.get(),self.maxy.get()])
            plt.gcf().canvas.draw()
            
        elif self.YtypeChoice.get()=="log":
            self.EQEgraph.clear()
            EQEfig=self.EQEgraph
            for i in range(len(sampletotake)):
                x = DATAx[sampletotake[i]][15]
                y = DATAx[sampletotake[i]][16]
                
                colx=["Energy","eV"," "]+x
                coly=["Ln(EQE)","-",DATAx[sampletotake[i]][5]]+y
                DATAforexport.append(colx)
                DATAforexport.append(coly)
                
                if self.CheckLegend.get()==1:
                    if self.CheckLegJsc.get()==0 and self.CheckLegEg.get()==0:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][5],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                    elif self.CheckLegJsc.get()==1 and self.CheckLegEg.get()==0:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][6],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                    elif self.CheckLegJsc.get()==0 and self.CheckLegEg.get()==1:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][24],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                    elif self.CheckLegJsc.get()==1 and self.CheckLegEg.get()==1:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][25],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                else:
                    EQEfig.plot(x,y,linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                
                if self.CheckTangent.get()==1:
                    m=DATAx[sampletotake[i]][13]
                    h=DATAx[sampletotake[i]][14]
                    x2=DATAx[sampletotake[i]][4]
                    x=np.linspace(x2-0.1,x2+0.1,10)
                    y=eval('m*x+h')
                    EQEfig.plot(x,y)
                    EQEfig.plot(DATAx[sampletotake[i]][17],DATAx[sampletotake[i]][18],'ro')
                    
            self.EQEgraph.set_ylabel('Ln(EQE) (-)', fontsize=14)
            self.EQEgraph.set_xlabel('Energy (eV)', fontsize=14)
            if titEQE:
                self.EQEgraph.set_title(self.titleEQE.get())
            if self.CheckLegend.get()==1:
                if self.pos1.get()==5:
                    self.leg=EQEfig.legend(bbox_to_anchor=(1, 0.5), loc=2, ncol=1)
                elif self.pos1.get()==1 or self.pos1.get()==2  or self.pos1.get()==3 or self.pos1.get()==4:   
                    self.leg=EQEfig.legend(loc=self.pos1.get())
                else:
                    self.leg=EQEfig.legend(loc=0)
            if self.CheckAutoscale.get()==0:
                self.EQEgraph.axis([self.minx.get(),self.maxx.get(),self.miny.get(),self.maxy.get()])
            plt.gcf().canvas.draw()
            
        elif self.YtypeChoice.get()=="Tauc":
            self.EQEgraph.clear()
            EQEfig=self.EQEgraph
            for i in range(len(sampletotake)):
                x = DATAx[sampletotake[i]][20]
                y = DATAx[sampletotake[i]][21]                
                
                colx=["Energy","eV"," "]+x
                coly=["Ln(1-EQE)^2 * E^2","a.u.",DATAx[sampletotake[i]][5]]+y
                DATAforexport.append(colx)
                DATAforexport.append(coly)
                
                if self.CheckLegend.get()==1:
                    if self.CheckLegJsc.get()==0 and self.CheckLegEg.get()==0:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][5],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                    elif self.CheckLegJsc.get()==1 and self.CheckLegEg.get()==0:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][6],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                    elif self.CheckLegJsc.get()==0 and self.CheckLegEg.get()==1:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][26],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                    elif self.CheckLegJsc.get()==1 and self.CheckLegEg.get()==1:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][27],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                else:
                    EQEfig.plot(x,y,linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                
                if self.CheckTangent.get()==1:
                    m=DATAx[sampletotake[i]][22]
                    h=DATAx[sampletotake[i]][23]
                    x2=DATAx[sampletotake[i]][19]
                    x=np.linspace(x2,x2+0.1,10)
                    y=eval('m*x+h')
                    EQEfig.plot(x,y)
                
            self.EQEgraph.set_ylabel('Ln(1-EQE)^2 * E^2 (a.u.)', fontsize=14)
            self.EQEgraph.set_xlabel('Energy (eV)', fontsize=14)
            if titEQE:
                self.EQEgraph.set_title(self.titleEQE.get())
            if self.CheckLegend.get()==1:
                if self.pos1.get()==5:
                    self.leg=EQEfig.legend(bbox_to_anchor=(1, 0.5), loc=2, ncol=1)
                elif self.pos1.get()==1 or self.pos1.get()==2  or self.pos1.get()==3 or self.pos1.get()==4:   
                    self.leg=EQEfig.legend(loc=self.pos1.get())
                else:
                    self.leg=EQEfig.legend(loc=0)
            if self.CheckAutoscale.get()==0:        
                self.EQEgraph.axis([self.minx.get(),self.maxx.get(),self.miny.get(),self.maxy.get()])
            plt.gcf().canvas.draw()
    
        elif self.YtypeChoice.get()=="NormalizedBySingle":
            self.EQEgraph.clear()
            EQEfig=self.EQEgraph
            for i in range(len(sampletotake)):
                x = DATAx[sampletotake[i]][2]
                y1 = DATAx[sampletotake[i]][3]
                
                y=[(m-min(y1))/(max(y1)-min(y1)) for m in y1]
                
                colx=["Wavelength","nm"," "]+x
                coly=["Norm. EQE","-",DATAx[sampletotake[i]][5]]+y
                DATAforexport.append(colx)
                DATAforexport.append(coly)
                
                if self.CheckLegend.get()==1:
                    if self.CheckLegJsc.get()==0 and self.CheckLegEg.get()==0:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][5],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                    elif self.CheckLegJsc.get()==1 and self.CheckLegEg.get()==0:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][6],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                    elif self.CheckLegJsc.get()==0 and self.CheckLegEg.get()==1:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][7],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                    elif self.CheckLegJsc.get()==1 and self.CheckLegEg.get()==1:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][8],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                else:
                    EQEfig.plot(x,y,linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
            self.EQEgraph.set_ylabel('Norm. EQE (-)', fontsize=14)
            self.EQEgraph.set_xlabel('Wavelength (nm)', fontsize=14)
            if titEQE:
                self.EQEgraph.set_title(self.titleEQE.get())
            if self.CheckLegend.get()==1:
                if self.pos1.get()==5:
                    self.leg=EQEfig.legend(bbox_to_anchor=(1, 0.5), loc=2, ncol=1)
                elif self.pos1.get()==1 or self.pos1.get()==2  or self.pos1.get()==3 or self.pos1.get()==4:   
                    self.leg=EQEfig.legend(loc=self.pos1.get())
                else:
                    self.leg=EQEfig.legend(loc=0)
            self.EQEgraph.axis([self.minx.get(),self.maxx.get(),self.miny.get(),self.maxy.get()])
            plt.gcf().canvas.draw()
            
        elif self.YtypeChoice.get()=="NormalizedByAll":
            self.EQEgraph.clear()
            EQEfig=self.EQEgraph
            AllY=[]
            for i in range(len(sampletotake)):
                AllY+=DATAx[sampletotake[i]][3]
            miny=min(AllY)
            maxy=max(AllY)
            
            for i in range(len(sampletotake)):
                x = DATAx[sampletotake[i]][2]
                y1 = DATAx[sampletotake[i]][3]
                
                y=[(m-miny)/(maxy-miny) for m in y1]
                
                colx=["Wavelength","nm"," "]+x
                coly=["Norm. EQE","-",DATAx[sampletotake[i]][5]]+y
                DATAforexport.append(colx)
                DATAforexport.append(coly)
                
                if self.CheckLegend.get()==1:
                    if self.CheckLegJsc.get()==0 and self.CheckLegEg.get()==0:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][5],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                    elif self.CheckLegJsc.get()==1 and self.CheckLegEg.get()==0:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][6],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                    elif self.CheckLegJsc.get()==0 and self.CheckLegEg.get()==1:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][7],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                    elif self.CheckLegJsc.get()==1 and self.CheckLegEg.get()==1:
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][8],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
                else:
                    EQEfig.plot(x,y,linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10])
            self.EQEgraph.set_ylabel('Norm. EQE (-)', fontsize=14)
            self.EQEgraph.set_xlabel('Wavelength (nm)', fontsize=14)
            if titEQE:
                self.EQEgraph.set_title(self.titleEQE.get())
            if self.CheckLegend.get()==1:
                if self.pos1.get()==5:
                    self.leg=EQEfig.legend(bbox_to_anchor=(1, 0.5), loc=2, ncol=1)
                elif self.pos1.get()==1 or self.pos1.get()==2  or self.pos1.get()==3 or self.pos1.get()==4:   
                    self.leg=EQEfig.legend(loc=self.pos1.get())
                else:
                    self.leg=EQEfig.legend(loc=0)
            self.EQEgraph.axis([self.minx.get(),self.maxx.get(),self.miny.get(),self.maxy.get()])
            plt.gcf().canvas.draw()
            
#%%#############             
    def GiveEQEatitle(self):
        self.window = tk.Toplevel()
        self.window.wm_title("Change title of EQE graph")
        center(self.window)
        self.window.geometry("325x55")
        self.titleEQE = tk.StringVar()
        entry=Entry(self.window, textvariable=self.titleEQE,width=40)
        entry.grid(row=0,column=0,columnspan=1)
        self.addtitlebutton = Button(self.window, text="Update",
                            command = self.giveEQEatitleupdate)
        self.addtitlebutton.grid(row=1, column=0, columnspan=1)
    def giveEQEatitleupdate(self): 
        global titEQE
        titEQE=1
        self.UpdateEQEGraph()
        
    def ExportEQEGraph(self):
        global DATAforexport 
        #graphname = self.entrytext.get()
        #plt.savefig(graphname +'.png', bbox_extra_artists=(self.leg,), bbox_inches='tight') 
        try:
            if self.CheckLegend.get()==1:
                f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
                self.fig1.savefig(f, dpi=300, bbox_extra_artists=(self.leg,), transparent=True) 
            else:
                f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
                self.fig1.savefig(f, dpi=300, transparent=True)
                    
            DATAforexport=map(list, six.moves.zip_longest(*DATAforexport, fillvalue=' '))

            DATAforexport1=[]
            for item in DATAforexport:
                line=""
                for item1 in item:
                    line=line+str(item1)+"\t"
                line=line[:-1]+"\n"
                DATAforexport1.append(line)
                
            file = open(str(f[:-4]+"_dat.txt"),'w')
            file.writelines("%s" % item for item in DATAforexport1)
            file.close() 
        except:
            print("there is an exception...check legend maybe...")
             
    class PopulateListofSampleStylingEQE(tk.Frame):
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
            global DATAFORGRAPH
            global takenforplot
            global colorstylelist
            global listofanswer
            global listoflinestyle
            global listofcolorstyle
            DATAx=DATAFORGRAPH
            listofanswer=[]
            sampletotake=[]
            if takenforplot!=[]:
                for item in takenforplot:
                    sampletotake.append(DATAx[item][0])
                    
            listoflinestyle=[]
            listofcolorstyle=[]
            for item in range(len(DATAx)):
                listoflinestyle.append(DATAx[item][9])
                listofcolorstyle.append(DATAx[item][10])
                listofanswer.append(DATAx[item][0])
            
            
            rowpos=1
            forbiddenrange=[]
            for itemm in sampletotake:
                for item1 in range(len(DATAx)): 
                    if item1 not in forbiddenrange:
                        if DATAx[item1][0] == itemm:
                            #print(itemm)
                            forbiddenrange.append(item1)
                            label=tk.Label(self.frame,text=DATAx[item1][0],fg='black',background='white')
                            label.grid(row=rowpos,column=0, columnspan=1)
                            textinit = tk.StringVar()
                            #self.listofanswer.append(Entry(self.window,textvariable=textinit))
                            listofanswer[item1]=Entry(self.frame,textvariable=textinit)
                            listofanswer[item1].grid(row=rowpos,column=1, columnspan=2)
                            textinit.set(DATAx[item1][5])
                
                            linestylelist = ["-","--","-.",":"]
                            listoflinestyle[item1]=tk.StringVar()
                            listoflinestyle[item1].set(DATAx[item1][9]) # default choice
                            OptionMenu(self.frame, listoflinestyle[item1], *linestylelist, command=()).grid(row=rowpos, column=4, columnspan=2)
                             
                            """
                            listofcolorstyle[item1]=tk.StringVar()
                            listofcolorstyle[item1].set(DATAx[item1][10]) # default choice
                            OptionMenu(self.frame, listofcolorstyle[item1], *colorstylelist, command=()).grid(row=rowpos, column=6, columnspan=2)
                            """
                            self.positioncolor=item1
                            colstyle=Button(self.frame, text='Select Color', foreground=listofcolorstyle[item1], command=partial(self.getColor,item1))
                            colstyle.grid(row=rowpos, column=6, columnspan=2)
                            rowpos=rowpos+1
                        else:
                            listofanswer[item1]=str(DATAx[item1][5])
                            listoflinestyle.append(str(DATAx[item1][9]))
                            listofcolorstyle.append(str(DATAx[item1][10]))
            #print(listofanswer)
            
        def getColor(self,rowitem):
            global listofcolorstyle
            color = askcolor(color="red", parent=self.frame, title="Color Chooser", alpha=False)
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
        global DATAFORGRAPH
        global takenforplot
        DATAx=DATAFORGRAPH
        sampletotake=[]
        if takenforplot!=[]:
            for item in takenforplot:
                sampletotake.append(DATAx[item][0])
                    
        self.reorderwindow = tk.Tk()
        center(self.reorderwindow)
        self.listbox = self.Drag_and_Drop_Listbox(self.reorderwindow)
        for name in sampletotake:
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
        global DATAFORGRAPH
        global takenforplot
        takenforplot=[]
        sampletotake=list(self.listbox.get(0,tk.END))
        for item in sampletotake:
            for i in range(len(DATAFORGRAPH)):
                if DATAFORGRAPH[i][0]==item:
                    takenforplot.append(i)
        self.UpdateEQELegMod()
        self.reorderwindow.destroy()
        
    def ChangeLegendEQEgraph(self):       
        
        if self.CheckLegend.get()==1:        
            self.window = tk.Toplevel()
            self.window.wm_title("Change Legends")
            center(self.window)
            self.window.geometry("400x300")
            
            Button(self.window, text="Update",
                                command = self.UpdateEQELegMod).pack()
            
            Button(self.window, text="Reorder",
                                command = self.reorder).pack()
    
            self.PopulateListofSampleStylingEQE(self.window).pack(side="top", fill="both", expand=True)
        
    def UpdateEQELegMod(self):
        global DATAFORGRAPH
        global listofanswer
        global listoflinestyle
        global listofcolorstyle
        
        leglist=[]
        for e in listofanswer:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        for item in range(len(DATAFORGRAPH)):
            DATAFORGRAPH[item][5]=leglist[item]
            DATAFORGRAPH[item][6]= leglist[item]+'_'+'Jsc: %.2f' % DATAFORGRAPH[item][1]
            DATAFORGRAPH[item][7]= leglist[item]+'_'+'Eg: %.2f' % DATAFORGRAPH[item][4]
            DATAFORGRAPH[item][8]= leglist[item]+'_'+'Jsc: %.2f' % DATAFORGRAPH[item][1]+'_'+'Eg: %.2f' % DATAFORGRAPH[item][4]
        leglist=[]
        for e in listoflinestyle:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        for item in range(len(DATAFORGRAPH)):
            DATAFORGRAPH[item][9]=leglist[item]        
        leglist=[]
        for e in listofcolorstyle:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e) 
        for item in range(len(DATAFORGRAPH)):
            DATAFORGRAPH[item][10]=leglist[item]  
                
        
        self.UpdateEQEGraph()
        self.window.destroy()
        self.ChangeLegendEQEgraph()

    def CalcCurrent(self):
        try:
            self.window = tk.Toplevel()
            self.window.wm_title("Calculate the current in a wavelength range")
            center(self.window)
            self.window.geometry("500x55")
    
            self.x0 = tk.DoubleVar()
            entry=Entry(self.window, textvariable=self.x0,width=10)
            entry.grid(row=0,column=0,columnspan=1)
            self.x0.set(320)
            self.x1 = tk.DoubleVar()
            entry=Entry(self.window, textvariable=self.x1,width=10)
            entry.grid(row=0,column=1,columnspan=1)
            self.x1.set(820)
            #self.calculatedJ = tk.Text(self.window)
            #self.calculatedJ.grid(row=0,column=2,columnspan=1)
            self.calculatedJ = tk.StringVar()
            entry=Entry(self.window, textvariable=self.calculatedJ,width=10)
            entry.grid(row=0,column=2,columnspan=1)
            self.calculatedJ.set('0')
            
            self.calcbutton = Button(self.window, text="Calculate",
                                command = self.dotheintegral)
            self.calcbutton.grid(row=1, column=0, columnspan=1)
            
            self.selectedEQEforcalc = tk.StringVar()
            w=OptionMenu(self.window,self.selectedEQEforcalc, *self.names)
            w.grid(row=1,column=1,columnspan=2)
            
        except:
            print("exception...")
        
    def dotheintegral(self):
        global DATAFORGRAPH
        itempos=0
        item=0
        for item in range(len(DATAFORGRAPH)):
            if DATAFORGRAPH[item][0]+'_'+'%.2f' % float(DATAFORGRAPH[item][1])==self.selectedEQEforcalc.get():
                itempos=item
                break
        try:    
            x = DATAFORGRAPH[itempos][2]
            y = DATAFORGRAPH[itempos][3]
            f = interp1d(x, y, kind='cubic')
            x2 = lambda x: self.AM15GParticlesinnm(x)*f(x)
            integral = echarge/10*integrate.quad(x2,self.x0.get(),self.x1.get())[0]
            self.calculatedJ.set('%.2f' % integral)
        except ValueError:
            print("a limit value is outside of interpolation range")
    
    def SelectData(self):
        global DATAFORGRAPH
        
        self.frame221.destroy()
        self.frame221=Frame(self.frame22,borderwidth=0,  bg="white")
        self.frame221.pack(fill=tk.BOTH,expand=1)
        frame = self.frame221
        

        scrollbar = Scrollbar(frame)
        scrollbar.grid(row=1, column=2,sticky="ns")
        
        valores = StringVar()
        self.names = ()
        self.names=self.SampleNames(DATAFORGRAPH)
              
        self.lstbox = Listbox(frame, listvariable=valores, selectmode=MULTIPLE, yscrollcommand=scrollbar.set)
        self.lstbox.grid(column=0, row=1, columnspan=2)
        scrollbar.config(command=self.lstbox.yview)
        btn = Button(frame, text="Update", command=self.select)
        btn.grid(column=1, row=0)
        
        for item in self.names:
            self.lstbox.insert(END,item)
        
    def select(self):
        global takenforplot
        takenforplot=list(self.lstbox.curselection())
        self.UpdateEQEGraph()
     
#%%#############         
###############################################################################        
if __name__ == '__main__':
    
    app = EQEApp()
    app.mainloop()


