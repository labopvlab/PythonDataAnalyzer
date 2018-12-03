#! python3

import os
from tkinter import filedialog
import csv
import math
from tkinter import Tk, messagebox
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
from scipy import integrate
from scipy.interpolate import interp1d
import peakutils
from peakutils.plot import plot as pplot
import xlsxwriter
import xlrd
from matplotlib import colors as mcolors


""""

"""





def listofpeakinfo(x,y,indexes,samplename):#x and y are np.arrays

    peakdata=[]
    try:
        plt.clear()
    except:
        pass
    plt.figure(figsize=(10,6))
    plt.plot(x,y,'black',label=samplename)
    
    
    for item in range(len(indexes)):
        nbofpoints=80#on each side of max position
        while(1):
            try:
                x0=x[indexes[item]-nbofpoints:indexes[item]+nbofpoints]
                y0=y[indexes[item]-nbofpoints:indexes[item]+nbofpoints]
        
                #baseline height
                bhleft=np.mean(y0[:20])
                bhright=np.mean(y0[-20:])
                baselineheightatmaxpeak=(bhleft+bhright)/2
                
                if abs(bhleft-bhright)<50:#arbitrary choice of criteria...
                    #find FWHM
                    d=y0-((max(y0)-bhright)/2)
                    ind=np.where(d>bhright)[0]
                    
                    hl=(x0[ind[0]-1]*y0[ind[0]]-y0[ind[0]-1]*x0[ind[0]])/(x0[ind[0]-1]-x0[ind[0]])
                    ml=(y0[ind[0]-1]-hl)/x0[ind[0]-1]
                    yfwhm=((max(y0)-baselineheightatmaxpeak)/2)+baselineheightatmaxpeak
                    xleftfwhm=(yfwhm - hl)/ml
                    hr=(x0[ind[-1]]*y0[ind[-1]+1]-y0[ind[-1]]*x0[ind[-1]+1])/(x0[ind[-1]]-x0[ind[-1]+1])
                    mr=(y0[ind[-1]]-hr)/x0[ind[-1]]
                    xrightfwhm=(yfwhm - hr)/mr
                    
                    FWHM=abs(xrightfwhm-xleftfwhm)
                    Peakheight=max(y0)-baselineheightatmaxpeak
                    center=x[indexes[item]]
                                 
                    plt.plot(x0, y0, 'red')
                    plt.plot([x0[0],x0[-1]],[bhleft,bhright],'blue')
#                    plt.plot(x0,y0,ms=0)
                    plt.plot([xleftfwhm,xrightfwhm],[yfwhm,yfwhm],'green')
                    plt.text(center,max(y0)+200,str('%.1f' % float(center)),rotation=90,verticalalignment='bottom',horizontalalignment='center',multialignment='center')
                                      
                    peakdata.append([center,FWHM,Peakheight])
                    break
                else:
                    if nbofpoints>=15:
                        nbofpoints-=10
                    else:
                        print("indexerror unsolvable")
                        break
            except IndexError:
                if nbofpoints>=15:
                    nbofpoints-=10
                else:
                    print("indexerror unsolvable")
                    break
    plt.scatter(x[indexes],y[indexes],c='red',s=12)
    plt.legend()
    plt.ylabel("Intensity (a.u.)")
    plt.xlabel("2\u0398 (degree)")
    plt.savefig(samplename+'.pdf')
#    plt.show()
    plt.close()
    return peakdata


#%%
#threshold=0.05
#MinDist=50
#    
#filetoread = open(os.path.join('C:\\Users\\jwerner\\switchdrive\\python\\xrddata\\data','P514_25.asc'))
#samplename="name"
#filerawdata = filetoread.readlines()
#DATA=[]
#x=[]
#y=[]
#    
#for item in filerawdata:
#    x.append(float(item.split(' ')[0]))
#    y.append(float(item.split(' ')[1]))
#
#x=np.array(x)
#y=np.array(y)
#if max(y)>3000:
#    threshold=0.05
#else:
#    threshold=0.065
#indexes = peakutils.indexes(y, thres=threshold, min_dist=MinDist)
#
#dat=listofpeakinfo(x,y,indexes,samplename)
#
#DATA.append([str(samplename),x,y,dat,max([item[2] for item in dat])])#[samplename,X,Y,[[center,FWHM,Peakheight],[]...],maxpeakheight]

