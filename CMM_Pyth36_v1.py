#! python3

import os

import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import Entry, Button, Toplevel, Frame, messagebox
from tkinter import filedialog
from pathlib import Path
import webbrowser
import csv
import shutil

"""ToDoList
- 


"""

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

def callCMM():
    webbrowser.open_new(r"https://jeancattin.shinyapps.io/Celltester_SpectrumSimulator/")
###############################################################################             
    
class CMM(Toplevel):

    def __init__(self, *args, **kwargs):
        
        Toplevel.__init__(self, *args, **kwargs)
        Toplevel.wm_title(self, "CMM")
        Toplevel.config(self,background="white")
        self.wm_geometry("400x205")
        #self.wm_resizable(False,True)
        center(self)
        self.initUI()

    def initUI(self):
        self.master.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.canvas0 = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.superframe=Frame(self.canvas0,background="#ffffff")
        self.canvas0.pack(side="left", fill="both", expand=True)
        
        label = tk.Label(self.canvas0, text="CMM DATA Preparation and Analysis", font=LARGE_FONT, bg="black",fg="white")
        label.pack(fill=tk.X,expand=0)
        
        #link to the spectrum preparation webpage made by Jean Cattin and Olivier Dupre in shiny
        frame1=Frame(self.canvas0,borderwidth=0,  bg="red")
        frame1.pack(fill=tk.BOTH,expand=0)
        
        CMMspectrawithR = Button(frame1, text='Go to Shiny Website for CMM-spectra', command = callCMM)
        CMMspectrawithR.pack()
        
        frame1to2=Frame(self.canvas0,borderwidth=0,  bg="blue")
        frame1to2.pack(fill=tk.X,expand=0)
        label = tk.Label(frame1to2, text="  ", bg="black",fg="white")
        label.pack(fill=tk.X,expand=0)
        #preparation of the sweep config
        frame2=Frame(self.canvas0,borderwidth=0,  bg="white")
        frame2.pack(fill=tk.X,expand=0)
        
        frame21=Frame(frame2,borderwidth=0,  bg="white")
        frame21.pack(fill=tk.X,expand=1)
        #Vstart 1.9
        self.Vstart = tk.DoubleVar()
        tk.Label(frame21, text="Vstart_For", bg="white").pack(side=tk.LEFT,fill=tk.X,expand=1)
        Entry(frame21, textvariable=self.Vstart,width=5).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.Vstart.set(-0.3)
        #Vend -0.3
        self.Vend = tk.DoubleVar()
        tk.Label(frame21, text="Vend_For", bg="white").pack(side=tk.LEFT,fill=tk.X,expand=1)
        Entry(frame21, textvariable=self.Vend,width=5).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.Vend.set(1.9)
        #number of points 100
        self.NumbPts = tk.DoubleVar()
        tk.Label(frame21, text="NumbPts", bg="white").pack(side=tk.LEFT,fill=tk.X,expand=1)
        Entry(frame21, textvariable=self.NumbPts,width=5).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.NumbPts.set(100)
        
        frame22=Frame(frame2,borderwidth=0,  bg="white")
        frame22.pack(fill=tk.X,expand=1)
        #delay s 0.1
        self.delay = tk.DoubleVar()
        tk.Label(frame22, text="delay", bg="white").pack(side=tk.LEFT,fill=tk.X,expand=1)
        Entry(frame22, textvariable=self.delay,width=5).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.delay.set(0.1)
        #integ time s 0.1
        self.integtime = tk.DoubleVar()
        tk.Label(frame22, text="integtime", bg="white").pack(side=tk.LEFT,fill=tk.X,expand=1)
        Entry(frame22, textvariable=self.integtime,width=5).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.integtime.set(0.1)
        #Vstep 0.02
        self.Vstep = tk.DoubleVar()
        tk.Label(frame22, text="Vstep", bg="white").pack(side=tk.LEFT,fill=tk.X,expand=1)
        Entry(frame22, textvariable=self.Vstep,width=5).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.Vstep.set(0.02)
        
        frame23=Frame(frame2,borderwidth=0,  bg="white")
        frame23.pack(side=tk.LEFT,fill=tk.X,expand=1)
        exportConfig = Button(frame23, text='Export Config', command = self.prepareConfigFiles)#when click export, should ask to load the spectra, and get the names, resave duplicates with _rev and save configsourcemter with same names
        exportConfig.pack()
    
        frame2to3=Frame(self.canvas0,borderwidth=0,  bg="blue")
        frame2to3.pack(fill=tk.X,expand=0)
        label = tk.Label(frame2to3, text="  ", bg="black",fg="white")
        label.pack(fill=tk.X,expand=0)
        #data analysis
        frame3=Frame(self.canvas0,borderwidth=0,  bg="red")
        frame3.pack(fill=tk.X,expand=0)
        CMMspectrawithR = Button(frame3, text='Analyze cmm spectral variation results', command = self.AnalyzeCMMspectralvar)
        CMMspectrawithR.pack()
        
        frame4to=Frame(self.canvas0,borderwidth=0,  bg="blue")
        frame4to.pack(fill=tk.BOTH,expand=1)
        label = tk.Label(frame4to, text="  ", bg="black",fg="white")
        label.pack(fill=tk.BOTH,expand=1)
    
    def on_closing(self):
        
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
            self.master.deiconify()    
        
    def prepareConfigFiles(self):
            
        #load spectra
        file_path =filedialog.askopenfilenames(title="Please select the ConfigLamps files")

        directory=str(Path(file_path[0]).parent)
        os.chdir(directory)#set directory to the ConfigLamps

        filenamelistfor=[]
        filenamelistrev=[]
        #duplicate the files and add _rev
        for i in range(len(file_path)):
            filename=os.path.split(file_path[i])[-1].split(".")[0]
            newpath=directory+'/' + filename+'_rev.txt'
            shutil.copy(file_path[i], newpath)
            filenamelistfor.append(filename)
            filenamelistrev.append(filename+'_rev')
            
        
        #export .par files with configsourcemeter
        
        parfileRev=["%Config sourceter\n",
                 "source/measure:	voltage/current dynamique\n",
                 "Vmax compliance [V]:\t3\n",
                 "Imax compliance [A]:\t1\n",
                 "V source range [V]:\t6 V\n",
                 "I sense range:\t1 A\n",
                 "I source range:\tauto\n",
                 "V sense range [V]:\tauto\n",
                 "start [V or A]:\t"+str(self.Vend.get())+"\n",
                 "stop  [V or A]:\t"+str(self.Vstart.get())+"\n",
                 "Number of points:\t"+str(int(self.NumbPts.get()))+"\n",
                 "delay [s]:\t"+str(self.delay.get())+"\n",
                 "Integration time [s]:\t"+str(self.integtime.get())+"\n",
                 "Vstep:\t"+str(self.Vstep.get())+"\n",
                 "Istep:\t3.000000E-2\n"
                 ]
        parfileFor=["%Config sourceter\n",
                 "source/measure:	voltage/current dynamique\n",
                 "Vmax compliance [V]:\t3\n",
                 "Imax compliance [A]:\t1\n",
                 "V source range [V]:\t6 V\n",
                 "I sense range:\t1 A\n",
                 "I source range:\tauto\n",
                 "V sense range [V]:\tauto\n",
                 "start [V or A]:\t"+str(self.Vstart.get())+"\n",
                 "stop  [V or A]:\t"+str(self.Vend.get())+"\n",
                 "Number of points:\t"+str(int(self.NumbPts.get()))+"\n",
                 "delay [s]:\t"+str(self.delay.get())+"\n",
                 "Integration time [s]:\t"+str(self.integtime.get())+"\n",
                 "Vstep:\t"+str(self.Vstep.get())+"\n",
                 "Istep:\t3.000000E-2\n"
                 ]
        
        for name in filenamelistfor:
            file = open(name+'.par','w')
            file.writelines("%s" % item for item in parfileFor)
            file.close()
        for name in filenamelistrev:
            file = open(name+'.par','w')
            file.writelines("%s" % item for item in parfileRev)
            file.close()
        
        
    def AnalyzeCMMspectralvar(self):
        
        file_path =filedialog.askopenfilenames(title="Please select the cmm summary files")
        directory = str(Path(file_path[0]).parent.parent)+'\\resultFilesCMM'
        if not os.path.exists(directory):
            os.makedirs(directory)
            os.chdir(directory)
        else :
            os.chdir(directory)
    
        for pathtoread in file_path:
            name=os.path.split(pathtoread)[-1].split(".")[0] #sample name is the file name
            
            with open(pathtoread) as f:
                reader = csv.reader(f, delimiter="\t")
                d = list(reader)
                
            VocFor=[]
            VocRev=[]
            JscFor=[]
            JscRev=[]
            FFFor=[]
            FFRev=[]
            PmppFor=[]
            PmppRev=[]
            VmppFor=[]
            VmppRev=[]
            JmppFor=[]
            JmppRev=[]
            RocFor=[]
            RocRev=[]
            RscFor=[]
            RscRev=[]
            illumination=[]
            
            for i in range(1,len(d)): #we suppose here that the cell was scanned in both directions (forward and reverse) and that both data will be found for all illumination settings
                if '_rev' in d[i][2]:
                    VocRev.append(float(d[i][3]))
                    JscRev.append(float(d[i][4]))
                    FFRev.append(float(d[i][5]))
                    PmppRev.append(float(d[i][6]))
                    RocRev.append(float(d[i][7]))
                    RscRev.append(float(d[i][8]))
                    VmppRev.append(float(d[i][9]))
                    JmppRev.append(float(d[i][10]))
                else:
                    illumination.append(d[i][2])
                    VocFor.append(float(d[i][3]))
                    JscFor.append(float(d[i][4]))
                    FFFor.append(float(d[i][5]))
                    PmppFor.append(float(d[i][6]))
                    RocFor.append(float(d[i][7]))
                    RscFor.append(float(d[i][8]))
                    VmppFor.append(float(d[i][9]))
                    JmppFor.append(float(d[i][10]))
            
            txtfile=["illumination"+'\t'+"VocFor"+'\t'+"VocRev"+'\t'+"JscFor"+'\t'+"JscRev"+'\t'+"FFFor"+'\t'+"FFRev"+'\t'+"PmppFor"+'\t'+"PmppRev"+'\t'+"RocFor"+'\t'+"RscRev"+'\t'+"VmppFor"+'\t'+"VmppRev"+'\t'+"JmppFor"+'\t'+"JmppRev"+'\n']
            for i in range(len(illumination)):
                txtfile.append(illumination[i]+'\t'+str(VocFor[i])+'\t'+str(VocRev[i])+'\t'+str(JscFor[i])+'\t'+str(JscRev[i])+'\t'+str(FFFor[i])+'\t'+str(FFRev[i])+'\t'+str(PmppFor[i])+'\t'+str(PmppRev[i])+'\t'+str(RocFor[i])+'\t'+str(RscRev[i])+'\t'+str(VmppFor[i])+'\t'+str(VmppRev[i])+'\t'+str(JmppFor[i])+'\t'+str(JmppRev[i])+'\n')
            file = open(name+'_FR.txt','w')
            file.writelines("%s" % item for item in txtfile)
            file.close()
             
            fig = plt.figure(figsize=(10, 12))
            Vocsubfig=fig.add_subplot(421)
            Jscsubfig=fig.add_subplot(422)
            FFsubfig=fig.add_subplot(423)
            Effsubfig=fig.add_subplot(424)
            Rocsubfig=fig.add_subplot(425)
            Rscsubfig=fig.add_subplot(426)
            Vmppsubfig=fig.add_subplot(427)
            Jmppsubfig=fig.add_subplot(428)
            
            Vocsubfig.set_ylabel('Voc (mV)')
            Vocsubfig.plot(illumination,VocFor,'ro')
            Vocsubfig.plot(illumination,VocRev,'bo')
            Jscsubfig.set_ylabel('Jsc (mA/cm2)')
            Jscsubfig.plot(illumination,JscFor,'ro')
            Jscsubfig.plot(illumination,JscRev,'bo')
            FFsubfig.set_ylabel('FF (%)')
            FFsubfig.plot(illumination,FFFor,'ro')
            FFsubfig.plot(illumination,FFRev,'bo')
            Effsubfig.set_ylabel('Eff (%)')
            Effsubfig.plot(illumination,PmppFor,'ro')
            Effsubfig.plot(illumination,PmppRev,'bo')
            Rocsubfig.set_ylabel('Roc ()')
            Rocsubfig.plot(illumination,RocFor,'ro')
            Rocsubfig.plot(illumination,RocRev,'bo')
            Rscsubfig.set_ylabel('Rsc ()')
            Rscsubfig.plot(illumination,RscFor,'ro')
            Rscsubfig.plot(illumination,RscRev,'bo')
            Vmppsubfig.set_ylabel('Vmpp (mV)')
            Vmppsubfig.plot(illumination,VmppFor,'ro')
            Vmppsubfig.plot(illumination,VmppRev,'bo')
            Jmppsubfig.set_ylabel('Jmpp (mA/cm2)')
            Jmppsubfig.plot(illumination,JmppFor,'ro')
            Jmppsubfig.plot(illumination,JmppRev,'bo')
            
            Vocsubfig.annotate(name+" - red=Forward; blue=Reverse", xy=(0.6,1.08), xycoords='axes fraction', fontsize=12,
                                                horizontalalignment='left', verticalalignment='bottom')
            
            plt.savefig(name+".png", dpi=300, transparent=False) 
            
            plt.close()
    
        
        
###############################################################################        
if __name__ == '__main__':
    app = CMM()
    app.mainloop()


