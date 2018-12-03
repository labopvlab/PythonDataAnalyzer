#! python3

"""

based on transfer matrix python package tmm, written by Steven Byrnes, http://sjbyrnes.com
main code to generate the matrices and calculate the currents written by Gabriel Christmann
readaptation and completion by J.Werner, to tkinter GUI, november 2017

"""

"""
still to be added:
    - textu
    - generation profile in device
    - refractive index in device for specific wavelength
    - E field in device
    - modifiable IQE
    
- when simulation is done, opens a toplevel window with the plot, with toolbar to rescale and save differently


"""
#%%
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as plt
from PIL import ImageTk
import PIL.Image
import tkinter as tk
from tkinter import ttk, Entry,messagebox, Button, Checkbutton, IntVar, Toplevel, OptionMenu, Frame, StringVar, Scrollbar, Listbox
from tkinter import filedialog
import numpy as np
from tkinter import *
import copy
import csv
import tmm.tmm_core as tm
import pickle


admittance0=2.6544E-3


#%%
def eta(index,imaginary_angle,TEorTM):
    res=index*np.cos(imaginary_angle)
    if(TEorTM==0):
        return admittance0*(np.abs(res.real)-1j*np.abs(res.imag))
    else:
        return admittance0*index*index/(np.abs(res.real)-1j*np.abs(res.imag))

def interp2w(value,abscis,ordo):
    return np.interp(value,abscis,ordo)   

def getgenspec(spectrgen,EQE):
    retval=[]
    for ii,wl in enumerate(EQE[0]):
        retval.append(EQE[1][ii]*interp2w(wl,spectrgen[0],spectrgen[1]))
    return [EQE[0],retval]
 
def getcurrent(spectrgen,EQE):
    retval=0
    for ii,wl in enumerate(EQE[0]):
        retval+=EQE[1][ii]*interp2w(wl,spectrgen[0],spectrgen[1])
    return retval
        
def elta(index,imaginary_angle,dd,ll):
    res= index*np.cos(imaginary_angle)
    return 2*np.pi*dd*(np.abs(res.real)-1j*np.abs(res.imag))/ll

def importindex(filename):
    index=[[],[]]
    with open(filename, 'rt') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar="'")
        iterdata=iter(spamreader)
        next(iterdata)
        for row in iterdata:
            index[0].append(float(row[0]))
            index[1].append(float(row[1]))
    return index
def plotdata(graph1,*nextgraphs):
    plt.figure()
    plt.plot(graph1[0],graph1[1])
    for graph in nextgraphs:
        plt.plot(graph[0],graph[1])

def plotdatas(graph1,*nextgraphs):
    plt.figure()
    plt.scatter(graph1[0],graph1[1],s=80,marker='s',color='b')
    for graph in nextgraphs:
        plt.scatter(graph[0],graph[1],s=80,marker='^',color='k')

def niceplotdata(abscisse,ordonnee,graph1,*nextgraphs):
    plt.figure()
    plt.plot(graph1[0][0],graph1[0][1],label=graph1[1])
    for graph in nextgraphs:
        plt.plot(graph[0][0],graph[0][1],label=graph[1])
    plt.xlabel(abscisse)
    plt.ylabel(ordonnee)
    plt.legend(framealpha=0,fancybox=False)
    plt.tight_layout()

def nicescatdata(abscisse,ordonnee,graph1,*nextgraphs):
    plt.figure()
    plt.scatter(graph1[0][0],graph1[0][1],label=graph1[1],s=80,marker='s',color='b')
    for graph in nextgraphs:
        plt.scatter(graph[0][0],graph[0][1],label=graph[1],s=80,marker='^',color='k')
    plt.xlabel(abscisse)
    plt.ylabel(ordonnee)
    plt.legend(framealpha=0,fancybox=False)
    plt.tight_layout()

def writefile(name,xx,yy):
    with open(name, 'w') as myfile:
        text=''
        for n,x in enumerate(xx):
            text=text+str(x)+'\t'+str(yy[n])+'\n'
        myfile.write(text)
            
def scatdatas(graph1,*nextgraphs):
    plt.figure()
    plt.scatter(graph1[0],graph1[1],s=80,marker='s',color='b')
    for graph in nextgraphs:
        plt.scatter(graph[0],graph[1],s=80,marker='s',color='b')
    plt.tight_layout()
    
def importindex2(filename):
    index=[[],[],[],[]]
    if filename.split('.')[1]=="csv":
        with open(filename, 'rt') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar="'")
            iterdata=iter(spamreader)
            next(iterdata)
            for row in iterdata:
                index[0].append(float(row[0]))#wavelength
                index[1].append(float(row[1])+1j*float(row[2]))#complex notation n+ik
                index[2].append(float(row[1]))#n
                index[3].append(float(row[2]))#k
        return index
    elif item.split('.')[1]=="txt":
        filetoread = open(filename,"r")
        filerawdata = filetoread.readlines()
        for row in filerawdata:
            if row[0]!="#" and row!="\n":
                index[0].append(float(row.split("\t")[0]))#wavelength
                index[1].append(float(row.split("\t")[1])+1j*float(row.split("\t")[2]))#complex notation n+ik
                index[2].append(float(row.split("\t")[1]))#n
                index[3].append(float(row.split("\t")[2]))#k
        return index
    elif item.split('.')[1]=="nk":
        filetoread = open(filename,"r")
        filerawdata = filetoread.readlines()
        for row in filerawdata:
            if row[0]!="#" and row!="\n":
                try:
                    index[0].append(float(row.split("\t")[0]))#wavelength
                    index[1].append(float(row.split("\t")[1])+1j*float(row.split("\t")[2]))#complex notation n+ik
                    index[2].append(float(row.split("\t")[1]))#n
                    index[3].append(float(row.split("\t")[2]))#k
                except:
                    pass
        return index

def importAM(filename):
    index=[[],[]]
    with open(filename, 'rt') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar="'")
        for row in spamreader:
            index[0].append(float(row[0]))
            index[1].append(float(row[1]))
    return index

def importAM2(filename):
    index=[[],[]]
    with open(filename, 'rt') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar="'")
        iterdata=iter(spamreader)
        next(iterdata)
        for row in iterdata:
            index[0].append(float(row[0]))
            index[1].append(float(row[1]))
    return index

def plotall(structure, genspec, lay1,lay2):
    huss=structure.geninalllays(genspec,1,0,1,'s')
    print("Generation in perovskite: ",huss[lay1])
    print("Generation in Si: ",huss[lay2])
    spec1=structure.absspectruminlay(lay1,genspec[0],1,0,1,'s')
    spec2=structure.absspectruminlay(lay2,genspec[0],1,0,1,'s')
    spec3=structure.calculateRTrange(genspec[0],1,0,1,'s')
    plotdata(spec1,spec2,[spec3[0],1-np.asarray(spec3[1])-np.asarray(spec3[2])],[spec3[0],np.asarray(spec1[1])+np.asarray(spec2[1])])

