#! python3

import os

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

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
import datetime
from creatingTables import CreateAllTables
from DatabaseReading_v0 import DBReadingapp
from mergingDBs_v1 import mergingapp
#%% 

"""
TODOLIST

- to modify data in the db: use "DB browser for SQlite"

- merge several .db files in one: works but not universal.

- other charac table: in principle this should be a many-to-many table. for simplicity, it is now a many-to-one. so the charac are joined in 1 string and not individually accessible.


- add entries for thickness
- deposition method: hybrid sequential, solution sequential, solution 1-step, antisolvent drip



modified tables: (still need to modify the mergingdb app)
    PkAbsorberMethod
    
"""
#%% 
newsampleslist=[]
newsampleslistnames=[]
newsampleslistforlistbox=[]

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
    
#%% 

class DBapp(Toplevel):

    def __init__(self, *args, **kwargs):
        
        Toplevel.__init__(self, *args, **kwargs)
        Toplevel.wm_title(self, "DBapp")
        Toplevel.config(self,background="white")
        self.wm_geometry("500x150")
        center(self)
        self.initUI()


    def initUI(self):
        self.master.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.canvas0 = tk.Canvas(self, borderwidth=0, background="#ffffff")
        #self.superframe=Frame(self.canvas0,background="#ffffff")
        self.canvas0.pack(side="left", fill="both", expand=True)
        
        label = tk.Label(self.canvas0, text="Welcome to the\nUltimate Database Managing System", font=12, bg="black",fg="white")
        label.pack(fill=tk.X,expand=0)
        
        Button(self.canvas0, text="Fresh data to store?",
               command = self.connection_to_storage, width=20).pack(side=tk.LEFT,expand=1)
        
        Button(self.canvas0, text="You’ve got a question?",
               command = self.connection_to_question, width=20).pack(side=tk.LEFT,expand=1)
        
        Button(self.canvas0, text="Merging DBs",
               command = self.merging_dbs, width=20).pack(side=tk.LEFT,expand=1)
        
    def on_closing(self):        
        #if messagebox.askokcancel("Quit", "Do you want to quit?"):
        self.destroy()
        self.master.deiconify()
         
#%%#####################################################################################################
#################merging dbs###############################################################    
    def merging_dbs(self):
        mergingapp()
    
                    
