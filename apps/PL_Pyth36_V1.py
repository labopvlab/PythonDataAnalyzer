#! python3

import os
from tkinter import filedialog
import csv
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
from scipy import integrate
from scipy.interpolate import interp1d

"""
-

"""


def gaus(x,a,x0,sigma):
    return a*np.exp(-(x-x0)**2/(2*sigma**2))

def PLSummary():
    #select the baseline
    ready=0
    j=0
    while j<2:
        try: 
            file_path_baseline =filedialog.askopenfilenames(title="Please select the PL baseline file")
            if file_path_baseline!='':
                ready=1 
                directory = filedialog.askdirectory(title="Where saving?")
                    
                if not os.path.exists(directory):
                    os.makedirs(directory)
                    os.chdir(directory)
                else :
                    os.chdir(directory)
                break
            else:
                print("Please select correct PL csv files")
                j+=1
        except:
            print("no file selected")
            j+=1
    
    baselines=[]
    for i in range(len(file_path_baseline)):
        with open(file_path_baseline[i]) as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            CSVdat=[]
            for row in readCSV:
                CSVdat.append(row)
            energies=[]
            intensities=[]
            for j in range(2,len(CSVdat)-1):
                energies.append(float(CSVdat[j][0]))
                intensities.append(float(CSVdat[j][1]))
            baselines.append([energies,intensities])
    
    #select the csv files
    ready=0
    j=0
    while j<2:
        try: 
            file_path_csv =filedialog.askopenfilenames(title="Please select the PL csv file")
            if file_path_csv!='':
                ready=1
                break
            else:
                print("Please select correct PL csv files")
                j+=1
        except:
            print("no file selected")
            j+=1    
    
    #read them all and extract data
    #export to txt file first column the energy, then all the intensity columns with titles named as Frame number or nothing is only 1 frame
    #baseline-corrected and normalized data
    initialpeakvalue=[] 
    peakareas=[]
    if ready:
        for i in range(len(file_path_csv)):
            name=os.path.split(file_path_csv[i])[-1]
            txtfile=["Energy"+"\t"+"Intensity"+"\n","eV"+ "\t"+ "-"+"\n",name+"\n"," \t \n"]
            with open(file_path_csv[i]) as csvfile:
                readCSV = csv.reader(csvfile, delimiter=',')
                CSVdat=[]
                energies=[]
                intensities=[]
                intensitiescorr=[]
                for row in readCSV:
                    CSVdat.append(row)
                if CSVdat[2][0]!="Frame 1": #initialpeak
                    for j in range(2,len(CSVdat)-1):
                        energies.append(float(CSVdat[j][0]))
                        intensities.append(float(CSVdat[j][1]))
                        txtfile.append(CSVdat[j][0]+"\t"+CSVdat[j][1]+"\n")
                    basefound=0
                    for j in range(len(baselines)):
                        if baselines[j][0][0]==energies[0]:
                            for k in range(len(intensities)):
                                intensitiescorr.append(intensities[k]-baselines[j][1][k])
                            basefound=1
                            break
                    if basefound:
                        txtfile=["Energy"+"\t"+"Intensity"+"\t"+"IntensityCorr"+"\t"+"IntensityCorrNorm"+"\n","eV"+ "\t"+ "-"+ "\t"+ "-"+ "\t"+ "-"+"\n",name+"\n"," \t \n"]
                        minimum=min(intensitiescorr)
                        maximum=max(intensitiescorr)
                        intensitiescorrnorm=[(x-minimum)/(maximum-minimum) for x in intensitiescorr]
                        for j in range(len(energies)):
                            txtfile.append(str(energies[j])+"\t"+str(intensities[j])+"\t"+str(intensitiescorr[j])+"\t"+str(intensitiescorrnorm[j])+"\n")
                        
                        x=np.array(energies)
                        y=np.array(intensitiescorrnorm)
                        
                        peak_value = y.max()
                        mean = x[y.argmax()] # observation of the data shows that the peak is close to the center of the interval of the x-data
                        sigma = mean - np.where(y > peak_value * np.exp(-5))[0][0] # when x is sigma in the gaussian model, the function evaluates to a*exp(-.5)
                        popt,pcov = curve_fit(gaus,x,y,p0=[peak_value,mean,sigma])

                        initialpeakvalue.append([name,popt.max()])
                        plt.plot(x,y,'b+:',label='data')
                        plt.plot(x,gaus(x,*popt),'ro:',label='fit')
                        plt.legend()
                        plt.title("max= "+str(popt.max()))
                        plt.xlabel('Energy (eV)')
                        plt.ylabel('PL intensity (-)')
                        plt.savefig(name+".png", dpi=300, transparent=False) 
                        plt.close()
                        
                    file = open(name+'.txt','w')
                    file.writelines("%s" % item for item in txtfile)
                    file.close()
                else: #if file is for ptbypt
                    txtfile=[]
                    txtfilecorr=[]
                    for j in range(3,len(CSVdat)):
                        if CSVdat[j]!=[]:
                            if "Frame" not in CSVdat[j][0]:
                                energies.append(float(CSVdat[j][0]))
                                txtfile.append(str(energies[-1]))
                                txtfilecorr.append(str(energies[-1]))
                            elif "Frame" in CSVdat[j][0]:
                                break
                    basenumb=99999
                    for j in range(len(baselines)):
                        if baselines[j][0][0]==energies[0]:
                            basenumb=j
                            break
                    if basenumb==99999:
                        print("no baseline found")
                    else:
                        intensities=[]
                        interm=[]
                        for j in range(3,len(CSVdat)):
                            if CSVdat[j]!=[]:
                                if "Frame" not in CSVdat[j][0]:
                                    interm.append(float(CSVdat[j][1]))
                                elif "Frame" in CSVdat[j][0]:
                                    intensities.append(interm)
                                    interm=[]
                                    
                        intensities.append(interm)
                               
                        intensitiescorr=[]
                        intensitiescorrnorm=[]
                        for j in range(len(intensities)):
                            corrinterm=[]
                            for k in range(len(intensities[j])):
                                corrinterm.append(intensities[j][k]-baselines[basenumb][1][k])
                            intensitiescorr.append(corrinterm)
                            minimum=min(corrinterm)
                            maximum=max(corrinterm)
                            intensitiescorrnorm.append([(x-minimum)/(maximum-minimum) for x in corrinterm])
                        
                        entete2=" "
                        entete1="eV"
                        entete0="Energy"
                        for j in range(len(intensities)):
                            entete2+="\tFrame "+str(j+1)
                            entete1+="\t"+"-"
                            entete0+="\tIntensityCorrNorm"
                            for k in range(len(intensities[j])):
                                txtfile[k]+="\t"+str(intensitiescorrnorm[j][k])
                        txtfile.insert(0,entete2)  
                        txtfile.insert(0,entete1)  
                        txtfile.insert(0,entete0) 
                        for k in range(len(txtfile)):
                            txtfile[k]+="\n"
                        
                        file = open(name+'_norm.txt','w')
                        file.writelines("%s" % item for item in txtfile)
                        file.close()
                        
                        entete2=" "
                        entete1="eV"
                        entete0="Energy"
                        for j in range(len(intensities)):
                            entete2+="\tFrame "+str(j+1)
                            entete1+="\t"+"-"
                            entete0+="\tIntensityCorr"
                            for k in range(len(intensities[j])):
                                txtfilecorr[k]+="\t"+str(intensitiescorr[j][k])
                        txtfilecorr.insert(0,entete2)  
                        txtfilecorr.insert(0,entete1)  
                        txtfilecorr.insert(0,entete0) 
                        for k in range(len(txtfilecorr)):
                            txtfilecorr[k]+="\n"
                        
                        file = open(name+'.txt','w')
                        file.writelines("%s" % item for item in txtfilecorr)
                        file.close()
                        
                        peaksareainterm=[]
                        for k in range(len(intensitiescorrnorm)):
                            x=np.array(energies)
                            y=np.array(intensitiescorrnorm[k])
                            f = interp1d(x, y, kind='linear')
                            xnew=lambda x: f(x)
                            integral=integrate.quad(xnew, x.min(), x.max())
                            peaksareainterm.append(integral[0])
                        file = open(name+'peaksarea.txt','w')
                        file.writelines("%s \t %s \n" % (str(item+1), str(peaksareainterm[item])) for item in range(len(peaksareainterm)))
                        file.close()
                        peakareas.append([name,peaksareainterm])
                        
            csvfile.close()
        file = open('initialPeakPositions.txt','w')
        file.writelines("%s \t %s \n" % (item[0], item[1]) for item in initialpeakvalue)
        file.close()
        
        plt.close()
        for i in range(len(peakareas)):
            plt.plot(range(1,len(peakareas[i][1])+1),peakareas[i][1],label=peakareas[i][0])
        #plt.legend()
        plt.xlabel('Frame #')
        plt.ylabel('Area under the curve')
        plt.savefig("peakareaevolution.png", dpi=300, transparent=False) 

###############################################################################        
if __name__ == '__main__':
    PLSummary()