def plotAllLayers(structure,genspec, actlay1,actlay2):
    huss=structure.geninalllays(genspec,1,0,1,'s')
    print("Generation in perovskite: ",huss[actlay1])
    print("Generation in Si: ",huss[actlay2])
    spec1=structure.absspectruminlay(actlay1,genspec[0],1,0,1,'s')
    spec2=structure.absspectruminlay(actlay2,genspec[0],1,0,1,'s')
    spec3=structure.calculateRTrange(genspec[0],1,0,1,'s')
    
    plt.figure()
    
    for item in range(structure.lengthstructure()):
        spec0=structure.absspectruminlay(item+1,genspec[0],1,0,1,'s')
        plt.plot(spec0[0],spec0[1])
    spec=[spec3[0],1-np.asarray(spec3[1])-np.asarray(spec3[2])]
    spec4=[spec3[0],np.asarray(spec1[1])+np.asarray(spec2[1])]
    plt.plot(spec[0],spec[1])
    plt.plot(spec4[0],spec4[1])
    plt.savefig("test.png", dpi=300, transparent=False) 

def plotAllLayersTriple(structure,genspec, actlay1,actlay2,actlay3):
    huss=structure.geninalllays(genspec,1,0,1,'s')
    print("Generation in top: ",huss[actlay1])
    print("Generation in middle: ",huss[actlay2])
    print("Generation in bottom: ",huss[actlay3])
    
    spectop=structure.absspectruminlay(actlay1,genspec[0],1,0,1,'s')
    specmid=structure.absspectruminlay(actlay2,genspec[0],1,0,1,'s')
    specbot=structure.absspectruminlay(actlay3,genspec[0],1,0,1,'s')
    specR=structure.calculateRTrange(genspec[0],1,0,1,'s')
    
    plt.figure()
    
    
    for item in range(structure.lengthstructure()):
        spec0=structure.absspectruminlay(item+1,genspec[0],1,0,1,'s')
        plt.plot(spec0[0],spec0[1])
    
    spec=[specR[0],1-np.asarray(specR[1])-np.asarray(specR[2])]
    spec4=[specR[0],np.asarray(spectop[1])+np.asarray(specmid[1])+np.asarray(specbot[1])]
    plt.plot(spec[0],spec[1])
    plt.plot(spec4[0],spec4[1])
    plt.savefig("test.png", dpi=300, transparent=False) 
    
class multilayer:
    """Class defining a multilayer structure by its name, its components"""
    def __init__(self,*layers):
        self.name=""
        self.structure=[]
        for layer in layers:
            self.structure.append(layer)
    def plotnprofile(self,wavelength):
        zpos=[]
        zn=[]
        pos=0
        for layer in self.structure:
            zpos.append(pos)
            pos+=layer.thickness
            zpos.append(pos)
            zn.append(layer.material.indexatWL(wavelength))
            zn.append(layer.material.indexatWL(wavelength))
        plt.plot(zpos,zn)
    
    def lengthstructure(self):
        return len(self.structure)

    def addlayer(self,layer):
        self.structure.append(layer)
        
    def addlayerinpos(self,position,layer):
        self.structure.insert(position,layer)
    
    def addbilayers(self,layer_1,layer_2,pairs):
        for uselessindex in range(pairs):
            self.structure.append(layer_1)
            self.structure.append(layer_2)
        
    def addDBR(self,material_1,material_2,wavelength,pairs):
        layer_1=layer(material_1,wavelength/(material_1.indexatWL(wavelength).real*4))
        layer_2=layer(material_2,wavelength/(material_2.indexatWL(wavelength).real*4))
        self.addbilayers(layer_1,layer_2,pairs)
        
    def updatematerial(self,material):
        for materials in self.structure:
            if(material.name==materials.name):
                materials=material
                
    def erasestructure(self):
        self.structure=[]

#    def createTM(self,incident_medium_n,incident_angle,wavelength,TEorTM):
#        transfer_matrix=ml.eye(2)*(1+0j)
#        ndlist=self.makendlist(wavelength)
#        for [n,d] in ndlist:
#            angleincurrentlayer=np.arcsin((1+0j)*incident_medium_n*np.sin(incident_angle*np.pi/180)/n)
#            etac=eta(n,angleincurrentlayer,TEorTM)
#            eltac=elta(n,angleincurrentlayer,d,wavelength)
#            intermediate_matrix=transfer_matrix
#            transfer_matrix=intermediate_matrix*np.matrix([[np.cos(eltac),1j*np.sin(eltac)/etac],[1j*np.sin(eltac)*etac,np.cos(eltac)]])
#        return transfer_matrix
    
    def makendlist(self,wavelength):
        ndlist=[]
        for layers in self.structure:
            ndlist.append([layers.material.indexatWL(wavelength),layers.thickness])
        return ndlist
            
#    def calculateRT(self,incident_medium_n,incident_angle,output_medium_n,wavelength,TEorTM):
#        angleinoutputmedium=np.arcsin((1+0j)*incident_medium_n*np.sin(incident_angle*np.pi/180)/output_medium_n)
#        etai=eta(incident_medium_n,incident_angle*np.pi/180,TEorTM)
#        etao=eta(output_medium_n,angleinoutputmedium,TEorTM)
#        transfer_matrix=self.createTM(incident_medium_n,incident_angle,wavelength,TEorTM)
#        [[bb],[cc]]=(transfer_matrix*np.matrix([[1],[etao]])).tolist()
#        return [np.absolute((etai*bb-cc)/(etai*bb+cc))**2,4*etai.real*etao.real/(np.absolute(etai*bb+cc)**2)]
    
    def calculatetmm(self,incident_medium_n,incident_angle,output_medium_n,wavelength,TEorTM):
        d_list=[np.inf]
        n_list=[incident_medium_n]
        for layers in self.structure:
            d_list.append(layers.thickness)
            n_list.append(layers.material.indexatWL(wavelength))
        d_list.append(np.inf)
        n_list.append(output_medium_n)
        return tm.coh_tmm(TEorTM, n_list, d_list, incident_angle*np.pi/180, wavelength)

    def calculatetmminc(self,incident_medium_n,incident_angle,output_medium_n,wavelength,TEorTM):
        d_list=[np.inf]
        n_list=[incident_medium_n]
        c_list=['i']
        for layers in self.structure:
            d_list.append(layers.thickness)
            n_list.append(layers.material.indexatWL(wavelength))
            #print(layers.material.indexatWL(wavelength))
#            print('huss')
            
            c_list.append(layers.coherence)
        d_list.append(np.inf)
        n_list.append(output_medium_n)
        c_list.append('i')