#%%#####################################################################################################
#################CONNECTION TO STORAGE###############################################################    
    def connection_to_storage(self):
        
        self.withdraw()
        self.connectionwindow = tk.Toplevel()
        center(self.connectionwindow)
        self.connectionwindow.protocol("WM_DELETE_WINDOW", self.backtomain)
        self.connectionwindow.wm_geometry("420x170")
        self.connectionwindow.wm_title("Connection")
        
        tk.Label(self.connectionwindow, text="I have already a database somewhere…", 
                 font=("Verdana", 10), bg="black",fg="white").pack(fill=tk.X,expand=0)
        
        Button(self.connectionwindow, text="look for your .db file...",
               command = lambda: self.browseconnection(1)).pack(expand=0)
        
        tk.Label(self.connectionwindow, text="No, I’m new to this. Please create one for me:", 
                 font=("Verdana", 10), bg="black",fg="white").pack(fill=tk.X,expand=0)
        
        Button(self.connectionwindow, text="select a new filename and path",
               command = lambda: self.browseconnection(2)).pack(expand=0)
        
        frame3=Frame(self.connectionwindow,borderwidth=0,  bg="white")
        frame3.pack()
        tk.Label(frame3, text="  ", 
                 font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        self.connectionpath = tk.StringVar()
        self.connectentry=Entry(frame3, textvariable=self.connectionpath,width=50)
        self.connectentry.pack(side="left", fill=tk.X,expand=1)
        Button(frame3, text="connect",
               command = lambda: self.connecttoDB(self.connectionpath.get(),self.new)).pack(side="left", fill=tk.X,expand=0)
        Button(self.connectionwindow, text="go back",
               command = self.backtomain).pack(side="left")

    def browseconnection(self, a):
        try:
            if a==1:
                path =filedialog.askopenfilenames(title="Please select the DB file")[0]
                self.new=0
            elif a==2:
                path = filedialog.asksaveasfilename(defaultextension=".db")
                self.new=1
            self.connectionpath.set(path)
            self.connectentry.delete(0, END) #deletes the current value
            self.connectentry.insert(0, path)
        except IndexError:
            print("you did not select correctly a file")
            
    def connecttoDB(self, path, new):
        if path!="":
            if path[-3:]==".db":
                self.db_conn=sqlite3.connect(path)
                self.theCursor=self.db_conn.cursor()
                print("connected to database")
                self.connectionwindow.destroy()
                CreateAllTables(self.db_conn, new)
                self.howmodifyDB()
            else:
                print("not correct file extension")


#%%##############################################################################################    

    def connection_to_question(self):
        self.withdraw()
        DBReadingapp()
      
    def backtomain(self):
        try:
            self.connectionwindow.destroy()
        except: pass    
        try:    
            self.modDBwindow.destroy()
        except: pass    
        try:    
            self.newbatchwindow.destroy()
        except: pass    
        try:    
            self.newsampleswindow.destroy()
        except: pass    
            
        try:    
            self.theCursor.close()
            self.db_conn.close()
        except:
            pass
        self.deiconify()

#################END CONNECTION###############################################################    
#%%##############################################################################################

##########
    def howmodifyDB(self):
        self.modDBwindow = tk.Toplevel()
        center(self.modDBwindow)
        self.modDBwindow.protocol("WM_DELETE_WINDOW", self.backtomain)
        self.modDBwindow.wm_geometry("250x180")
        self.modDBwindow.wm_title("ModDB")

        tk.Label(self.modDBwindow, text=" ", font=("Verdana", 10)).pack()

        Button(self.modDBwindow, text="new batch?",
               command = self.newbatch, width=30).pack()
        
        tk.Label(self.modDBwindow, text="************************", font=("Verdana", 10)).pack()

        try:
            self.theCursor.execute("SELECT batchname FROM batch")
            result=self.theCursor.fetchall()
            if result!=[]:
                result1=[item[0] for item in result]
                    
                self.batchnamelist=tuple(result1)
                self.batchChoice=StringVar()
                self.batchChoice.set(self.batchnamelist[0])
                self.dropMenuFrame = OptionMenu(self.modDBwindow, self.batchChoice, *self.batchnamelist, command=())
                self.dropMenuFrame.pack()
                
#                Button(self.modDBwindow, text="modify existing batch?",
#                       command = (), width=30).pack()
                Button(self.modDBwindow, text="delete a batch with all its data?",
                       command = self.warningbefordelete, width=30).pack()
        except:
            print("exception...")
################################################
########deleting batch##########################        
    def warningbefordelete(self):
        result = messagebox.askquestion("Delete", "Are You Sure?\nThere is no way back if you click yes\nand all related data will be deleted!", icon='warning')
        if result == 'yes':
            self.db_conn.execute("DELETE from batch WHERE batchname=?",(self.batchChoice.get(),))
            self.db_conn.commit()
            self.backtomain()
        
#%%################################################       
##########new batch window######################
        
    def newbatch(self):
        self.modDBwindow.destroy()
        self.newbatchwindow = tk.Toplevel()
        center(self.newbatchwindow)
        self.newbatchwindow.protocol("WM_DELETE_WINDOW", self.backtomain)
        self.newbatchwindow.wm_geometry("300x200")
        self.newbatchwindow.wm_title("NewBatch")
        
        frame1=Frame(self.newbatchwindow,borderwidth=0,  bg="white")
        frame1.pack()
        tk.Label(frame1, text="Batch name, e.g. P999", font=("Verdana", 10)).pack(side="left",fill=tk.BOTH,expand=1)
        self.batchname = tk.StringVar()
        self.entry1=Entry(frame1, textvariable=self.batchname,width=10)
        self.entry1.pack(side="left",fill=tk.BOTH,expand=1)
        self.batchname.set("")
        
        frame1=Frame(self.newbatchwindow,borderwidth=0,  bg="white")
        frame1.pack()
        tk.Label(frame1, text="General topic", font=("Verdana", 10)).pack(side="left",fill=tk.BOTH,expand=1)
        self.topiclist=["nip", "pin","2TT","3TT","4TT","triple","layer charac"]
        self.topicChoice=StringVar()
        self.topicChoice.set(self.topiclist[0])
        self.dropMenuFrame = OptionMenu(frame1, self.topicChoice, *self.topiclist, command=())
        self.dropMenuFrame.pack(side="left",fill=tk.BOTH,expand=1)
        
        frame1=Frame(self.newbatchwindow,borderwidth=0,  bg="white")
        frame1.pack()
        tk.Label(frame1, text="Batch responsible", font=("Verdana", 10)).pack(side="left",fill=tk.BOTH,expand=1)

        self.usernamelist=[]
        result = self.theCursor.execute("SELECT username FROM users")
        for row in result:
            self.usernamelist.append(row[0])
        if self.usernamelist==[]:
            self.usernamelist=[""]
        self.usernamelist=tuple(self.usernamelist)
        self.UserChoice=StringVar()
        self.UserChoice.set(self.usernamelist[0])
        self.dropMenuFrame = OptionMenu(frame1, self.UserChoice, *self.usernamelist, command=())
        self.dropMenuFrame.pack(side="left",fill=tk.BOTH,expand=1)

        Button(frame1, text="Add new user",
               command = self.addnewUser).pack(side="left",fill=tk.BOTH,expand=1)
        
        frame1=Frame(self.newbatchwindow,borderwidth=0,  bg="white")
        frame1.pack()
        tk.Label(frame1, text="start date", font=("Verdana", 10)).pack(side="left",fill=tk.BOTH,expand=1)
        
        todaydate=datetime.date.today().strftime ("%Y-%m-%d")
        self.startbatchday = tk.StringVar()
        self.entry1=Entry(frame1, textvariable=self.startbatchday,width=2)
        self.entry1.pack(side="left",fill=tk.BOTH,expand=1)
        self.startbatchday.set(todaydate.split('-')[2])
        self.startbatchmonth = tk.StringVar()
        self.entry1=Entry(frame1, textvariable=self.startbatchmonth,width=2)
        self.entry1.pack(side="left",fill=tk.BOTH,expand=1)
        self.startbatchmonth.set(todaydate.split('-')[1])
        self.startbatchyear = tk.StringVar()
        self.entry1=Entry(frame1, textvariable=self.startbatchyear,width=4)
        self.entry1.pack(side="left",fill=tk.BOTH,expand=1)
        self.startbatchyear.set(todaydate.split('-')[0])
        
        frame1=Frame(self.newbatchwindow,borderwidth=0,  bg="white")
        frame1.pack()
        self.environmentalchecked=0
        self.selectCharacSetupschecked=0
        Button(frame1, text="Environment",
               command = self.addEnvironmentData).pack(side="left", fill=tk.Y,expand=0)
        Button(frame1, text="CharacSetupsUsed",
               command = self.selectCharacSetups).pack(side="left", fill=tk.Y,expand=0)

        frame1=Frame(self.newbatchwindow,borderwidth=0,  bg="white")
        frame1.pack()
        tk.Label(frame1, text="comment", font=("Verdana", 10)).pack(side="left",fill=tk.BOTH,expand=1)
        self.commentbatch = tk.StringVar()
        self.entry1=Entry(frame1, textvariable=self.commentbatch,width=30)
        self.entry1.pack(side="left",fill=tk.BOTH,expand=1)
        self.commentbatch.set("")
        
        tk.Label(self.newbatchwindow, text="  ", font=("Verdana", 10)).pack(fill=tk.BOTH,expand=1)

        frame1=Frame(self.newbatchwindow,borderwidth=0,  bg="white")
        frame1.pack()
        Button(frame1, text="Validate",
               command = self.newbatchvalidate).pack(side="left", fill=tk.BOTH,expand=1)
        Button(frame1, text="go back",
               command = self.backtomain).pack(side="left", fill=tk.BOTH,expand=1)
        
    def newbatchvalidate(self):
        if self.batchname.get()!="" and self.environmentalchecked==1 and self.selectCharacSetupschecked==1:
            #check the username, find its id in DB
            self.theCursor.execute("SELECT id FROM users WHERE username=?",(self.UserChoice.get(),))
            id_exists = self.theCursor.fetchone()
#            print(type(id_exists[0]))
                    
            goodtogo=0
    
            #insert the data in the table batch
            #get last id number, put id+1 for the foreign key toward environment
            self.theCursor.execute('SELECT max(id) FROM batch')
            max_id = self.theCursor.fetchone()[0]
            #print(max_id)
            if max_id==None:
                max_id=0
#            try:
            self.db_conn.execute("INSERT INTO batch (batchname, topic, startdate, commentbatch, users_id, environment_id, takencharacsetups_id) VALUES (?,?,?,?,?,?,?)",
                            (str(self.batchname.get()), str(self.topicChoice.get()), str(self.startbatchyear.get()+"-"+self.startbatchmonth.get()+"-"+self.startbatchday.get()), str(self.commentbatch.get()), id_exists[0], max_id+1, max_id+1))
            self.db_conn.commit()
            goodtogo=1
#            except sqlite3.OperationalError:
#                print("data couldn't be added to batch")
#            except sqlite3.IntegrityError:
#                print("the batchname already exists...")
#            except sqlite3.TypeError:
#                print("typeerror in batch")
                
            #get last id of batch table
            #insert data into environment
            goodtogo2=0
            try:
                self.db_conn.execute("INSERT INTO environment (RHyellowroom, Tempyellowroom, RHMC162, Tempmc162, gloveboxsolvent, solventGBwatervalue, solventGBoxygenvalue, evapGBwatervalue, evapGBoxygenvalue, commentenvir) VALUES (?,?,?,?,?,?,?,?,?,?)",
                                (self.rhyellowroom.get(), self.tempyellowroom.get(), self.rhmc162.get(), self.tempmc162.get(), self.GBsollev.get(),self.sGBwatlevel.get(),self.sGBo2level.get(),self.eGBwatlevel.get(),self.eGBo2level.get(),self.commentenvironment.get()))
                self.db_conn.commit()
                goodtogo2=1
            except sqlite3.OperationalError:
                print("data couldn't be added to environment")
            except sqlite3.TypeError:
                print("typeerror in environment")
            
            goodtogo3=0
            try:
                self.db_conn.execute("INSERT INTO takencharacsetups (takencharacsetupsname) VALUES (?)",
                                (self.CharacSetupsSelection,))
                self.db_conn.commit()
                goodtogo3=1
            except sqlite3.OperationalError:
                print("data couldn't be added to takencharacsetupsname")
            except sqlite3.TypeError:
                print("typeerror in takencharacsetupsname")
                        
            if goodtogo and goodtogo2 and goodtogo3:
                #close the batch window
                self.newbatchwindow.destroy()
                #move to the next window
                self.newsamples()
        elif self.batchname.get()=="":
            print("enter a batch name")
            messagebox.showinfo("", "enter a batch name")
        elif self.environmentalchecked==0:
            print("enter environmental data")
            messagebox.showinfo("", "enter environmental data")
        elif self.selectCharacSetupschecked==0:
            print("enter CharacSetups")
            messagebox.showinfo("", "enter CharacSetups")
            
    def selectCharacSetups(self):
        self.selectCharacSetupswin = tk.Toplevel()
        center(self.selectCharacSetupswin)
        self.selectCharacSetupswin.wm_geometry("400x270")
        self.selectCharacSetupswin.wm_title("selectCharacSetups")
        
        self.theCursor.execute("SELECT characsetupname FROM characsetups")
        characsetupsinDB = self.theCursor.fetchall()
#        print(characsetupsinDB)
        
        frame0=Frame(self.selectCharacSetupswin,borderwidth=0,  bg="white")
        frame0.pack(fill=tk.BOTH, expand=1)
        self.listboxsamplesCharacSetups=Listbox(frame0,width=20, height=5, selectmode=tk.EXTENDED)
        self.listboxsamplesCharacSetups.pack(side="left", fill=tk.BOTH, expand=1)
        scrollbar = tk.Scrollbar(frame0, orient="vertical")
        scrollbar.config(command=self.listboxsamplesCharacSetups.yview)
        scrollbar.pack(side="right", fill="y")
        self.listboxsamplesCharacSetups.config(yscrollcommand=scrollbar.set)
                
        for item in characsetupsinDB:
            self.listboxsamplesCharacSetups.insert(tk.END, item[0])
        
        
        frame1=Frame(self.selectCharacSetupswin,borderwidth=0,  bg="white")
        frame1.pack()
        Button(frame1, text="Validate",
               command = self.validateCharacSetups).pack(fill=tk.X,expand=0)
    
    def validateCharacSetups(self):
        datlist=self.listboxsamplesCharacSetups.curselection()
        
        self.CharacSetupsSelection = ""
        for item in datlist:
            self.CharacSetupsSelection=self.CharacSetupsSelection+self.listboxsamplesCharacSetups.get(item)+'/'
        
        self.selectCharacSetupschecked=1
#        print(self.CharacSetupsSelection)
        self.selectCharacSetupswin.destroy()
        
    def addEnvironmentData(self):
        self.Environmentwin = tk.Toplevel()
        center(self.Environmentwin)
        self.Environmentwin.wm_geometry("400x270")
        self.Environmentwin.wm_title("Environment")
        
        frame0=Frame(self.Environmentwin,borderwidth=0,  bg="white")
        frame0.pack()
        frame01=Frame(frame0,borderwidth=0,  bg="white")
        frame01.pack(side="left",fill=tk.BOTH,expand=1)
        tk.Label(frame01, text="RHyellowroom", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        tk.Label(frame01, text="Temp.yellowroom", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        tk.Label(frame01, text="RHmc162", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        tk.Label(frame01, text="Temp.mc162", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        tk.Label(frame01, text="GB solvent level", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        tk.Label(frame01, text="solvent GB water value", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        tk.Label(frame01, text="solvent GB oxygen value", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        tk.Label(frame01, text="evap GB water value", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        tk.Label(frame01, text="evap GB oxygen value", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        tk.Label(frame01, text="comment", font=("Verdana", 10)).pack(fill=tk.X,expand=1)

        
        frame02=Frame(frame0,borderwidth=0,  bg="white")
        frame02.pack(side="left",fill=tk.BOTH,expand=1)
        self.rhyellowroom = tk.DoubleVar()
        self.entry1=Entry(frame02, textvariable=self.rhyellowroom,width=4)
        self.rhyellowroom.set(-1)
        self.entry1.pack(fill=tk.X,expand=1)
        self.tempyellowroom = tk.DoubleVar()
        self.entry3=Entry(frame02, textvariable=self.tempyellowroom,width=30)
        self.entry3.pack(fill=tk.X,expand=1)
        self.tempyellowroom.set(-1)
        self.rhmc162 = tk.DoubleVar()
        self.entry1=Entry(frame02, textvariable=self.rhmc162,width=4)
        self.rhmc162.set(-1)
        self.entry1.pack(fill=tk.X,expand=1)
        self.tempmc162 = tk.DoubleVar()
        self.entry3=Entry(frame02, textvariable=self.tempmc162,width=30)
        self.entry3.pack(fill=tk.X,expand=1)
        self.tempmc162.set(-1)
        self.GBsollev = tk.DoubleVar()
        self.entry4=Entry(frame02, textvariable=self.GBsollev,width=30)
        self.entry4.pack(fill=tk.X,expand=1)
        self.GBsollev.set(-1)
        self.sGBwatlevel = tk.DoubleVar()
        self.entry4=Entry(frame02, textvariable=self.sGBwatlevel,width=30)
        self.entry4.pack(fill=tk.X,expand=1)
        self.sGBwatlevel.set(-1)
        self.sGBo2level = tk.DoubleVar()
        self.entry4=Entry(frame02, textvariable=self.sGBo2level,width=30)
        self.entry4.pack(fill=tk.X,expand=1)
        self.sGBo2level.set(-1)
        self.eGBwatlevel = tk.DoubleVar()
        self.entry4=Entry(frame02, textvariable=self.eGBwatlevel,width=30)
        self.entry4.pack(fill=tk.X,expand=1)
        self.eGBwatlevel.set(-1)
        self.eGBo2level = tk.DoubleVar()
        self.entry4=Entry(frame02, textvariable=self.eGBo2level,width=30)
        self.entry4.pack(fill=tk.X,expand=1)
        self.eGBo2level.set(-1)
        self.commentenvironment = tk.StringVar()
        self.entry6=Entry(frame02, textvariable=self.commentenvironment,width=30)
        self.entry6.pack(fill=tk.X,expand=1)
        self.commentenvironment.set("")

        self.environmentalchecked=1

        frame1=Frame(self.Environmentwin,borderwidth=0,  bg="white")
        frame1.pack()
        Button(frame1, text="Validate",
               command = self.Environmentwin.destroy).pack(fill=tk.X,expand=0)
        
    def addnewUser(self):
        self.newUserwin = tk.Toplevel()
        center(self.newUserwin)
        self.newUserwin.wm_geometry("270x170")
        self.newUserwin.wm_title("NewUser")
        
        frame0=Frame(self.newUserwin,borderwidth=0,  bg="white")
        frame0.pack()
        frame01=Frame(frame0,borderwidth=0,  bg="white")
        frame01.pack(side="left",fill=tk.BOTH,expand=1)
        tk.Label(frame01, text="username", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        tk.Label(frame01, text="firstname", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        tk.Label(frame01, text="lastname", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        tk.Label(frame01, text="affiliation", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        tk.Label(frame01, text="email", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        tk.Label(frame01, text="comment", font=("Verdana", 10)).pack(fill=tk.X,expand=1)

        
        frame02=Frame(frame0,borderwidth=0,  bg="white")
        frame02.pack(side="left",fill=tk.BOTH,expand=1)
        self.username = tk.StringVar()
        self.entry1=Entry(frame02, textvariable=self.username,width=30)
        self.username.set("JDoe")
        self.entry1.pack(fill=tk.X,expand=1)
        
        self.firstname = tk.StringVar()
        self.entry2=Entry(frame02, textvariable=self.firstname,width=30)
        self.entry2.pack(fill=tk.X,expand=1)
        self.firstname.set("John")
        self.lastname = tk.StringVar()
        self.entry3=Entry(frame02, textvariable=self.lastname,width=30)
        self.entry3.pack(fill=tk.X,expand=1)
        self.lastname.set("Doe")
        self.affiliation = tk.StringVar()
        self.entry4=Entry(frame02, textvariable=self.affiliation,width=30)
        self.entry4.pack(fill=tk.X,expand=1)
        self.affiliation.set("Univ. of Whatever")
        self.email = tk.StringVar()
        self.entry5=Entry(frame02, textvariable=self.email,width=30)
        self.entry5.pack(fill=tk.X,expand=1)
        self.email.set("john.doe@server.com")
        self.comment = tk.StringVar()
        self.entry6=Entry(frame02, textvariable=self.comment,width=30)
        self.entry6.pack(fill=tk.X,expand=1)
        self.comment.set("")
        
        
        frame1=Frame(self.newUserwin,borderwidth=0,  bg="white")
        frame1.pack()
        Button(frame1, text="Validate",
               command = self.addnewUserValidate).pack(fill=tk.X,expand=0)

    def addnewUserValidate(self):
       
        self.UserChoice.set(self.username.get())
        self.dropMenuFrame['menu'].delete(0, 'end')
        goodtogo=0
        try:
            self.db_conn.execute("INSERT INTO users (username, firstname, lastname, affiliation, email, commentusers) VALUES (?,?,?,?,?,?)",
                            (self.username.get(), self.firstname.get(), self.lastname.get(), self.affiliation.get(), self.email.get(), self.comment.get()))
            self.db_conn.commit()
            goodtogo=1
        except sqlite3.OperationalError:
            print("data couldn't be added to users")
            goodtogo=0
        except sqlite3.IntegrityError:
            print("the username already exists...")
            goodtogo=0
        
        if goodtogo:
            self.usernamelist=[]
            result = self.theCursor.execute("SELECT username FROM users")
            for row in result:
                self.usernamelist.append(row[0])
            self.usernamelist=tuple(self.usernamelist)
            for choice in self.usernamelist:
                self.dropMenuFrame['menu'].add_command(label=choice, command=tk._setit(self.UserChoice, choice))
    
            self.newUserwin.destroy()
        
#%%############end batch###########################     
##########new samples window###################### to do : compatibility with triple junction
            #if tandem, should add bottom cell reference number to link to SiliconDB: bottomCellDBRef in samples table
        
    def newsamples(self):
        self.newsampleswindow = tk.Toplevel()
        center(self.newsampleswindow)
        self.newsampleswindow.protocol("WM_DELETE_WINDOW", self.backtomain)
        if self.topicChoice.get()!="triple":
            self.newsampleswindow.wm_geometry("650x500")
        elif self.topicChoice.get()=="triple":
            self.newsampleswindow.wm_geometry("830x500")
        self.newsampleswindow.wm_title("New samples")

        frame0=Frame(self.newsampleswindow,borderwidth=0,  bg="white")
        frame0.pack()
        frame01=Frame(frame0,borderwidth=0,  bg="white")
        frame01.pack(side="left",fill=tk.BOTH,expand=1)
        tk.Label(frame01, text="Sample number", font=("Verdana", 10)).pack(fill=tk.BOTH,expand=1)
        tk.Label(frame01, text="Substrate type", font=("Verdana", 10)).pack(fill=tk.BOTH,expand=1)
        tk.Label(frame01, text="Device architecture", font=("Verdana", 10)).pack(fill=tk.BOTH,expand=1)
        tk.Label(frame01, text="bottomSiDBref", font=("Verdana", 10)).pack(fill=tk.BOTH,expand=1)
        tk.Label(frame01, text="Polarity", font=("Verdana", 10)).pack(fill=tk.BOTH,expand=1)
        tk.Label(frame01, text="#ofcells", font=("Verdana", 10)).pack(fill=tk.BOTH,expand=1)

        frame02=Frame(frame0,borderwidth=0,  bg="white")
        frame02.pack(side="left",fill=tk.BOTH,expand=1)
        #sample number
        self.samplenumber = tk.StringVar()
        self.entry1=Entry(frame02, textvariable=self.samplenumber,width=5)
        self.entry1.pack(fill=tk.BOTH,expand=1)
        self.samplenumber.set("")
        #substrate type
        self.subtypelist=[]
        result = self.theCursor.execute("SELECT substratetype FROM substtype")
        for row in result:
            self.subtypelist.append(row[0])
        if self.subtypelist==[]:
            self.subtypelist=[""]
        self.subtypelist=tuple(self.subtypelist)
        self.substChoice=StringVar()
        self.substChoice.set(self.subtypelist[0])
        self.dropMenuFramesubst = OptionMenu(frame02, self.substChoice, *self.subtypelist, command=())
        self.dropMenuFramesubst.pack(fill=tk.BOTH,expand=1)
        #device architecture
        self.cellarchitlist=["planar", "mesoporous","NULL"]
        self.cellarchitChoice=StringVar()
        self.cellarchitChoice.set(self.cellarchitlist[0])
        self.dropMenuFrame = OptionMenu(frame02, self.cellarchitChoice, *self.cellarchitlist, command=())
        self.dropMenuFrame.pack(fill=tk.BOTH,expand=1)
        #bottom si DB ref
        self.bottomDBref = tk.StringVar()
        self.entry2=Entry(frame02, textvariable=self.bottomDBref,width=5)
        self.entry2.pack(fill=tk.BOTH,expand=1)
        self.bottomDBref.set("")
        #polarity
        self.polaritylist=["nip", "pin","NULL"]
        self.polarityChoice=StringVar()
        self.polarityChoice.set(self.polaritylist[1])
        self.dropMenuFrame = OptionMenu(frame02, self.polarityChoice, *self.polaritylist, command=())
        self.dropMenuFrame.pack(fill=tk.BOTH,expand=1)
        ##ofcells
        self.numbofcell = tk.IntVar()
        self.entry2=Entry(frame02, textvariable=self.numbofcell,width=5)
        self.entry2.pack(fill=tk.BOTH,expand=1)
        self.numbofcell.set(1)
        
        frame06=Frame(frame0,borderwidth=0,  bg="white")
        frame06.pack(side="left",fill=tk.BOTH,expand=1)
        tk.Label(frame06, text=" ", font=("Verdana", 10)).pack(fill=tk.BOTH,expand=1)
        Button(frame06, text="Add",
               command = self.addnewSubstratetype).pack(fill=tk.BOTH,expand=1)
        tk.Label(frame06, text=" ", font=("Verdana", 10)).pack(fill=tk.BOTH,expand=1)
        tk.Label(frame06, text=" ", font=("Verdana", 10)).pack(fill=tk.BOTH,expand=1)
        tk.Label(frame06, text=" ", font=("Verdana", 10)).pack(fill=tk.BOTH,expand=1)
        tk.Label(frame06, text=" ", font=("Verdana", 10)).pack(fill=tk.BOTH,expand=1)

        
        frame03=Frame(frame0,borderwidth=0,  bg="white")
        frame03.pack(side="left",fill=tk.BOTH,expand=1)
        tk.Label(frame03, text="recombjct", font=("Verdana", 10)).pack(fill=tk.BOTH,expand=1)
        tk.Label(frame03, text="p-side", font=("Verdana", 10)).pack(fill=tk.BOTH,expand=1)
        tk.Label(frame03, text="n-side", font=("Verdana", 10)).pack(fill=tk.BOTH,expand=1)
        tk.Label(frame03, text="Absorber", font=("Verdana", 10)).pack(fill=tk.BOTH,expand=1)
        tk.Label(frame03, text="Method", font=("Verdana", 10)).pack(fill=tk.BOTH,expand=1)
        tk.Label(frame03, text="topelectrode", font=("Verdana", 10)).pack(fill=tk.BOTH,expand=1)
        
        
        frame04=Frame(frame0,borderwidth=0,  bg="white")
        frame04.pack(side="left",fill=tk.BOTH,expand=1)
        #recombjct
        self.recombjctlist=[]
        result = self.theCursor.execute("SELECT recombjctstack FROM recombjct")
        for row in result:
            self.recombjctlist.append(row[0])
        if self.recombjctlist==[]:
            self.recombjctlist=[""]
        self.recombjctlist=tuple(self.recombjctlist)
        self.recombjctChoice=StringVar()
        self.recombjctChoice.set(self.recombjctlist[0])
        self.dropMenuFramerecombjct = OptionMenu(frame04, self.recombjctChoice, *self.recombjctlist, command=())
        self.dropMenuFramerecombjct.pack(fill=tk.BOTH,expand=1)
        #p-side
        self.psidelist=[]
        result = self.theCursor.execute("SELECT contactstackP FROM Pcontact")
        for row in result:
            self.psidelist.append(row[0])
        if self.psidelist==[]:
            self.psidelist=[""]
        self.psidelist=tuple(self.psidelist)
        self.psideChoice=StringVar()
        self.psideChoice.set(self.psidelist[0])
        self.dropMenuFramepside = OptionMenu(frame04, self.psideChoice, *self.psidelist, command=())
        self.dropMenuFramepside.pack(fill=tk.BOTH,expand=1)
        #n-side
        self.nsidelist=[]
        result = self.theCursor.execute("SELECT contactstackN FROM Ncontact")
        for row in result:
            self.nsidelist.append(row[0])
        if self.nsidelist==[]:
            self.nsidelist=[""]
        self.nsidelist=tuple(self.nsidelist)
        self.nsideChoice=StringVar()
        self.nsideChoice.set(self.nsidelist[0])
        self.dropMenuFramenside = OptionMenu(frame04, self.nsideChoice, *self.nsidelist, command=())
        self.dropMenuFramenside.pack(fill=tk.BOTH,expand=1)        
        #absorber
        self.absorberlist=[]
        result = self.theCursor.execute("SELECT absorbercomposition FROM PkAbsorber")
        for row in result:
            self.absorberlist.append(row[0])
        if self.absorberlist==[]:
            self.absorberlist=[""]
        self.absorberlist=tuple(self.absorberlist)
        self.absorberChoice=StringVar()
        self.absorberChoice.set(self.absorberlist[0])
        self.dropMenuFrameabsorber = OptionMenu(frame04, self.absorberChoice, *self.absorberlist, command=())
        self.dropMenuFrameabsorber.pack(fill=tk.BOTH,expand=1) 
        self.absorberMethodlist=[]
        result = self.theCursor.execute("SELECT absorberMethod FROM PkAbsorberMethod")
        for row in result:
            self.absorberMethodlist.append(row[0])
        if self.absorberMethodlist==[]:
            self.absorberMethodlist=[""]
        self.absorberMethodlist=tuple(self.absorberMethodlist)
        self.absorberMethodChoice=StringVar()
        self.absorberMethodChoice.set(self.absorberMethodlist[0])
        self.dropMenuFrameabsorberMethod = OptionMenu(frame04, self.absorberMethodChoice, *self.absorberMethodlist, command=())
        self.dropMenuFrameabsorberMethod.pack(fill=tk.BOTH,expand=1)
        #electrode
        self.electrodelist=[]
        result = self.theCursor.execute("SELECT electrodestack FROM electrode")
        for row in result:
            self.electrodelist.append(row[0])
        if self.electrodelist==[]:
            self.electrodelist=[""]
        self.electrodelist=tuple(self.electrodelist)
        self.electrodeChoice=StringVar()
        self.electrodeChoice.set(self.electrodelist[0])
        self.dropMenuFrameelectrode = OptionMenu(frame04, self.electrodeChoice, *self.electrodelist, command=())
        self.dropMenuFrameelectrode.pack(fill=tk.BOTH,expand=1) 
        

        frame05=Frame(frame0,borderwidth=0,  bg="white")
        frame05.pack(side="left",fill=tk.BOTH,expand=1)
        Button(frame05, text="Add",
               command = self.addnewrecombjct).pack(fill=tk.BOTH,expand=1)
        Button(frame05, text="Add",
               command = self.addnewPcontact).pack(fill=tk.BOTH,expand=1)
        Button(frame05, text="Add",
               command = self.addnewNcontact).pack(fill=tk.BOTH,expand=1)
        Button(frame05, text="Add",
               command = self.addnewabsorber).pack(fill=tk.BOTH,expand=1)
        Button(frame05, text="Add",
               command = self.addnewabsorberMethod).pack(fill=tk.BOTH,expand=1)
        Button(frame05, text="Add",
               command = self.addnewelectrode).pack(fill=tk.BOTH,expand=1)

        if self.topicChoice.get()=="triple":   
    
            frame07=Frame(frame0,borderwidth=0,  bg="white")
            frame07.pack(side="left",fill=tk.BOTH,expand=1)
            tk.Label(frame07, text="tripletop", font=("Verdana", 10)).pack(fill=tk.BOTH,expand=1)
            #p-side
            self.psidelisttop=[]
            result = self.theCursor.execute("SELECT contactstackP FROM Pcontact")
            for row in result:
                self.psidelisttop.append(row[0])
            if self.psidelisttop==[]:
                self.psidelisttop=[""]
            self.psidelisttop=tuple(self.psidelisttop)
            self.psidetopChoice=StringVar()
            self.psidetopChoice.set(self.psidelisttop[0])
            self.dropMenuFramepsidetop = OptionMenu(frame07, self.psidetopChoice, *self.psidelisttop, command=())
            self.dropMenuFramepsidetop.pack(fill=tk.BOTH,expand=1)
            #n-side
            self.nsidelisttop=[]
            result = self.theCursor.execute("SELECT contactstackN FROM Ncontact")
            for row in result:
                self.nsidelisttop.append(row[0])
            if self.nsidelisttop==[]:
                self.nsidelisttop=[""]
            self.nsidelisttop=tuple(self.nsidelisttop)
            self.nsidetopChoice=StringVar()
            self.nsidetopChoice.set(self.nsidelisttop[0])
            self.dropMenuFramensidetop = OptionMenu(frame07, self.nsidetopChoice, *self.nsidelisttop, command=())
            self.dropMenuFramensidetop.pack(fill=tk.BOTH,expand=1)        
            #absorber
            self.absorberlisttop=[]
            result = self.theCursor.execute("SELECT absorbercomposition FROM PkAbsorber")
            for row in result:
                self.absorberlisttop.append(row[0])
            if self.absorberlisttop==[]:
                self.absorberlisttop=[""]
            self.absorberlisttop=tuple(self.absorberlisttop)
            self.absorbertopChoice=StringVar()
            self.absorbertopChoice.set(self.absorberlisttop[0])
            self.dropMenuFrameabsorbertop = OptionMenu(frame07, self.absorbertopChoice, *self.absorberlisttop, command=())
            self.dropMenuFrameabsorbertop.pack(fill=tk.BOTH,expand=1) 
            self.absorberMethodlisttop=[]
            result = self.theCursor.execute("SELECT absorberMethod FROM PkAbsorberMethod")
            for row in result:
                self.absorberMethodlisttop.append(row[0])
            if self.absorberMethodlisttop==[]:
                self.absorberMethodlisttop=[""]
            self.absorberMethodlisttop=tuple(self.absorberMethodlisttop)
            self.absorberMethodtopChoice=StringVar()
            self.absorberMethodtopChoice.set(self.absorberMethodlisttop[0])
            self.dropMenuFrameabsorberMethodtop = OptionMenu(frame07, self.absorberMethodtopChoice, *self.absorberMethodlisttop, command=())
            self.dropMenuFrameabsorberMethodtop.pack(fill=tk.BOTH,expand=1) 
            #electrode
            self.electrodelisttop=[]
            result = self.theCursor.execute("SELECT electrodestack FROM electrode")
            for row in result:
                self.electrodelisttop.append(row[0])
            if self.electrodelisttop==[]:
                self.electrodelisttop=[""]
            self.electrodelisttop=tuple(self.electrodelisttop)
            self.electrodetopChoice=StringVar()
            self.electrodetopChoice.set(self.electrodelisttop[0])
            self.dropMenuFrameelectrodetop = OptionMenu(frame07, self.electrodetopChoice, *self.electrodelisttop, command=())
            self.dropMenuFrameelectrodetop.pack(fill=tk.BOTH,expand=1) 
            

        frame1=Frame(self.newsampleswindow,borderwidth=0,  bg="white")
        frame1.pack()
        tk.Label(frame1, text="comment", font=("Verdana", 10)).pack(side="left",fill=tk.BOTH,expand=1)
        self.commentsamples = tk.StringVar()
        self.entry1=Entry(frame1, textvariable=self.commentsamples,width=50)
        self.entry1.pack(side="left",fill=tk.BOTH,expand=1)
        self.commentsamples.set("")

        frame4=Frame(self.newsampleswindow,borderwidth=0,  bg="white")
        frame4.pack()
        Button(frame4, text="Add new sample",
               command = self.addnewsamplestolist).pack(side="left", fill=tk.BOTH,expand=1)
        Button(frame4, text="Delete selected sample",
               command = self.deletesamplesfromlist).pack(side="left", fill=tk.BOTH,expand=1)
        self.newsampleswindow.bind('<Return>', self.onclickenter)#allows to call the addsamples by just clicking the enter key (faster)
        
        
        frame2=Frame(self.newsampleswindow,borderwidth=0,  bg="white")
        frame2.pack(fill=tk.BOTH, expand=1)
        
        self.listboxsamples=Listbox(frame2,width=20, height=5, selectmode=tk.EXTENDED)
        self.listboxsamples.pack(side="left", fill=tk.BOTH, expand=1)
        scrollbar = tk.Scrollbar(frame2, orient="vertical")
        scrollbar.config(command=self.listboxsamples.yview)
        scrollbar.pack(side="right", fill="y")
        self.listboxsamples.config(yscrollcommand=scrollbar.set)

        
        frame3=Frame(self.newsampleswindow,borderwidth=0,  bg="white")
        frame3.pack()
        Button(frame3, text="Validate",
               command = self.validatesampleslist).pack(side="left", fill=tk.BOTH,expand=1)
        Button(frame3, text="Cancel",
               command = self.backtomain).pack(side="left", fill=tk.BOTH,expand=1)
    def onclickenter(self,a):
        self.addnewsamplestolist()
    def addnewrecombjct(self):
        self.newSubstwin = tk.Toplevel()
        center(self.newSubstwin)
        self.newSubstwin.wm_geometry("270x100")
        self.newSubstwin.wm_title("Newrecombjct")
        
        tk.Label(self.newSubstwin, text="No spaces and layers separated by '/'", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        self.newrecombjctname = tk.StringVar()
        self.entry1=Entry(self.newSubstwin, textvariable=self.newrecombjctname,width=30)
        self.entry1.pack(fill=tk.X,expand=1)
        Button(self.newSubstwin, text="Validate",
               command = self.addnewrecombjctValidate).pack(fill=tk.X,expand=0)
        
    def addnewrecombjctValidate(self):
        self.substChoice.set(self.newrecombjctname.get())
        self.dropMenuFramesubst['menu'].delete(0,'end')
        
        goodtogo=0
        try:
            self.db_conn.execute("INSERT INTO recombjct (recombjctstack) VALUES (?)",
                            (self.newsubstratetypename.get(),))
            self.db_conn.commit()
            goodtogo=1
        except sqlite3.OperationalError:
            print("name couldn't be added to recombjct")
        except sqlite3.IntegrityError:
            print("the newrecombjctname already exists...")
        
        if goodtogo:
            self.recombjctlist=[]
            result = self.theCursor.execute("SELECT recombjctstack FROM recombjct")
            for row in result:
                self.recombjctlist.append(row[0])
            self.recombjctlist=tuple(self.recombjctlist)
            for choice in self.recombjctlist:
                self.dropMenuFramerecombjct['menu'].add_command(label=choice, command=tk._setit(self.recombjctChoice, choice))
    
            self.newSubstwin.destroy()
    
    def addnewSubstratetype(self):
        self.newSubstwin = tk.Toplevel()
        center(self.newSubstwin)
        self.newSubstwin.wm_geometry("270x100")
        self.newSubstwin.wm_title("NewSubstrate")
        
        tk.Label(self.newSubstwin, text="No spaces and layers separated by '/'", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        self.newsubstratetypename = tk.StringVar()
        self.entry1=Entry(self.newSubstwin, textvariable=self.newsubstratetypename,width=30)
        self.entry1.pack(fill=tk.X,expand=1)
        Button(self.newSubstwin, text="Validate",
               command = self.addnewSubstValidate).pack(fill=tk.X,expand=0)
        
    def addnewSubstValidate(self):
        self.substChoice.set(self.newsubstratetypename.get())
        self.dropMenuFramesubst['menu'].delete(0,'end')
        
        goodtogo=0
        try:
            self.db_conn.execute("INSERT INTO substtype (substratetype) VALUES (?)",
                            (self.newsubstratetypename.get(),))
            self.db_conn.commit()
            goodtogo=1
        except sqlite3.OperationalError:
            print("name couldn't be added to substtype")
        except sqlite3.IntegrityError:
            print("the newsubstratetypename already exists...")
        
        if goodtogo:
            self.subtypelist=[]
            result = self.theCursor.execute("SELECT substratetype FROM substtype")
            for row in result:
                self.subtypelist.append(row[0])
            self.subtypelist=tuple(self.subtypelist)
            for choice in self.subtypelist:
                self.dropMenuFramesubst['menu'].add_command(label=choice, command=tk._setit(self.substChoice, choice))
    
            self.newSubstwin.destroy()
    
    def addnewPcontact(self):
        self.newPcontactwin = tk.Toplevel()
        center(self.newPcontactwin)
        self.newPcontactwin.wm_geometry("270x170")
        self.newPcontactwin.wm_title("NewPcontact")
        
        tk.Label(self.newPcontactwin, text="No spaces and layers separated by '/'", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        self.newPcontactname = tk.StringVar()
        self.entry1=Entry(self.newPcontactwin, textvariable=self.newPcontactname,width=30)
        self.entry1.pack(fill=tk.X,expand=1)
        Button(self.newPcontactwin, text="Validate",
               command = self.addnewPcontactValidate).pack(fill=tk.X,expand=0)
        
    def addnewPcontactValidate(self):
        self.psideChoice.set(self.newPcontactname.get())
        self.dropMenuFramepside['menu'].delete(0,'end')
        if self.topicChoice.get()=="triple":
            self.psidetopChoice.set(self.newPcontactname.get())
            self.dropMenuFramepsidetop['menu'].delete(0,'end')
    
        goodtogo=0
        try:
            self.db_conn.execute("INSERT INTO Pcontact (contactstackP) VALUES (?)",
                            (self.newPcontactname.get(),))
            self.db_conn.commit()
            goodtogo=1
        except sqlite3.OperationalError:
            print("name couldn't be added to Pcontact")
        except sqlite3.IntegrityError:
            print("the newPcontactname already exists...")
        
        if goodtogo:
            self.psidelist=[]
            if self.topicChoice.get()=="triple":
                self.psidelisttop=[]
            result = self.theCursor.execute("SELECT contactstackP FROM Pcontact")
            for row in result:
                self.psidelist.append(row[0])
                if self.topicChoice.get()=="triple":
                    self.psidelisttop.append(row[0])
            self.psidelist=tuple(self.psidelist)
            if self.topicChoice.get()=="triple":
                self.psidelisttop=tuple(self.psidelisttop)
            for choice in self.psidelist:
                self.dropMenuFramepside['menu'].add_command(label=choice, command=tk._setit(self.psideChoice, choice))
                if self.topicChoice.get()=="triple":
                    self.dropMenuFramepsidetop['menu'].add_command(label=choice, command=tk._setit(self.psidetopChoice, choice))
    
            self.newPcontactwin.destroy()

    def addnewNcontact(self):
        self.newNcontactwin = tk.Toplevel()
        center(self.newNcontactwin)
        self.newNcontactwin.wm_geometry("270x170")
        self.newNcontactwin.wm_title("NewNcontact")
        
        tk.Label(self.newNcontactwin, text="No spaces and layers separated by '/'", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        self.newNcontactname = tk.StringVar()
        self.entry1=Entry(self.newNcontactwin, textvariable=self.newNcontactname,width=30)
        self.entry1.pack(fill=tk.X,expand=1)
        Button(self.newNcontactwin, text="Validate",
               command = self.addnewNcontactValidate).pack(fill=tk.X,expand=0)
        
    def addnewNcontactValidate(self):
        self.nsideChoice.set(self.newNcontactname.get())
        self.dropMenuFramenside['menu'].delete(0,'end')
        if self.topicChoice.get()=="triple":
            self.nsidetopChoice.set(self.newNcontactname.get())
            self.dropMenuFramensidetop['menu'].delete(0,'end')
        
        goodtogo=0
        try:
            self.db_conn.execute("INSERT INTO Ncontact (contactstackN) VALUES (?)",
                            (self.newNcontactname.get(),))
            self.db_conn.commit()
            goodtogo=1
        except sqlite3.OperationalError:
            print("name couldn't be added to Ncontact")
        except sqlite3.IntegrityError:
            print("the newNcontactname already exists...")
        
        if goodtogo:
            self.nsidelist=[]
            if self.topicChoice.get()=="triple":
                self.nsidelisttop=[]
            result = self.theCursor.execute("SELECT contactstackN FROM Ncontact")
            for row in result:
                self.nsidelist.append(row[0])
                if self.topicChoice.get()=="triple":
                    self.nsidelisttop.append(row[0])
            self.nsidelist=tuple(self.nsidelist)
            if self.topicChoice.get()=="triple":
                self.nsidelisttop=tuple(self.nsidelisttop)
            for choice in self.nsidelist:
                self.dropMenuFramenside['menu'].add_command(label=choice, command=tk._setit(self.nsideChoice, choice))
                if self.topicChoice.get()=="triple":
                    self.dropMenuFramensidetop['menu'].add_command(label=choice, command=tk._setit(self.nsidetopChoice, choice))
    
            self.newNcontactwin.destroy()    
            
    def addnewabsorber(self):
        self.newabsorberwin = tk.Toplevel()
        center(self.newabsorberwin)
        self.newabsorberwin.wm_geometry("270x170")
        self.newabsorberwin.wm_title("Newabsorber")
        
        tk.Label(self.newabsorberwin, text="No spaces and layers separated by '/'", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        self.newabsorbername = tk.StringVar()
        self.entry1=Entry(self.newabsorberwin, textvariable=self.newabsorbername,width=30)
        self.entry1.pack(fill=tk.X,expand=1)
        Button(self.newabsorberwin, text="Validate",
               command = self.addnewabsorberValidate).pack(fill=tk.X,expand=0)
        
    def addnewabsorberValidate(self):
        self.absorberChoice.set(self.newabsorbername.get())
        self.dropMenuFrameabsorber['menu'].delete(0,'end')
        if self.topicChoice.get()=="triple":
            self.absorbertopChoice.set(self.newabsorbername.get())
            self.dropMenuFrameabsorbertop['menu'].delete(0,'end')
    
        goodtogo=0
        try:
            self.db_conn.execute("INSERT INTO PkAbsorber (absorbercomposition) VALUES (?)",
                            (self.newabsorbername.get(),))
            self.db_conn.commit()
            goodtogo=1
        except sqlite3.OperationalError:
            print("name couldn't be added to PkAbsorber")
        except sqlite3.IntegrityError:
            print("the absorbercomposition already exists...")
        
        if goodtogo:
            self.absorberlist=[]
            if self.topicChoice.get()=="triple":
                self.absorberlisttop=[]
            result = self.theCursor.execute("SELECT absorbercomposition FROM PkAbsorber")
            for row in result:
                self.absorberlist.append(row[0])
                if self.topicChoice.get()=="triple":
                    self.absorberlisttop.append(row[0])
            self.absorberlist=tuple(self.absorberlist)
            if self.topicChoice.get()=="triple":
                self.absorberlisttop=tuple(self.absorberlisttop)
            for choice in self.absorberlist:
                self.dropMenuFrameabsorber['menu'].add_command(label=choice, command=tk._setit(self.absorberChoice, choice))
                if self.topicChoice.get()=="triple":
                    self.dropMenuFrameabsorbertop['menu'].add_command(label=choice, command=tk._setit(self.absorbertopChoice, choice))
    
            self.newabsorberwin.destroy()  
            
    def addnewabsorberMethod(self):
        self.newabsorberMethodwin = tk.Toplevel()
        center(self.newabsorberMethodwin)
        self.newabsorberMethodwin.wm_geometry("270x170")
        self.newabsorberMethodwin.wm_title("NewabsorberMethod")
        
        self.newabsorberMethodname = tk.StringVar()
        self.entry1=Entry(self.newabsorberMethodwin, textvariable=self.newabsorberMethodname,width=30)
        self.entry1.pack(fill=tk.X,expand=1)
        Button(self.newabsorberMethodwin, text="Validate",
               command = self.addnewabsorberMethodValidate).pack(fill=tk.X,expand=0)
        
    def addnewabsorberMethodValidate(self):
        self.absorberMethodChoice.set(self.newabsorberMethodname.get())
        self.dropMenuFrameabsorberMethod['menu'].delete(0,'end')
        if self.topicChoice.get()=="triple":
            self.absorberMethodtopChoice.set(self.newabsorberMethodname.get())
            self.dropMenuFrameabsorberMethodtop['menu'].delete(0,'end')
    
        goodtogo=0
        try:
            self.db_conn.execute("INSERT INTO PkAbsorberMethod (absorberMethod) VALUES (?)",
                            (self.newabsorberMethodname.get(),))
            self.db_conn.commit()
            goodtogo=1
        except sqlite3.OperationalError:
            print("name couldn't be added to PkAbsorberMethod")
        except sqlite3.IntegrityError:
            print("the absorberMethod already exists...")
        
        if goodtogo:
            self.absorberMethodlist=[]
            if self.topicChoice.get()=="triple":
                self.absorberMethodlisttop=[]
            result = self.theCursor.execute("SELECT absorberMethod FROM PkAbsorberMethod")
            for row in result:
                self.absorberMethodlist.append(row[0])
                if self.topicChoice.get()=="triple":
                    self.absorberMethodlisttop.append(row[0])
            self.absorberMethodlist=tuple(self.absorberMethodlist)
            if self.topicChoice.get()=="triple":
                self.absorberMethodlisttop=tuple(self.absorberMethodlisttop)
            for choice in self.absorberMethodlist:
                self.dropMenuFrameabsorberMethod['menu'].add_command(label=choice, command=tk._setit(self.absorberMethodChoice, choice))
                if self.topicChoice.get()=="triple":
                    self.dropMenuFrameabsorberMethodtop['menu'].add_command(label=choice, command=tk._setit(self.absorberMethodtopChoice, choice))
    
            self.newabsorberMethodwin.destroy()  
            
            
    def addnewelectrode(self):
        self.newelectrodewin = tk.Toplevel()
        center(self.newelectrodewin)
        self.newelectrodewin.wm_geometry("270x170")
        self.newelectrodewin.wm_title("Newelectrode")
        
        tk.Label(self.newelectrodewin, text="No spaces and layers separated by '/'", font=("Verdana", 10)).pack(fill=tk.X,expand=1)
        self.newelectrodename = tk.StringVar()
        self.entry1=Entry(self.newelectrodewin, textvariable=self.newelectrodename,width=30)
        self.entry1.pack(fill=tk.X,expand=1)
        Button(self.newelectrodewin, text="Validate",
               command = self.addnewelectrodeValidate).pack(fill=tk.X,expand=0)
        
    def addnewelectrodeValidate(self):
        self.electrodeChoice.set(self.newelectrodename.get())
        self.dropMenuFrameelectrode['menu'].delete(0,'end')
        if self.topicChoice.get()=="triple":
            self.electrodetopChoice.set(self.newelectrodename.get())
            self.dropMenuFrameelectrodetop['menu'].delete(0,'end')
            
        goodtogo=0
#        try:
        self.db_conn.execute("INSERT INTO electrode (electrodestack) VALUES (?)",
                        (self.newelectrodename.get(),))
        self.db_conn.commit()
        goodtogo=1
#        except sqlite3.OperationalError:
#            print("name couldn't be added to electrode")
#        except sqlite3.IntegrityError:
#            print("the electrodestack already exists...")
        
        if goodtogo:
            self.electrodelist=[]
            if self.topicChoice.get()=="triple":
                self.electrodelisttop=[]
            result = self.theCursor.execute("SELECT electrodestack FROM electrode")
            for row in result:
                self.electrodelist.append(row[0])
                if self.topicChoice.get()=="triple":
                    self.electrodelisttop.append(row[0])
            self.electrodelist=tuple(self.electrodelist)
            if self.topicChoice.get()=="triple":
                self.electrodelisttop=tuple(self.electrodelisttop)
            for choice in self.electrodelist:
                self.dropMenuFrameelectrode['menu'].add_command(label=choice, command=tk._setit(self.electrodeChoice, choice))
                if self.topicChoice.get()=="triple":
                    self.dropMenuFrameelectrodetop['menu'].add_command(label=choice, command=tk._setit(self.electrodetopChoice, choice))
    
            self.newelectrodewin.destroy()
    
        
    def addnewsamplestolist(self):
        global newsampleslist, newsampleslistnames, newsampleslistforlistbox        
        
        if self.batchname.get()+'_'+self.samplenumber.get() not in newsampleslistnames:#check if sample name is unique
            if self.polarityChoice.get()=="nip":
                if self.topicChoice.get()=="triple":
                    newsampleslistforlistbox.append(self.cellarchitChoice.get()+'-'+self.batchname.get()+'_'+self.samplenumber.get()+'/'+self.substChoice.get()+'/'+self.recombjctChoice.get()+'/'+self.nsideChoice.get()+'/'+self.absorberChoice.get()+'/'+self.psideChoice.get()+'/'+self.electrodeChoice.get()+'/'+self.nsidetopChoice.get()+'/'+self.absorbertopChoice.get()+'/'+self.psidetopChoice.get()+'/'+self.electrodetopChoice.get())
                    newsampleslist.append([newsampleslistforlistbox[-1],
                                               self.batchname.get()+'_'+self.samplenumber.get(),self.substChoice.get(),self.cellarchitChoice.get(),self.polarityChoice.get(),self.psideChoice.get(),self.nsideChoice.get(),self.absorberChoice.get(),self.electrodeChoice.get(),self.commentsamples.get(),self.numbofcell.get(),self.bottomDBref.get(),self.recombjctChoice.get(),self.nsidetopChoice.get(),self.absorbertopChoice.get(),self.psidetopChoice.get(),self.electrodetopChoice.get(),self.absorberMethodChoice.get(),self.absorberMethodtopChoice.get()])
                else:
                    newsampleslistforlistbox.append(self.cellarchitChoice.get()+'-'+self.batchname.get()+'_'+self.samplenumber.get()+'/'+self.substChoice.get()+'/'+self.recombjctChoice.get()+'/'+self.nsideChoice.get()+'/'+self.absorberChoice.get()+'/'+self.psideChoice.get()+'/'+self.electrodeChoice.get())
                    newsampleslist.append([newsampleslistforlistbox[-1],
                                           self.batchname.get()+'_'+self.samplenumber.get(),self.substChoice.get(),self.cellarchitChoice.get(),self.polarityChoice.get(),self.psideChoice.get(),self.nsideChoice.get(),self.absorberChoice.get(),self.electrodeChoice.get(),self.commentsamples.get(),self.numbofcell.get(),self.bottomDBref.get(),self.recombjctChoice.get()],self.absorberMethodChoice.get())
                newsampleslistnames.append(self.batchname.get()+'_'+self.samplenumber.get())  
                self.listboxsamples.insert(tk.END, newsampleslistforlistbox[-1])
            else:
                if self.topicChoice.get()=="triple":
                    newsampleslistforlistbox.append(self.cellarchitChoice.get()+'-'+self.batchname.get()+'_'+self.samplenumber.get()+'/'+self.substChoice.get()+'/'+self.recombjctChoice.get()+'/'+self.psideChoice.get()+'/'+self.absorberChoice.get()+'/'+self.nsideChoice.get()+'/'+self.electrodeChoice.get()+'/'+self.psidetopChoice.get()+'/'+self.absorbertopChoice.get()+'/'+self.nsidetopChoice.get()+'/'+self.electrodetopChoice.get())
                    newsampleslist.append([newsampleslistforlistbox[-1],
                                           self.batchname.get()+'_'+self.samplenumber.get(),self.substChoice.get(),self.cellarchitChoice.get(),self.polarityChoice.get(),self.psideChoice.get(),self.nsideChoice.get(),self.absorberChoice.get(),self.electrodeChoice.get(),self.commentsamples.get(),self.numbofcell.get(),self.bottomDBref.get(),self.recombjctChoice.get(),self.nsidetopChoice.get(),self.absorbertopChoice.get(),self.psidetopChoice.get(),self.electrodetopChoice.get(),self.absorberMethodChoice.get(),self.absorberMethodtopChoice.get()])
                else:
                    newsampleslistforlistbox.append(self.cellarchitChoice.get()+'-'+self.batchname.get()+'_'+self.samplenumber.get()+'/'+self.substChoice.get()+'/'+self.recombjctChoice.get()+'/'+self.psideChoice.get()+'/'+self.absorberChoice.get()+'/'+self.nsideChoice.get()+'/'+self.electrodeChoice.get())
                    newsampleslist.append([newsampleslistforlistbox[-1],
                                           self.batchname.get()+'_'+self.samplenumber.get(),self.substChoice.get(),self.cellarchitChoice.get(),self.polarityChoice.get(),self.psideChoice.get(),self.nsideChoice.get(),self.absorberChoice.get(),self.electrodeChoice.get(),self.commentsamples.get(),self.numbofcell.get(),self.bottomDBref.get(),self.recombjctChoice.get(),self.absorberMethodChoice.get()])
                newsampleslistnames.append(self.batchname.get()+'_'+self.samplenumber.get())               
                self.listboxsamples.insert(tk.END, newsampleslistforlistbox[-1])
        else:
            print("sample name already exists")
            messagebox.showinfo("", "sample name already exists")
    
    def deletesamplesfromlist(self):
        global newsampleslist, newsampleslistnames, newsampleslistforlistbox
               
#        print(newsampleslistnames)
        
        selection = self.listboxsamples.curselection()
#        pos = 0
        for i in selection :
#            idx = int(i) - pos
            value=self.listboxsamples.get(i)
            ind = newsampleslistforlistbox.index(value)
            del(newsampleslistforlistbox[ind])
            del(newsampleslist[ind])
            del(newsampleslistnames[ind])
#            pos = pos + 1
        for index in selection[::-1]:
            self.listboxsamples.delete(index)
#        print(newsampleslistnames)
        
    def validatesampleslist(self):
        global newsampleslist, newsampleslistnames, newsampleslistforlistbox
#        print("samplelistvalidated")
        
        #pop up window: are you sure? cancel
        if messagebox.askokcancel("Validate?", "Are you sure?"):
#            print("validating")
            
            #batch_id
            self.theCursor.execute("SELECT id FROM batch WHERE batchname=?",(self.batchname.get(),))
            batch_id_exists = self.theCursor.fetchone()[0]
            
            for i in range(len(newsampleslist)):
                #search in DB for id => foreign keys
                if self.topicChoice.get()=="triple":
        #            Pcontact_id
                    self.theCursor.execute("SELECT id FROM Pcontact WHERE contactstackP=?",(newsampleslist[i][5],))
                    Pcontact_id_exists = self.theCursor.fetchone()[0]
                    self.theCursor.execute("SELECT id FROM Pcontact WHERE contactstackP=?",(newsampleslist[i][15],))
                    Pcontacttop_id_exists = self.theCursor.fetchone()[0]
        #            Ncontact_id
                    self.theCursor.execute("SELECT id FROM Ncontact WHERE contactstackN=?",(newsampleslist[i][6],))
                    Ncontact_id_exists = self.theCursor.fetchone()[0]
                    self.theCursor.execute("SELECT id FROM Ncontact WHERE contactstackN=?",(newsampleslist[i][13],))
                    Ncontacttop_id_exists = self.theCursor.fetchone()[0]
        #            PkAbsorber_id
                    self.theCursor.execute("SELECT id FROM PkAbsorber WHERE absorbercomposition=?",(newsampleslist[i][7],))
                    PkAbsorber_id_exists = self.theCursor.fetchone()[0]
                    self.theCursor.execute("SELECT id FROM PkAbsorber WHERE absorbercomposition=?",(newsampleslist[i][14],))
                    PkAbsorbertop_id_exists = self.theCursor.fetchone()[0]
        #            substtype_id
                    self.theCursor.execute("SELECT id FROM substtype WHERE substratetype=?",(newsampleslist[i][2],))
                    substtype_id_exists = self.theCursor.fetchone()[0]
        #            electrode_id
                    self.theCursor.execute("SELECT id FROM electrode WHERE electrodestack=?",(newsampleslist[i][8],))
                    electrode_id_exists = self.theCursor.fetchone()[0]
                    self.theCursor.execute("SELECT id FROM electrode WHERE electrodestack=?",(newsampleslist[i][16],))
                    electrodetop_id_exists = self.theCursor.fetchone()[0]
        #            recombjct_id
                    self.theCursor.execute("SELECT id FROM recombjct WHERE recombjctstack=?",(newsampleslist[i][12],))
                    recombjct_id_exists = self.theCursor.fetchone()[0]
        #           absorberMethod_id
                    self.theCursor.execute("SELECT id FROM PkAbsorberMethod WHERE absorberMethod=?",(newsampleslist[i][17],))
                    absorberMethod_id = self.theCursor.fetchone()[0]
                    self.theCursor.execute("SELECT id FROM PkAbsorberMethod WHERE absorberMethod=?",(newsampleslist[i][18],))
                    absorberMethodtop_id = self.theCursor.fetchone()[0]
                    
                    if newsampleslist[i][4]=='nip':
                        topstack=newsampleslist[i][13] +'/'+ newsampleslist[i][14] +'/'+ newsampleslist[i][15] +'/'+ newsampleslist[i][16]
                    else:
                        topstack=newsampleslist[i][15] +'/'+ newsampleslist[i][14] +'/'+ newsampleslist[i][13] +'/'+ newsampleslist[i][16]
                    
                    try:
                        self.theCursor.execute("INSERT or REPLACE INTO tripletop (topstack,Pcontact_id,Ncontact_id,PkAbsorber_id,electrode_id,PkAbsorberMethod_id) VALUES (?,?,?,?,?,?)",
                                        (topstack, Pcontacttop_id_exists, Ncontacttop_id_exists, PkAbsorbertop_id_exists, electrodetop_id_exists, absorberMethodtop_id))
#                        self.theCursor.commit()
                        tripletop_id_exists =self.theCursor.lastrowid
                    except sqlite3.OperationalError:
                        print("data couldn't be added to tripletop")
                    
                    try:
                        self.db_conn.execute("INSERT INTO samples (samplename,samplefullstack,bottomCellDBRef,recombjct_id,tripletop_id,cellarchitecture,polarity,commentsamples,Pcontact_id,Ncontact_id,PkAbsorber_id,substtype_id,electrode_id,batch_id,PkAbsorberMethod_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                        (newsampleslistnames[i],newsampleslist[i][0],newsampleslist[i][11],recombjct_id_exists,tripletop_id_exists,newsampleslist[i][3],newsampleslist[i][4],newsampleslist[i][9],
                                         Pcontact_id_exists,Ncontact_id_exists,PkAbsorber_id_exists,substtype_id_exists,electrode_id_exists,batch_id_exists,absorberMethod_id))
                        self.db_conn.commit()
                    except sqlite3.OperationalError:
                        print("data couldn't be added to samples")
                    except sqlite3.IntegrityError:
                        print("the samplename already exists...")
                else:
        #            Pcontact_id
                    self.theCursor.execute("SELECT id FROM Pcontact WHERE contactstackP=?",(newsampleslist[i][5],))
                    Pcontact_id_exists = self.theCursor.fetchone()[0]
        #            Ncontact_id
                    self.theCursor.execute("SELECT id FROM Ncontact WHERE contactstackN=?",(newsampleslist[i][6],))
                    Ncontact_id_exists = self.theCursor.fetchone()[0]
        #            PkAbsorber_id
                    self.theCursor.execute("SELECT id FROM PkAbsorber WHERE absorbercomposition=?",(newsampleslist[i][7],))
                    PkAbsorber_id_exists = self.theCursor.fetchone()[0]
        #            substtype_id
                    self.theCursor.execute("SELECT id FROM substtype WHERE substratetype=?",(newsampleslist[i][2],))
                    substtype_id_exists = self.theCursor.fetchone()[0]
        #            electrode_id
                    self.theCursor.execute("SELECT id FROM electrode WHERE electrodestack=?",(newsampleslist[i][8],))
                    electrode_id_exists = self.theCursor.fetchone()[0]
        #            recombjct_id
                    self.theCursor.execute("SELECT id FROM recombjct WHERE recombjctstack=?",(newsampleslist[i][12],))
                    recombjct_id_exists = self.theCursor.fetchone()[0]    
        #           absorberMethod_id
                    self.theCursor.execute("SELECT id FROM PkAbsorberMethod WHERE absorberMethod=?",(newsampleslist[i][13],))
                    absorberMethod_id = self.theCursor.fetchone()[0]
                    
                    try:
                        self.db_conn.execute("INSERT INTO samples (samplename,samplefullstack,bottomCellDBRef,recombjct_id,cellarchitecture,polarity,commentsamples,Pcontact_id,Ncontact_id,PkAbsorber_id,substtype_id,electrode_id,batch_id,PkAbsorberMethod_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                        (newsampleslistnames[i],newsampleslist[i][0],newsampleslist[i][11],recombjct_id_exists,newsampleslist[i][3],newsampleslist[i][4],newsampleslist[i][9],
                                         Pcontact_id_exists,Ncontact_id_exists,PkAbsorber_id_exists,substtype_id_exists,electrode_id_exists,batch_id_exists,absorberMethod_id))
                        self.db_conn.commit()
                    except sqlite3.OperationalError:
                        print("data couldn't be added to samples")
                    except sqlite3.IntegrityError:
                        print("the samplename already exists...")
            
            #create the cells
            for i in range(len(newsampleslist)):
                self.theCursor.execute("SELECT id FROM samples WHERE samplename=?",(newsampleslist[i][1],))
                sample_id_exists = self.theCursor.fetchone()[0]
                if newsampleslist[i][10]==1:
                    self.db_conn.execute("INSERT INTO cells (cellname, samples_id, batch_id) VALUES (?,?,?)",('SingleCell',sample_id_exists,batch_id_exists))
                else:
                    cellpossiblename=["A","B","C","D","E"]
                    for j in range(newsampleslist[i][10]):
                        self.db_conn.execute("INSERT INTO cells (cellname, samples_id, batch_id) VALUES (?,?,?)",(cellpossiblename[j],sample_id_exists,batch_id_exists))
                
            self.db_conn.commit()
            #close window and back to main first window            
            print("samples inserted")
            self.backtomain()
            self.master.destroy()
            
            
        else:
            print("cancel")      

#%%############end samples###########################
        



        
###############################################################################        
if __name__ == '__main__':
    
    app = DBapp()
    app.mainloop()