#plt.figure(figsize=(10,15))
#plt.plot(DATA[0][1],DATA[0][2])


#%%
def XRDautoanalysis():
    global colorstylelist
    
    file_path =filedialog.askopenfilenames(title="Please select the XRD files")
    #select a result folder
    
    current_path=os.path.dirname(os.path.dirname(file_path[0]))
#    print(current_path)
    folderName = filedialog.askdirectory(title = "choose a folder to export the auto-analysis results", initialdir=current_path)
    os.chdir(folderName)
    
    DATA=[]
    #analyze and create data list
    #export graphs on-the-fly
    
    for filename in file_path:
        filetoread = open(filename,"r")
        filerawdata = filetoread.readlines()
        samplename=os.path.splitext(os.path.basename(filename))[0]
    
        x=[]
        y=[]
            
        for item in filerawdata:
            x.append(float(item.split(' ')[0]))
            y.append(float(item.split(' ')[1]))
        
        x=np.array(x)
        y=np.array(y)
        
    #    if max(y)<3000:
    #        threshold=0.065
    #    elif max(y)>3000 and max(y)<10000:
    #        threshold=0.05
    #    elif max(y)>10000:
    #        threshold=0.04    
        threshold=0.01  
        MinDist=50
        
        while(1):
            indexes = peakutils.indexes(y, thres=threshold, min_dist=MinDist)
    #        print(len(indexes))
            if len(indexes)<15:
                break
            else:
                threshold+=0.01
        
        dat=listofpeakinfo(x,y,indexes,samplename)
        
        DATA.append([str(samplename),x,y,dat,max([item[2] for item in dat])])#[samplename,X,Y,[[center,FWHM,Peakheight],[]...],maxpeakheight]
    
    #create a graph with all rawdata arranged vertically, without overlapping
    font = {'color':  'black',
            'weight': 'bold',
            'size': 12
            }
    
    plt.figure(figsize=(10,15))
    plt.plot(DATA[0][1],DATA[0][2])
    plt.text(5,DATA[0][2][1],DATA[0][0],horizontalalignment='right',fontdict=font,bbox=dict(facecolor='white', edgecolor='white', pad=0.0))
    cumulativeheight=0
    dataextended=[list(DATA[0][1]),list(DATA[0][2])]
    headings=["2theta\tIntensity\t","deg\t-\t","-\t"+DATA[0][0]+"\t"]
    for i in range(1,len(DATA)):
        cumulativeheight+=float(max(DATA[i-1][2]))+200
        newy=[item2+cumulativeheight for item2 in list(DATA[i][2])]
        dataextended.append(list(DATA[i][1]))
        dataextended.append(newy)
        headings[0]+="2theta\tIntensity\t"
        headings[1]+="deg\t-\t"
        headings[2]+="-\t"+DATA[i][0]+"\t"
        plt.plot(list(DATA[i][1]),newy)
        plt.text(5,DATA[i][2][1]+cumulativeheight,DATA[i][0],horizontalalignment='right',fontdict=font,bbox=dict(facecolor='white', edgecolor='white', pad=0.0))
    
    plt.yticks([])
    plt.xlabel("2\u0398 (degree)")
    plt.savefig('Allxrdtogether.pdf')
    #plt.show()
    
    #export txt file with rawdata to replot it in origin
    dataextended=list(map(list,zip(*dataextended)))
    
    for i in range(len(dataextended)):
        textdat=""
        for item in dataextended[i]:
            textdat+=str(item)+"\t"
        headings.append(textdat)
    
    for i in range(len(headings)):
        headings[i]=headings[i][:-1]+"\n"
    file = open("Allxrdtogether.txt",'w')
    file.writelines("%s" % item for item in headings)
    file.close()
    #export excel summary file with all peak info
    workbook = xlsxwriter.Workbook('Summary.xlsx')
    
    #one tab for PbI2 peak: look for samples having a peak between 11.5 and 13
    #export graph of xrd curves restricted to this peak
    plt.close()
    PbI2peak=plt.figure(figsize=(10,6))
    worksheet = workbook.add_worksheet("PbI2-12ishDeg")
    worksheetdat=[["SampleName","Position","FWHM","Intensity"]]
    maxpeak=0
    for i in range(len(DATA)):
        for j in range(len(DATA[i][3])):
            if DATA[i][3][j][0]<=13:
                if DATA[i][3][j][0]>12 and DATA[i][3][j][0]<13.2:
                    worksheetdat.append([DATA[i][0],DATA[i][3][j][0],DATA[i][3][j][1],DATA[i][3][j][2]])
                    plt.plot(DATA[i][1],DATA[i][2],label=DATA[i][0])
                    maxPbi2=max([DATA[i][2][k] for k in range(len(DATA[i][1])) if DATA[i][1][k]<13.2 and DATA[i][1][k]>12])
                    if maxPbi2>maxpeak:
                        maxpeak=maxPbi2
            else:
                break
    for item in range(len(worksheetdat)):
        for item0 in range(len(worksheetdat[item])):
            worksheet.write(item,item0,worksheetdat[item][item0])
    plt.xlim(right=13.2)
    plt.xlim(left=12.2)
    plt.ylim(top=1.01*maxpeak)
    plt.ylim(bottom=0)
    plt.yticks([])
    plt.ylabel("Intensity (a.u.)")
    plt.xlabel("2\u0398 (degree)")
    if len(worksheetdat)>1:
        if item>7:
            leg=PbI2peak.legend(loc='center left', bbox_to_anchor=(0.2, 0.7),ncol=2)
        else:
            leg=PbI2peak.legend(loc='center left', bbox_to_anchor=(0.2, 0.7),ncol=1)
    #    extent = PbI2peak.get_window_extent().transformed(PbI2peak.dpi_scale_trans.inverted())
        PbI2peak.savefig('PbI2peaks.pdf', dpi=300, bbox_extra_artists=(leg,), transparent=True) 
    
    #plt.savefig('PbI2peaks.pdf')
    plt.close()
    PKpeak=plt.figure(figsize=(10,6))
    #one tab for Perovskite: between 13.5 and 15
    #export graph of xrd curves restricted to this peak
    worksheet = workbook.add_worksheet("Pk-14ishDeg")
    worksheetdat=[["SampleName","Position","FWHM","Intensity"]]
    maxpeak=0
    for i in range(len(DATA)):
        for j in range(len(DATA[i][3])):
            if DATA[i][3][j][0]<=15:
                if DATA[i][3][j][0]>13.5 and DATA[i][3][j][0]<15:
                    worksheetdat.append([DATA[i][0],DATA[i][3][j][0],DATA[i][3][j][1],DATA[i][3][j][2]])
                    plt.plot(DATA[i][1],DATA[i][2],label=DATA[i][0])
                    maxPk=max([DATA[i][2][k] for k in range(len(DATA[i][1])) if DATA[i][1][k]<15 and DATA[i][1][k]>13.5])
                    if maxPk>maxpeak:
                        maxpeak=maxPk
            else:
                break
    for item in range(len(worksheetdat)):
        for item0 in range(len(worksheetdat[item])):
            worksheet.write(item,item0,worksheetdat[item][item0])
    plt.xlim(right=15)
    plt.xlim(left=13.5)
    plt.ylim(top=1.01*maxpeak)
    plt.ylim(bottom=0)
    plt.yticks([])
    plt.ylabel("Intensity (a.u.)")
    plt.xlabel("2\u0398 (degree)")
    if len(worksheetdat)>1:
        #plt.legend(bbox_to_anchor=(1, 1), loc='upper left', ncol=1)
        if item>7:
            leg=PKpeak.legend(loc='center left', bbox_to_anchor=(0.2, 0.7),ncol=2)
        else:
            leg=PKpeak.legend(loc='center left', bbox_to_anchor=(0.2, 0.7),ncol=1)
    #    extent = PKpeak.get_window_extent().transformed(PKpeak.dpi_scale_trans.inverted())
        PKpeak.savefig('PKpeaks.pdf', dpi=300, bbox_extra_artists=(leg,), transparent=True) 
        #plt.savefig('PKpeaks.pdf')
    
    
    #one tab per sample with peaks position, height and FWHM
    for i in range(len(DATA)):
        worksheet = workbook.add_worksheet(DATA[i][0])
        summary=[["Position","FWHM","Intensity"]]+DATA[i][3]
        for item in range(len(summary)):
            for item0 in range(len(summary[item])):
                worksheet.write(item,item0,summary[item][item0])
    workbook.close()
    plt.close()
    
    messagebox.showinfo("Information","The analysis is over")