#        print(n_list)
#        print(d_list)
#        print(c_list)
        return tm.inc_tmm(TEorTM, n_list, d_list, c_list, incident_angle*np.pi/180, wavelength)

    def calculatetmmforwlrange(self,wlrange,incident_medium_n,incident_angle,output_medium_n,TEorTM):
        return [self.calculatetmminc(incident_medium_n,incident_angle,output_medium_n,wl,TEorTM) for wl in wlrange]
        
    def calculateRTrange(self,wlrange,incident_medium_n,incident_angle,output_medium_n,TEorTM):
        huss=self.calculatetmmforwlrange(wlrange,incident_medium_n,incident_angle,output_medium_n,TEorTM)
        RR=[]
        TT=[]
        for ii,transc in enumerate(huss):
            RR.append(transc['R'])
            TT.append(transc['T'])
        return [wlrange,RR,TT]
    
    def absinalllayers(self,wl,incident_medium_n,incident_angle,output_medium_n,TEorTM):
        return tm.inc_absorp_in_each_layer(self.calculatetmminc(incident_medium_n,incident_angle,output_medium_n,wl,TEorTM))

    def absspectruminlay(self,layer,wlrange,incident_medium_n,incident_angle,output_medium_n,TEorTM):
        absinlay=[]
        for wl in wlrange:
            absinlay.append(self.absinalllayers(wl,incident_medium_n,incident_angle,output_medium_n,TEorTM)[layer])
        return [wlrange,absinlay]
    
    def generationinlay(self,layer,generationspectrum,incident_medium_n,incident_angle,output_medium_n,TEorTM):
        geninlay=0
        for nn,wl in enumerate(generationspectrum[0][1:]):
            #print(wl-generationspectrum[0][nn])
            #geninlay+=self.absinalllayers(wl,incident_medium_n,incident_angle,output_medium_n,TEorTM)[layer]*generationspectrum[1][nn]*(wl-generationspectrum[1][nn-1])
            geninlay+=self.absinalllayers(wl,incident_medium_n,incident_angle,output_medium_n,TEorTM)[layer]*generationspectrum[1][nn+1]*(wl-generationspectrum[0][nn])
        return geninlay

    def geninalllays(self,generationspectrum,incident_medium_n,incident_angle,output_medium_n,TEorTM):
        gen=np.zeros(len(self.structure)+2)
        for nn,wl in enumerate(generationspectrum[0][1:]):
            #rint(np.array(self.absinalllayers(wl,incident_medium_n,incident_angle,output_medium_n,TEorTM)))
            gen+=np.array(self.absinalllayers(wl,incident_medium_n,incident_angle,output_medium_n,TEorTM))*generationspectrum[1][nn+1]*(wl-generationspectrum[0][nn])
        return gen
    
    def scanlayerthickness(self,layertoscan0,scanrange,generationspectrum,incident_medium_n,incident_angle,output_medium_n,TEorTM):
        layertoscan=layertoscan0-1
        retval=[scanrange]
        for ii in range(len(self.structure)+2):
            retval.append([])
        for thick in scanrange:
            self.structure[layertoscan].thickness=thick
            gen=self.geninalllays(generationspectrum,incident_medium_n,incident_angle,output_medium_n,TEorTM)
            for ii in range(len(self.structure)+2):
                retval[ii+1].append(gen[ii])
            print(thick)
        return retval

    def scanlayerthickness2D(self,layer1toscan0,layer2toscan0,scanrange1,scanrange2,generationspectrum,incident_medium_n,incident_angle,output_medium_n,TEorTM):
        layer1toscan=layer1toscan0-1
        layer2toscan=layer2toscan0-1
        
        DATA=[]
        
        for thick1 in scanrange1:
            self.structure[layer1toscan].thickness=thick1
            print(thick1)
            print("")
            retval=[scanrange2]
            for ii in range(len(self.structure)+2):
                retval.append([])
            for thick2 in scanrange2:
                self.structure[layer2toscan].thickness=thick2
                gen=self.geninalllays(generationspectrum,incident_medium_n,incident_angle,output_medium_n,TEorTM)
                for ii in range(len(self.structure)+2):
                    retval[ii+1].append(gen[ii])
                print(thick2)
            DATA.append([thick1,[list(x) for x in zip(*retval)]])
            print("")
        return DATA
            
    
    
    def getcurrentinlayerstextu(self,currentspectrum):
        r1TE=np.transpose(np.asarray([tm.inc_absorp_in_each_layer(self.calculatetmminc(1,54.74,1,x,'s')) for x in currentspectrum[0]]))
        r2TE=np.transpose(np.asarray([tm.inc_absorp_in_each_layer(self.calculatetmminc(1,15.79,1,x,'s')) for x in currentspectrum[0]]))
        r1TM=np.transpose(np.asarray([tm.inc_absorp_in_each_layer(self.calculatetmminc(1,54.74,1,x,'p')) for x in currentspectrum[0]]))
        r2TM=np.transpose(np.asarray([tm.inc_absorp_in_each_layer(self.calculatetmminc(1,15.79,1,x,'p')) for x in currentspectrum[0]]))
        listlayers=[]
        for ii,layer in enumerate(r1TE):
            layerTE=[]
            layerTM=[]
            for jj,wlpos in enumerate(layer):
                if(ii==0):
                    layerTE.append(wlpos*r2TE[ii][jj])
                    layerTM.append(r1TM[ii][jj]*r2TM[ii][jj])
                else:
                    layerTE.append(wlpos+r1TE[0][jj]*r2TE[ii][jj])
                    layerTM.append(r1TM[ii][jj]+r1TM[0][jj]*r2TM[ii][jj])
            listlayers.append([np.trapz(np.asarray(layerTE)*np.asarray(currentspectrum[1]),x=currentspectrum[0])/10,np.trapz(np.asarray(layerTM)*np.asarray(currentspectrum[1]),x=currentspectrum[0])/10])
            
        return listlayers
        
        
        
        
class layer:
    """Class defining a layer by its material and thickness"""
    def __init__(self,material,thickness,coherence):
        self.name=""
        self.material=material
        self.thickness=thickness
        self.coherence=coherence
        
class material:
    """Class defining a material by its name and refractive index"""
    def __init__(self,name,indextabl):
        
        self.name=name
        self.indextable=[sorted(indextabl[0]),[x for _,x in sorted(zip(indextabl[0],indextabl[1]))]]
        
    def indexatWL(self,wavelength):
        return np.interp(wavelength,self.indextable[0],[x.real for x in self.indextable[1]])+1j*np.interp(wavelength,self.indextable[0],[x.imag for x in self.indextable[1]])

#%%

LARGE_FONT= ("Verdana", 16)
SMALL_FONT= ("Verdana", 10)

stackDir			= os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'TMstacks')# cell stacks predifined with layer names and thicknesses
matDir			= os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'matdata')	# materials data
resDir        = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'results')
matPrefix		= 'nk_'		# materials data prefix
matHeader		= 1				# number of lines in header


#get list of stack names
stacklist=os.listdir(stackDir)
stackNameList=[]
for item in stacklist:
    stackNameList.append(item.split('.')[0])

matlist=os.listdir(matDir)
owd = os.getcwd()
os.chdir(matDir)
matnamelist=[]
material_list={}
material_list_dat={}
for item in matlist:
    if item.split('.')[1]=="csv":
        name=item.split('_')[1].split('.')[0]
        matnamelist.append(name)
        material_list[name]=material(name,importindex2(item))
        material_list_dat[name]=importindex2(item)
    elif item.split('.')[1]=="txt":
        if "interpolated" not in item:
            name=item.split('.')[0]
            matnamelist.append(name)
            material_list[name]=material(name,importindex2(item))
            material_list_dat[name]=importindex2(item)
    elif item.split('.')[1]=="nk":
        if "interpolated" not in item:
            name=item.split('.')[0]
            matnamelist.append("s_"+ name)
            material_list["s_"+ name]=material("s_"+ name,importindex2(item))
            material_list_dat["s_"+ name]=importindex2(item)
