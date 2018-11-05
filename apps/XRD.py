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
import csv
from scipy.optimize import curve_fit
import peakutils
from peakutils.plot import plot as pplot


"""
TODOLIST


"""
#%%
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
    
class XRDApp(Toplevel):

    def __init__(self, *args, **kwargs):
        
        Toplevel.__init__(self, *args, **kwargs)
        Toplevel.wm_title(self, "XRDApp")
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
        
        label = tk.Label(self.canvas0, text="XRD DATA Analyzer", font=LARGE_FONT, bg="black",fg="white")
        label.pack(fill=tk.X,expand=0)
        
        frame1=Frame(self.canvas0,borderwidth=0,  bg="white")
        frame1.pack(fill=tk.BOTH,expand=1)
        frame1.bind("<Configure>", self.onFrameConfigure)
        self.fig1 = plt.figure(figsize=(1, 1))
        canvas = FigureCanvasTkAgg(self.fig1, frame1)
        canvas.get_tk_widget().pack(fill=tk.BOTH,expand=1)
        self.XRDgraph = plt.subplot2grid((1, 1), (0, 0), colspan=3)
        self.toolbar = NavigationToolbar2TkAgg(canvas, frame1)
        self.toolbar.update()
        canvas._tkcanvas.pack(fill = tk.BOTH, expand = 1) 
        
        frame2=Frame(self.canvas0,borderwidth=0,  bg="white")
        frame2.pack(fill=tk.X,expand=0)
        
        frame21=Frame(frame2,borderwidth=0,  bg="white")
        frame21.pack(side=tk.LEFT,fill=tk.X,expand=1)
        frame211=Frame(frame21,borderwidth=0,  bg="white")
        frame211.pack(fill=tk.X,expand=0)
        self.shift = tk.DoubleVar()
        Entry(frame211, textvariable=self.shift,width=5).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.shiftBut = Button(frame211, text="Shift to ref peak",command = ()).pack(side=tk.LEFT,expand=1)
        self.shift.set(0)
        frame212=Frame(frame21,borderwidth=0,  bg="white")
        frame212.pack(fill=tk.X,expand=0)
        self.CheckBkgRemoval = IntVar()
        legend=Checkbutton(frame212,text='BkgRemoval',variable=self.CheckBkgRemoval, 
                           onvalue=1,offvalue=0,height=1, width=10, command = (), bg="white")
        legend.pack(side=tk.LEFT,expand=1)
        frame213=Frame(frame21,borderwidth=0,  bg="white")
        frame213.pack(fill=tk.X,expand=0)
        self.rescale = tk.DoubleVar()
        Entry(frame213, textvariable=self.rescale,width=5).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.rescale.set(990)
        self.rescaleBut = Button(frame213, text="Rescale to ref",command = ()).pack(side=tk.LEFT,expand=1)

        
        frame22=Frame(frame2,borderwidth=0,  bg="blue")
        frame22.pack(side=tk.LEFT,fill=tk.X,expand=1)
        frame221=Frame(frame22,borderwidth=0,  bg="white")
        frame221.pack(fill=tk.X,expand=0)
        self.importBut = Button(frame221, text="Import",command = ()).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.UpdateBut = Button(frame221, text="Update",command = ()).pack(side=tk.LEFT,fill=tk.X,expand=1)
        frame222=Frame(frame22,borderwidth=0,  bg="white")
        frame222.pack(fill=tk.X,expand=0)
        self.ShowPeakDetectionBut = Button(frame222, text="Show Peak Detection",command = ()).pack(side=tk.LEFT,fill=tk.X,expand=1)
        frame223=Frame(frame22,borderwidth=0,  bg="white")
        frame223.pack(fill=tk.X,expand=0)
        self.thresholdPeakDet = tk.DoubleVar()
        Entry(frame223, textvariable=self.thresholdPeakDet,width=5).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.thresholdPeakDet.set(0.05)
        tk.Label(frame223, text="Threshold", bg="white").pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.MinDistPeakDet = tk.DoubleVar()
        Entry(frame223, textvariable=self.MinDistPeakDet,width=5).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.MinDistPeakDet.set(40)
        tk.Label(frame223, text="MinDist", bg="white").pack(side=tk.LEFT,fill=tk.X,expand=1)

        
        frame23=Frame(frame2,borderwidth=0,  bg="red")
        frame23.pack(fill=tk.X,expand=0)
        self.ExportBut = Button(frame23, text="Export",command = ()).pack(fill=tk.X,expand=1)
        self.GraphCheck = IntVar()
        legend=Checkbutton(frame23,text='Graph',variable=self.GraphCheck, 
                           onvalue=1,offvalue=0,height=1, width=10, command = (), bg="white")
        legend.pack(expand=1)
        self.PeakData = IntVar()
        legend=Checkbutton(frame23,text='PeakData',variable=self.PeakData, 
                           onvalue=1,offvalue=0,height=1, width=10, command = (), bg="white")
        legend.pack(expand=1)
        
        
        frame3=Frame(self.canvas0,borderwidth=0,  bg="white")
        frame3.pack(fill=tk.X,expand=0)
        
        
        
        

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
    def onFrameConfigure(self, event):
        #self.canvas0.configure(scrollregion=self.canvas0.bbox("all"))
        self.canvas0.configure(scrollregion=(0,0,500,500))
            
    
     
#%%#############         
###############################################################################        
if __name__ == '__main__':
    
    app = XRDApp()
    app.mainloop()