if __name__ == '__main__':    
    XRDautoanalysis()
    

#%%
#filename=file_path[0]
#filetoread = open(filename,"r")
#filerawdata = filetoread.readlines()
#
#x=[]
#y=[]
#
##print(filerawdata[0].split(' '))
#
#for item in filerawdata:
#    x.append(float(item.split(' ')[0]))
#    y.append(float(item.split(' ')[1]))
#
#x=np.array(x)
#y=np.array(y)
#
#indexes = peakutils.indexes(y, thres=threshold, min_dist=MinDist)
#
#dat=listofpeakinfo(x,y,indexes,"samplename")
#print(dat)
    
    
##find the peaks
#indexes = peakutils.indexes(y, thres=0.05, min_dist=20)
##print(x[indexes])
#plt.figure(figsize=(10,6))
#plt.plot(x,y,'black')
##plt.scatter(x[indexes],y[indexes],c='red')
##pplot(x, y, indexes)
#
##refine by interpolation
#peaks_x = peakutils.interpolate(x, y, ind=indexes)
##print(peaks_x)
#
##find and remove baseline
##base = peakutils.baseline(y, 3) #(y, deg=intepolation degree, max_it=None, tol=None)
##plt.figure(figsize=(10,6))
##plt.plot(x, y-base)
#
##print(len(indexes))
##find FWHM of particular peak, integrate area
#indexofStudiedPeak=indexes[2]
#nbofpoints=80#on each side of max position
#
#while(1):
#    try:
#        x0=x[indexofStudiedPeak-nbofpoints:indexofStudiedPeak+nbofpoints]
#        y0=y[indexofStudiedPeak-nbofpoints:indexofStudiedPeak+nbofpoints]
#
#        #baseline height
#        bhleft=np.mean(y0[:20])
#        bhright=np.mean(y0[-20:])
#        baselineheightatmaxpeak=(bhleft+bhright)/2
#        
#        if abs(bhleft-bhright)<30:#arbitrary choice of criteria...
#        
#            #find FWHM
#            d=y0-((max(y0)-bhright)/2)
#            ind=np.where(d>bhright)[0]
#            
#            hl=(x0[ind[0]-1]*y0[ind[0]]-y0[ind[0]-1]*x0[ind[0]])/(x0[ind[0]-1]-x0[ind[0]])
#            ml=(y0[ind[0]-1]-hl)/x0[ind[0]-1]
#            yfwhm=((max(y0)-baselineheightatmaxpeak)/2)+baselineheightatmaxpeak
#            xleftfwhm=(yfwhm - hl)/ml
#            #print(xleftfwhm)
#            hr=(x0[ind[-1]]*y0[ind[-1]+1]-y0[ind[-1]]*x0[ind[-1]+1])/(x0[ind[-1]]-x0[ind[-1]+1])
#            mr=(y0[ind[-1]]-hr)/x0[ind[-1]]
#            xrightfwhm=(yfwhm - hr)/mr
#            #print(xrightfwhm)
#            
#            FWHM=abs(xrightfwhm-xleftfwhm)
#    #        print(FWHM)
#            Peakheight=max(y0)-baselineheightatmaxpeak
#    #        print(Peakheight)
#            center=x[indexofStudiedPeak]
#    #        print(center)
#            
#            plt.plot(x0, y0)
#            plt.plot([x0[0],x0[-1]],[bhleft,bhright])
#            plt.scatter(x0,y0)
#            plt.scatter(x[indexofStudiedPeak],y[indexofStudiedPeak],c='red')
#            plt.plot([xleftfwhm,xrightfwhm],[yfwhm,yfwhm])
#            
#            plt.text(center,max(y0)+200,str('%.1f' % float(center)),rotation=90,verticalalignment='bottom',horizontalalignment='center',multialignment='center')
#    
#    #        print(len(indexes))
#            break
#        else:
#            if nbofpoints>=15:
#                nbofpoints-=10
#            else:
#                print("indexerror unsolvable")
#                break
#    except IndexError:
#        if nbofpoints>=15:
#            nbofpoints-=10
#        else:
#            print("indexerror unsolvable")
#            break

