matnamelist.sort(key=lambda x: x.lower())
os.chdir(owd)
#with open('material_list.pk', 'wb') as fichier:
#    mon_pickler = pickle.Pickler(fichier)
#    mon_pickler.dump(material_list)

#with open('material_list.pk','rb') as fichier:
#    mon_depickler = pickle.Unpickler(fichier)
#    material_list=pickle.load(mon_depickler)

with open('material_list.pickle', 'wb') as fichier:
    pickle.dump(material_list,fichier,pickle.HIGHEST_PROTOCOL)

with open('material_list.pickle','rb') as fichier:
    material_list=pickle.load(fichier)

AM1p5Gc=importAM2(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'spectratxtfiles','AM1.5Gdf.csv'))

numberofLayer = 0

MatThickActList=[] #list of list with [Material, thickness, Active?, Incoherent?] info in order of stack

#%%

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
    

class PlotNKdat(Toplevel):

    def __init__(self, *args, **kwargs):
        
        Toplevel.__init__(self, *args, **kwargs)
        Toplevel.wm_title(self, "PlotNKdat")
        Toplevel.config(self,background="white")
        self.wm_geometry("580x350")
        center(self)
        self.initUI()


    def initUI(self):
        global matnamelist
#        print(matnamelist)
#        self.master.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.canvas0 = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.superframe=Frame(self.canvas0,background="#ffffff")
        self.canvas0.pack(side="left", fill="both", expand=True)
        
        label = tk.Label(self.canvas0, text="n&k data checking", font=LARGE_FONT, bg="black",fg="white")
        label.pack(fill=tk.X,expand=0)
        
        self.frame1=Frame(self.canvas0,borderwidth=0,  bg="white")
        self.frame1.pack(side="left", fill=tk.BOTH,expand=1)
        self.frame11=Frame(self.frame1,borderwidth=0,  bg="white")
        self.frame11.pack(side="left", fill=tk.BOTH,expand=1)
#        self.frame1.bind("<Configure>", self.onFrameConfigure)
        self.fig1 = plt.figure()
        canvas = FigureCanvasTkAgg(self.fig1, self.frame11)
        canvas.get_tk_widget().pack(fill=tk.BOTH,expand=1)
        self.nkgraph = plt.subplot2grid((1, 5), (0, 0), colspan=5)
#        self.nkgraph=plt.subplot2grid()
        self.toolbar = NavigationToolbar2TkAgg(canvas, self.frame11)
        self.toolbar.update()
        canvas._tkcanvas.pack(fill = tk.BOTH, expand = 1) 
        
        
        self.frame2=Frame(self.canvas0,borderwidth=0,  bg="white")
        self.frame2.pack(side="right", fill=tk.BOTH,expand=0)
        
        valores = StringVar()
        self.listboxsamples=Listbox(self.frame2,listvariable=valores, selectmode=tk.SINGLE,width=20, height=5)
        self.listboxsamples.bind('<<ListboxSelect>>', self.updateNkgraph)
        self.listboxsamples.pack(side="left", fill=tk.BOTH, expand=1)
        scrollbar = tk.Scrollbar(self.frame2, orient="vertical")
        scrollbar.config(command=self.listboxsamples.yview)
        scrollbar.pack(side="right", fill="y")
        self.listboxsamples.config(yscrollcommand=scrollbar.set)
        
        for item in matnamelist:
            self.listboxsamples.insert(tk.END,item)
        
    def on_closing(self):
        
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            plt.close()
            self.destroy()

    def updateNkgraph(self,a):
        global matnamelist, material_list_dat

        try:
            w=material_list_dat[matnamelist[self.listboxsamples.curselection()[0]]][0]
            n=material_list_dat[matnamelist[self.listboxsamples.curselection()[0]]][2]
            k=material_list_dat[matnamelist[self.listboxsamples.curselection()[0]]][3]
        except ValueError:
            print("valueerror")
            w=[]
            n=[]
            k=[]
        if len(w)==len(n) and len(w)==len(k):
            pass
        else:
            w=[]
            n=[]
            k=[]
        plt.close()
        self.frame11.destroy()
        self.frame11=Frame(self.frame1,borderwidth=0,  bg="white")
        self.frame11.pack(side="left", fill=tk.BOTH,expand=1)
        self.fig1 = plt.figure()
        canvas = FigureCanvasTkAgg(self.fig1, self.frame11)
        canvas.get_tk_widget().pack(fill=tk.BOTH,expand=1)
        self.nkgraph = plt.subplot2grid((1, 5), (0, 0), colspan=5)
        self.toolbar = NavigationToolbar2TkAgg(canvas, self.frame11)
        self.toolbar.update()
        canvas._tkcanvas.pack(fill = tk.BOTH, expand = 1) 
        
        self.nkgraph.set_xlabel("Wavelength (nm)")
        self.nkgraph.set_ylabel("n")
        self.nkgraph.plot(w,n,'r')
        self.nkgraph.tick_params(axis='y', labelcolor='r')
        
        self.nkgraph2 = self.nkgraph.twinx()
        
        self.nkgraph2.set_ylabel("k")
        self.nkgraph2.plot(w,k,'b')
        self.nkgraph2.tick_params(axis='y', labelcolor='b')
        
        self.fig1.tight_layout()
        plt.gcf().canvas.draw()
        

#%%

###############################################################################             
    
class TMSimApp(Toplevel):

    def __init__(self, *args, **kwargs):
        
        Toplevel.__init__(self, *args, **kwargs)
        Toplevel.wm_title(self, "TMSim")
        Toplevel.config(self,background="white")
        self.wm_geometry("390x500")
        #self.wm_resizable(False,True)
        center(self)
        self.initUI()

    def initUI(self):
        global stackNameList
        self.master.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        label = tk.Label(self, text="Transfer Matrix Optical Modeling", font=LARGE_FONT, bg="black",fg="white")
        label.pack(fill=tk.X,expand=0)

        
        frame2=Frame(self,borderwidth=0,  bg="white")
        frame2.pack(fill=tk.X,expand=0)
        tk.Label(frame2, text="StartWave",font=SMALL_FONT,  bg="white").pack(side=tk.LEFT,expand=1)
        self.StartWave = tk.DoubleVar()
        Entry(frame2, textvariable=self.StartWave,width=5).pack(side=tk.LEFT,expand=1)
        self.StartWave.set(320)
        tk.Label(frame2, text="EndWave",font=SMALL_FONT,  bg="white").pack(side=tk.LEFT,expand=1) 
        self.EndWave = tk.DoubleVar()
        Entry(frame2, textvariable=self.EndWave,width=5).pack(side=tk.LEFT,expand=1) 
        self.EndWave.set(1200)
        
#        self.frame3=Frame(self,borderwidth=0,  bg="white")
#        self.frame3.pack(fill=tk.X,expand=0)           
#        self.StackChoice=StringVar()
#        tk.Label(self.frame3, text=self.StackChoice.get(),font=SMALL_FONT,  bg="white").pack(side=tk.LEFT,expand=1)      
#        self.dropMenuStack = OptionMenu(self.frame3, self.StackChoice, *stackNameList, command=())
#        self.dropMenuStack.pack(side=tk.LEFT,expand=1) 
        self.LoadStack = Button(frame2, text="Load CellStack", command = self.loadstack)
        self.LoadStack.pack(side=tk.RIGHT,expand=1) 
        
        #tk.Label(self, text=" ",font=SMALL_FONT,  bg="white").grid(row=7,column=0)
        
        frame4=Frame(self,borderwidth=0,  bg="white")
        frame4.pack(fill=tk.X,expand=0) 
        self.SaveStack = Button(frame4, text="Save CellStack", command = self.savestack)
        self.SaveStack.pack(side=tk.LEFT,expand=1) 
        self.AddLayer = Button(frame4, text="Add Layer", command = self.AddLayer)
        self.AddLayer.pack(side=tk.LEFT,expand=1) 
        self.Reorder = Button(frame4, text="Reorder", command = self.reorder)
        self.Reorder.pack(side=tk.LEFT,expand=1)
        self.deletelayer = Button(frame4, text="DeleteLayer", command = self.deletelayer)
        self.deletelayer.pack(side=tk.LEFT,expand=1)
        self.checknk = Button(frame4, text="check n&k", command = PlotNKdat)
        self.checknk.pack(side=tk.LEFT,expand=1)
        
        
        frame5=Frame(self,borderwidth=0,  bg="white")
        frame5.pack(fill=tk.X,expand=0) 
        self.StartSim = Button(frame5, text="Start simulation",width=15, command = self.simulate)
        self.StartSim.pack(side=tk.LEFT,expand=1) 
             
        self.check1D = IntVar()
        Check1Dvar=Checkbutton(frame5,text="1D",variable=self.check1D, 
                           onvalue=1,offvalue=0,height=1, width=1, command = (),fg='black',background='white')
        Check1Dvar.pack(side=tk.LEFT,expand=1)
        self.check1D.set(0)
        
        self.check2D = IntVar()
        Check2Dvar=Checkbutton(frame5,text="2D",variable=self.check2D, 
                           onvalue=1,offvalue=0,height=1, width=1, command = (),fg='black',background='white')
        Check2Dvar.pack(side=tk.LEFT,expand=1)
        self.check2D.set(0)
        
        image = PIL.Image.open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'images',"soleil.jpg"))
        image=image.resize((50,50),PIL.Image.ANTIALIAS)
        sunpic=ImageTk.PhotoImage(image)
        sun_label = tk.Label(frame5, image=sunpic)
        sun_label.image=sunpic
        sun_label.pack(side=tk.LEFT,expand=1)
        
        self.Help = Button(frame5, text="Help/Info/Credits",width=15, command = self.Help)
        self.Help.pack(side=tk.RIGHT,expand=1) 
        
        
        
        
        self.canvas0 = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.frame6 = tk.Frame(self.canvas0, background="#ffffff")
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas0.yview)
        self.canvas0.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas0.pack(side="left", fill="both", expand=True)
        self.canvas0.create_window((4,4), window=self.frame6, anchor="nw", 
                                  tags="self.frame6")
        self.frame6.bind("<Configure>", self.onFrameConfigure)

        self.populate()
        
    def on_closing(self):
        
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
            self.master.deiconify()
        
    def onFrameConfigure(self, event):
        self.canvas0.configure(scrollregion=self.canvas0.bbox("all"))

    def populate(self):
        global numberofLayer
        global matnamelist
        global MatThickActList
        
        matlist=copy.deepcopy(MatThickActList)
        #print(matlist[0][0])
            
        for item in range(numberofLayer):
            label=tk.Label(self.frame6,text=item+1,fg='black',background='white')
            label.grid(row=item+1,column=0, columnspan=1) 

            #the material of the layer
            MatThickActList[item][0]=StringVar()
            MatThickActList[item][0].set(matlist[item][0]) # default choice
            
            w = ttk.Combobox(self.frame6, textvariable=MatThickActList[item][0], values=matnamelist)            
            w.grid(row=item+1, column=2, columnspan=4)
            
            #the thickness of the layer
            textinit = tk.IntVar()
            MatThickActList[item][1]=Entry(self.frame6,textvariable=textinit,width=6)
            textinit.set(matlist[item][1])
            MatThickActList[item][1].grid(row=item+1,column=6, columnspan=4)

            #active or not? active=photoactive
            MatThickActList[item][2] = IntVar()
            ActiveCheck=Checkbutton(self.frame6,text="active?",variable=MatThickActList[item][2], 
                               onvalue=1,offvalue=0,height=1, width=5, command = (),fg='black',background='white')
            ActiveCheck.grid(row=item+1,column=12, columnspan=2)
            MatThickActList[item][2].set(matlist[item][2])
            
            #coherent=unchecked or incoherent=checked
            MatThickActList[item][3] = IntVar()
            CoherCheck=Checkbutton(self.frame6,text="incoherent?",variable=MatThickActList[item][3], 
                               onvalue=1,offvalue=0,height=1, width=8, command = (),fg='black',background='white')
            CoherCheck.grid(row=item+1,column=15, columnspan=4)
            MatThickActList[item][3].set(matlist[item][3])
            
            
    def AddLayer(self):
        global numberofLayer
        global MatThickActList
        
        numberofLayer += 1
        
        MatThickActList.append(['Air',0,0,1]) #material,thickness,active,conherence (coherent=0;incoherent=1=checked)
        
        self.updatelist()
    
    
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
        global MatThickActList
        
        for i in range(len(MatThickActList)):
            if type(MatThickActList[i][0])!=str:
                MatThickActList[i][0]=MatThickActList[i][0].get()
            if type(MatThickActList[i][1])!=int:
                MatThickActList[i][1]=int(MatThickActList[i][1].get())
            if type(MatThickActList[i][2])!=int:
                MatThickActList[i][2]=int(MatThickActList[i][2].get())
            if type(MatThickActList[i][3])!=int:
                MatThickActList[i][3]=int(MatThickActList[i][3].get())
        
        
        self.listforordering=[]
        for i in range(len(MatThickActList)):
            self.listforordering.append(str(i)+"_"+MatThickActList[i][0])
        
        self.reorderwindow = tk.Tk()
        self.reorderwindow.wm_title("Drag&Drop to reorder")
        self.reorderwindow.geometry("250x200")
        center(self.reorderwindow)
        self.listbox = self.Drag_and_Drop_Listbox(self.reorderwindow)
        for name in self.listforordering:
          self.listbox.insert(tk.END, name)
          self.listbox.selection_set(0)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(self.listbox, orient="vertical")
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        printbut = tk.Button(self.reorderwindow, text="reorder",
                                    command = self.updateafterordering)
        printbut.pack()
        self.reorderwindow.mainloop()    
    
    def updateafterordering(self):
        global MatThickActList
        #reorder the MatThickActList according to the listbox defined order
        
        reorderedlist=list(self.listbox.get(0,tk.END))
        
        numreorderedlist=[]
        for item in reorderedlist:
            numreorderedlist.append(int(item.split('_')[0]))
        
        MatThickActList = [MatThickActList[i] for i in numreorderedlist]
        
        #update frame6 and close order window
        
        self.updatelist()
        self.reorderwindow.destroy()    
    
    def deletelayer(self):
        global MatThickActList
        
        self.deletewin=tk.Tk()
        self.deletewin.wm_title("Select 1 or more")
        self.deletewin.geometry("250x200")
        center(self.deletewin)
        self.lb=tk.Listbox(self.deletewin, selectmode=tk.MULTIPLE)
        
        for i in range(len(MatThickActList)):
            if type(MatThickActList[i][0])!=str:
                MatThickActList[i][0]=MatThickActList[i][0].get()
            if type(MatThickActList[i][1])!=int:
                MatThickActList[i][1]=int(MatThickActList[i][1].get())
            if type(MatThickActList[i][2])!=int:
                MatThickActList[i][2]=int(MatThickActList[i][2].get())
            if type(MatThickActList[i][3])!=int:
                MatThickActList[i][3]=int(MatThickActList[i][3].get())
        
        
        self.listfordelete=[]
        for i in range(len(MatThickActList)):
            self.listfordelete.append(str(i)+"_"+MatThickActList[i][0])
    
        for i in range(len(self.listfordelete)):
            self.lb.insert("end",self.listfordelete[i])
        self.lb.pack(side="top",fill="both",expand=True)
        scrollbar = tk.Scrollbar(self.lb, orient="vertical")
        scrollbar.config(command=self.lb.yview)
        scrollbar.pack(side="right", fill="y")
        self.lb.config(yscrollcommand=scrollbar.set)
        
        delbut = tk.Button(self.deletewin, text="delete", command = self.deletebut)
        delbut.pack()
    
    def deletebut(self):
        global MatThickActList
        global numberofLayer       
        
        selected = list(self.lb.curselection())
        
        MatThickActList=self.multi_delete(MatThickActList,selected)
        
        numberofLayer -= len(selected)
        
        self.updatelist()
        
        self.deletewin.destroy()
        
        
    def multi_delete(self, listorig, indiceslist):
        newlist=[]
        for i in range(len(listorig)):
            if i not in indiceslist:
                newlist.append(listorig[i])
        return newlist    
    
#    def selectMat(self,a):#create a pop-up window with a selectable list of materials in a listbox
#        print(a)
    
    def loadstack(self):
        global MatThickActList
        global numberofLayer
        
        owd = os.getcwd()
        
        os.chdir(stackDir)
        
        filepath =filedialog.askopenfilename(title="Please select the stack file", initialdir=stackDir)
        if filepath!='':
            try:
                filetoread=open(filepath,"r")
                filedata=filetoread.readlines()
                
                MatThickActList=[]
                i=0
                for item in filedata: 
                    MatThickActList.append([item[:-1].split("\t")[0],int(item[:-1].split("\t")[1]),int(item[:-1].split("\t")[2]),int(item[:-1].split("\t")[3])])
                    i+=1
                numberofLayer=len(MatThickActList)
                
                os.chdir(owd)
                
                self.updatelist()
            except:
                messagebox.showinfo("Import failed","Might not be the correct file?!...")
    
    
    def savestack(self):
        global MatThickActList
        global stackNameList
        
        for i in range(len(MatThickActList)):
            if type(MatThickActList[i][0])!=str:
                MatThickActList[i][0]=MatThickActList[i][0].get()
            if type(MatThickActList[i][1])!=int:
                MatThickActList[i][1]=int(MatThickActList[i][1].get())
            if type(MatThickActList[i][2])!=int:
                MatThickActList[i][2]=int(MatThickActList[i][2].get())
            if type(MatThickActList[i][3])!=int:
                MatThickActList[i][3]=int(MatThickActList[i][3].get())
                
        try:
            owd = os.getcwd()
        
            os.chdir(stackDir)
        
            f = filedialog.asksaveasfilename(defaultextension=".txt", filetypes = (("text file", "*.txt"),("All Files", "*.*")))
            
            file = open(f,'w')
            file.writelines("%s\t%d\t%d\t%d\n" % tuple(item) for item in MatThickActList)
            file.close()
            
            os.chdir(owd)
            
            stacklist=os.listdir(stackDir)
            stackNameList=[]
            for item in stacklist:
                stackNameList.append(item.split('.')[0])
        except:
            print("something wrong during saving process...")
        self.updatelist()
    
    def updatelist(self):
        global MatThickActList

        for i in range(len(MatThickActList)):
            if type(MatThickActList[i][0])!=str:
                MatThickActList[i][0]=MatThickActList[i][0].get()
            if type(MatThickActList[i][1])!=int:
                MatThickActList[i][1]=int(MatThickActList[i][1].get())
            if type(MatThickActList[i][2])!=int:
                MatThickActList[i][2]=int(MatThickActList[i][2].get())
            if type(MatThickActList[i][3])!=int:
                MatThickActList[i][3]=int(MatThickActList[i][3].get())

        self.frame6.destroy()
        self.frame6 = tk.Frame(self.canvas0, background="#ffffff")
        self.canvas0.create_window((4,4), window=self.frame6, anchor="nw", tags="self.frame6")
        self.frame6.bind("<Configure>", self.onFrameConfigure)
        self.populate()
    
    
    ####################start simulation code##############################
    def simulate(self):
        if self.check1D.get()==1 and self.check2D.get()==1:
            print("cannot make both 1D and 2D at the same time")
        else:
            self.simulate1()
            
    def simulate1(self):
        global numberofLayer
        global matnamelist
        global MatThickActList
        
        for i in range(len(MatThickActList)):
            if type(MatThickActList[i][0])!=str:
                MatThickActList[i][0]=MatThickActList[i][0].get()
            if type(MatThickActList[i][1])!=int:
                MatThickActList[i][1]=int(MatThickActList[i][1].get())
            if type(MatThickActList[i][2])!=int:
                MatThickActList[i][2]=int(MatThickActList[i][2].get())
            if type(MatThickActList[i][3])!=int:
                MatThickActList[i][3]=int(MatThickActList[i][3].get())
        
        #ask path to export
        owd = os.getcwd()
        
        os.chdir(resDir)
        
        f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
            
        os.chdir(owd)
        
        #check the wavelength range and readapt to have only in decades (round to nearest decade)
        start=divmod(self.StartWave.get(),10)
        startWave=int(self.StartWave.get())
        if start[1]!=0:
            if start[1]>5:
                startWave=int((start[0]+1)*10)
            else:
                startWave=int(start[0]*10)
        end=divmod(self.EndWave.get(),10)
        EndWave=int(self.EndWave.get())
        if end[1]!=0:
            if end[1]>5:
                EndWave=int((end[0]+1)*10)
            else:
                EndWave=int(end[0]*10)

        #create structure and fill with user-defined layer properties
       
        if MatThickActList!=[]:
            if MatThickActList[0][3]==1:
                coher='i'
            else:
                coher='c'
            structure=multilayer(layer(material_list[MatThickActList[0][0]],MatThickActList[0][1],coher))
            if len(MatThickActList)>1:
                for i in range(1,len(MatThickActList)):
                    if MatThickActList[i][3]==1:
                        coher='i'
                    else:
                        coher='c'
                    structure.addlayer(layer(material_list[MatThickActList[i][0]],MatThickActList[i][1],coher))
        
        #create spectrum according to start and end Wavelength
        specttotake=[[],[]]
        for item in range(len(AM1p5Gc[0])):
            if AM1p5Gc[0][item] >= startWave and AM1p5Gc[0][item] <= EndWave:
                specttotake[0].append(AM1p5Gc[0][item])
                specttotake[1].append(AM1p5Gc[1][item])
        
        #check which layer is active and calculate current, print
        huss=structure.geninalllays(specttotake,1,0,1,'s')
        numbofactive=0
        spectofactivelayers=[]
        namesofactive=[]
        specR=structure.calculateRTrange(specttotake[0],1,0,1,'s')
        currents=[]
        for i in range(len(MatThickActList)):
            if MatThickActList[i][2]==1:
                numbofactive+=1
                spectofactivelayers.append(structure.absspectruminlay(i+1,specttotake[0],1,0,1,'s'))
                Jsc=str(MatThickActList[i][0])+': '+"%.2f"%huss[i+1]+'\n'
                currents.append(Jsc)
                namesofactive.append(MatThickActList[i][0])
                print(Jsc)
        if spectofactivelayers!=[]:
            spectotal=[specR[0],np.asarray(spectofactivelayers[0][1])]

            for i in range(1,len(spectofactivelayers)):   
                spectotal[1]+=np.asarray(spectofactivelayers[i][1])

            #make graph and export
            datatoexport=[]
            headoffile1=""
            headoffile2=""
            plt.figure()
            k=0
            for item in spectofactivelayers:
                plt.plot(item[0],item[1],label=currents[k][:-1])
                datatoexport.append(item[0])
                datatoexport.append(item[1])
                headoffile1+="Wavelength\tIntensity\t"
                headoffile2+=" \t"+namesofactive[k]+"\t"
                k+=1
            if len(spectofactivelayers)>1:
                plt.plot(spectotal[0],spectotal[1],label="Total")
                datatoexport.append(spectotal[0])
                datatoexport.append(spectotal[1])
                headoffile1+="Wavelength\tIntensity\t"
                headoffile2+=" \tTotal\t"
                
            specRR=[specR[0],1-np.asarray(specR[1])-np.asarray(specR[2])]
            datatoexport.append(specRR[0])
            datatoexport.append(specRR[1])
            headoffile1+="Wavelength\tIntensity\n"
            headoffile2+=" \tReflectance\n"
            plt.plot(specRR[0],specRR[1],label="Reflectance")
            plt.xlabel("Wavelength (nm)")
            plt.ylabel("Light Intensity Fraction")
            plt.xlim([specRR[0][0],specRR[0][-1]])
            plt.ylim([0,1])
            plt.legend(loc='lower right',ncol=1)
            plt.savefig(f, dpi=300, transparent=False) 
            plt.close()
            datatoexportINV=[list(x) for x in zip(*datatoexport)]
            datatoexportINVtxt=[]
            for item in datatoexportINV:
                lineinterm=""
                for i in range(len(item)-1):
                    lineinterm+=str(item[i])+"\t"
                lineinterm+=str(item[len(item)-1])+"\n"
                datatoexportINVtxt.append(lineinterm)
            
            file = open(f[:-4]+"_rawdata.txt",'w')
            file.writelines(headoffile1)
            file.writelines(headoffile2)
            file.writelines(item for item in datatoexportINVtxt)
            file.close()
        
        if self.check1D.get()==1:
            #ask which layer to scan and what range
            self.simulatedialog = tk.Toplevel()
            self.simulatedialog.wm_title("Define the variation ranges")
            self.simulatedialog.geometry("350x200")
            center(self.simulatedialog)
            
            self.matlistfor2Dvar=[item[0] for item in MatThickActList]
            frame1=Frame(self.simulatedialog,borderwidth=0,  bg="white")
            frame1.pack(side=tk.LEFT,fill=tk.BOTH, expand=1)
            label = tk.Label(frame1, text="Material1", font=SMALL_FONT, bg="white",fg="black")
            label.pack()
            tk.Label(frame1, text="from",font=SMALL_FONT,  bg="white").pack()
            self.Startthick1 = tk.DoubleVar()
            Entry(frame1, textvariable=self.Startthick1,width=5).pack()
            self.Startthick1.set(0)
            tk.Label(frame1, text="step",font=SMALL_FONT,  bg="white").pack() 
            self.Stepthick1 = tk.DoubleVar()
            Entry(frame1, textvariable=self.Stepthick1,width=5).pack()
            self.Stepthick1.set(1)
            tk.Label(frame1, text="to",font=SMALL_FONT,  bg="white").pack() 
            self.Endthick1 = tk.DoubleVar()
            Entry(frame1, textvariable=self.Endthick1,width=5).pack() 
            self.Endthick1.set(10)
            #tk.Label(frame1, text="layer#?",font=SMALL_FONT,  bg="white").pack() 
            #self.layernumb1 = tk.DoubleVar()
            #Entry(frame1, textvariable=self.layernumb1,width=5).pack() 
            #self.layernumb1.set(0)
            
            self.Matchoice1=StringVar()
            self.dropMenu2D1 = OptionMenu(frame1, self.Matchoice1, *self.matlistfor2Dvar, command=())
            self.dropMenu2D1.pack()
            self.Matchoice1.set(self.matlistfor2Dvar[0])
            
            frame3=Frame(self.simulatedialog,borderwidth=0,  bg="white")
            frame3.pack(fill=tk.BOTH, expand=1)
            StartSim = Button(frame3, text="Start simulation",width=15, command = self.Sim1DthickVar)
            StartSim.pack(fill=tk.BOTH, expand=1)
            
            CancelSim = Button(frame3, text="Cancel",width=15, command = self.CancelSim)
            CancelSim.pack(fill=tk.BOTH, expand=1)
            
            self.structure=structure
            self.specttotake=specttotake
            self.f=f
            
        if self.check2D.get()==1:
            self.simulatedialog = tk.Toplevel()
            self.simulatedialog.wm_title("Define the variation ranges")
            self.simulatedialog.geometry("350x200")
            center(self.simulatedialog)
            
            self.matlistfor2Dvar=[item[0] for item in MatThickActList]
            frame1=Frame(self.simulatedialog,borderwidth=0,  bg="white")
            frame1.pack(side=tk.LEFT,fill=tk.BOTH, expand=1)
            label = tk.Label(frame1, text="Material1", font=SMALL_FONT, bg="white",fg="black")
            label.pack()
            tk.Label(frame1, text="from",font=SMALL_FONT,  bg="white").pack()
            self.Startthick1 = tk.DoubleVar()
            Entry(frame1, textvariable=self.Startthick1,width=5).pack()
            self.Startthick1.set(0)
            tk.Label(frame1, text="step",font=SMALL_FONT,  bg="white").pack() 
            self.Stepthick1 = tk.DoubleVar()
            Entry(frame1, textvariable=self.Stepthick1,width=5).pack()
            self.Stepthick1.set(1)
            tk.Label(frame1, text="to",font=SMALL_FONT,  bg="white").pack() 
            self.Endthick1 = tk.DoubleVar()
            Entry(frame1, textvariable=self.Endthick1,width=5).pack() 
            self.Endthick1.set(10)
            
            self.Matchoice1=StringVar()
            self.dropMenu2D1 = OptionMenu(frame1, self.Matchoice1, *self.matlistfor2Dvar, command=())
            self.dropMenu2D1.pack()
            self.Matchoice1.set(self.matlistfor2Dvar[0])
            
            frame2=Frame(self.simulatedialog,borderwidth=0,  bg="white")
            frame2.pack(side=tk.RIGHT,fill=tk.BOTH,expand=1)
            label = tk.Label(frame2, text="Material2", font=SMALL_FONT, bg="white",fg="black")
            label.pack()
            tk.Label(frame2, text="from",font=SMALL_FONT,  bg="white").pack()
            self.Startthick2 = tk.DoubleVar()
            Entry(frame2, textvariable=self.Startthick2,width=5).pack()
            self.Startthick2.set(0)
            tk.Label(frame2, text="step",font=SMALL_FONT,  bg="white").pack() 
            self.Stepthick2 = tk.DoubleVar()
            Entry(frame2, textvariable=self.Stepthick2,width=5).pack()
            self.Stepthick2.set(1)
            tk.Label(frame2, text="to",font=SMALL_FONT,  bg="white").pack() 
            self.Endthick2 = tk.DoubleVar()
            Entry(frame2, textvariable=self.Endthick2,width=5).pack() 
            self.Endthick2.set(10)
            
            self.Matchoice2=StringVar()
            self.Matchoice2.set(self.matlistfor2Dvar[0])
            self.dropMenu2D2 = OptionMenu(frame2, self.Matchoice2, *self.matlistfor2Dvar, command=())
            self.dropMenu2D2.pack()
            
            frame3=Frame(self.simulatedialog,borderwidth=0,  bg="white")
            frame3.pack(fill=tk.BOTH, expand=1)
            StartSim = Button(frame3, text="Start simulation",width=15, command = self.Sim2DthickVar)
            StartSim.pack(fill=tk.BOTH, expand=1)
            
            CancelSim = Button(frame3, text="Cancel",width=15, command = self.CancelSim)
            CancelSim.pack(fill=tk.BOTH, expand=1)
            
            self.structure=structure
            self.specttotake=specttotake
            self.f=f
            
        
        #reupdate the screen
        print("finished")
        self.updatelist()
    
    def CancelSim(self):
        self.simulatedialog.destroy()
        self.updatelist()
    
    def Sim1DthickVar(self):
        global MatThickActList
        
        for i in range(len(MatThickActList)):
            if type(MatThickActList[i][0])!=str:
                MatThickActList[i][0]=MatThickActList[i][0].get()
            if type(MatThickActList[i][1])!=int:
                MatThickActList[i][1]=int(MatThickActList[i][1].get())
            if type(MatThickActList[i][2])!=int:
                MatThickActList[i][2]=int(MatThickActList[i][2].get())
            if type(MatThickActList[i][3])!=int:
                MatThickActList[i][3]=int(MatThickActList[i][3].get())
        
        d=self.structure.scanlayerthickness(self.matlistfor2Dvar.index(self.Matchoice1.get())+1,range(int(self.Startthick1.get()),int(self.Endthick1.get()+1),int(self.Stepthick1.get())),self.specttotake,1,0,1,'s')
        dinv=[list(x) for x in zip(*d)]
        
        head="Thickness\tAir\t"
        for item in self.matlistfor2Dvar:
            head+=item+"\t"
        head+="Air\n"
        datatoexportINVtxt=[]
        for item in dinv:
            lineinterm=""
            for i in range(len(item)-1):
                lineinterm+=str(item[i])+"\t"
            lineinterm+=str(item[len(item)-1])+"\n"
            datatoexportINVtxt.append(lineinterm)
        
        file = open(self.f[:-4]+"_1Drawdata.txt",'w')
        file.writelines(head)
        file.writelines(item for item in datatoexportINVtxt)
        file.close()
        
        plt.figure()
        activelist=[]
        for i in range(len(MatThickActList)):
            if MatThickActList[i][2]==1:
                activelist.append(i)
                plt.plot(d[0],d[i+2],label=MatThickActList[i][0])
        
        plt.xlabel(self.Matchoice1.get()+" thickness (nm)")
        plt.ylabel("Current")
        plt.legend(ncol=1)
        plt.savefig(self.f[:-4]+"_1D.png", dpi=300, transparent=False)
        plt.close()
        self.simulatedialog.destroy()
        self.updatelist()
        
    def Sim2DthickVar(self):
        global MatThickActList
        
        for i in range(len(MatThickActList)):
            if type(MatThickActList[i][0])!=str:
                MatThickActList[i][0]=MatThickActList[i][0].get()
            if type(MatThickActList[i][1])!=int:
                MatThickActList[i][1]=int(MatThickActList[i][1].get())
            if type(MatThickActList[i][2])!=int:
                MatThickActList[i][2]=int(MatThickActList[i][2].get())
            if type(MatThickActList[i][3])!=int:
                MatThickActList[i][3]=int(MatThickActList[i][3].get())
        
        d=self.structure.scanlayerthickness2D(self.matlistfor2Dvar.index(self.Matchoice1.get())+1,self.matlistfor2Dvar.index(self.Matchoice2.get())+1,range(int(self.Startthick1.get()),int(self.Endthick1.get()+1),int(self.Stepthick1.get())),range(int(self.Startthick2.get()),int(self.Endthick2.get()+1),int(self.Stepthick2.get())),self.specttotake,1,0,1,'s')

        #print(d)
        
        datatoexporttxt=[]
        
        for i in range(len(d)):
            for j in range(len(d[i][1])):
                linetxt=str(d[i][0])
                for k in range(len(d[i][1][j])):
                    linetxt+="\t"+str(d[i][1][j][k])
                linetxt+="\n"
                datatoexporttxt.append(linetxt)
                
        head="Thick. "+self.Matchoice1.get()+"\tThick. "+self.Matchoice2.get()+"\tAir\t"
        for item in self.matlistfor2Dvar:
            head+=item+"\t"
        head+="Air\n"
        file = open(self.f[:-4]+"_2Drawdata.txt",'w')
        file.writelines(head)
        file.writelines(item for item in datatoexporttxt)
        file.close()
        
        self.simulatedialog.destroy()
        self.updatelist()
        
    
    ######################end simulation code################################
    
    def Help(self):
              
        self.window = tk.Toplevel()
        self.window.wm_title("HelpDesk")
        self.window.geometry("900x200")
        self.window.config(background="white")
        center(self.window)
        
        S=Scrollbar(self.window)
        T=tk.Text(self.window,height=50,width=200)
        S.pack(side=tk.RIGHT, fill=tk.Y)
        T.pack(side=tk.LEFT, fill=tk.BOTH,expand=1)
        S.config(command=T.yview)
        T.config(yscrollcommand=S.set)
        quote= """
 More info about transfer matrix modeling: https://en.wikipedia.org/wiki/Transfer-matrix_method_(optics)
 
####
 based on transfer matrix python package tmm, written by Steven Byrnes, http://sjbyrnes.com
 main code to generate the matrices and calculate the currents written by Gabriel Christmann (PV-Center, CSEM)
 readaptation and completion by J.Werner (PV-Lab, EPFL), 2017-18
 
 IQE=100%
 the light is considered entering/exiting from/to an incoherent medium with refractive index of 1 (Air), and perpendicular to the device plane.
 all layers are considered flat.                                                                                                 
        """
        T.insert(tk.END,quote)
            
        
###############################################################################        
if __name__ == '__main__':
    app = TMSimApp()
    app.mainloop()


