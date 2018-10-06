#! python3

from tkinter import Button, Tk, Label, Frame
from PIL import ImageTk


import PL_Pyth36_V1 as PL
import HallEffect_Pyth36 as Hall
import qsspc_Pyth36 as QSSPC
import ellipso_Pyth36 as Ellipso
import CMM_Pyth36_v1 as CMM
import Spectro_Pyth36 as spectrofcts
import TMsimulNew_Pyth36 as TMMfcts
import EQE_fcts_Pyth36_v2 as EQEfcts
import IV_fcts_Pyth36_V2 as IVfcts
import JVfollowup_Pyth36_v0 as JVfollowup
import Database_v0 as DB


"""todolist




"""

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



LARGE_FONT= ("Verdana", 12)

class TheAnalyser(Frame):
    
    def __init__(self,master):
        Frame.__init__(self, master)
        self.master=master
        self.master.resizable(False,False)       
        self.master.iconbitmap('icon1.ico')
        
        self.master.title('MultiDataAnalyzer')

        center(self.master)
        for j in range(20):
            for i in range(10):
                self.master.grid_rowconfigure(i,weight=1)
                self.master.grid_columnconfigure(j,weight=1)
                label = Label(self.master, text="A", font=LARGE_FONT,fg='red')
                label.grid(row=i, column=j,columnspan=1)
        background_label = Label(self.master, image=background_image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        EQEbutton = Button(root, text='EQE', command = self.callEQE)
        EQEbutton.grid(row=2,column=5,columnspan=2)
        Spectrobutton = Button(root, text='Spectro', command = self.callSpectro)
        Spectrobutton.grid(row=2,column=14,columnspan=2)
        Ellipsobutton = Button(root, text='Ellipso', command = self.callEllipso)
        Ellipsobutton.grid(row=3,column=14,columnspan=2)
        QSSPCbutton = Button(root, text='QSSPC', command = self.callQSSPC)
        QSSPCbutton.grid(row=4,column=14,columnspan=2)
        PLbutton = Button(root, text='PL', command = self.callPL)
        PLbutton.grid(row=5,column=14,columnspan=2)
        Hallbutton = Button(root, text='HallEffect', command = self.callHall)
        Hallbutton.grid(row=4,column=16,columnspan=3)
        IVbutton = Button(root, text='IV', command = self.callIV)
        IVbutton.grid(row=3,column=5,columnspan=2)
        CMMbutton = Button(root, text='CMM', command = self.callCMM)
        CMMbutton.grid(row=6,column=4,columnspan=3)
        TMSbutton = Button(root, text='TMM', command = self.callTMM)
        TMSbutton.grid(row=5,column=4,columnspan=3)
        DBbutton = Button(root, text='DATABASE', command = self.callDB)
        DBbutton.grid(row=6,column=17,columnspan=4)
        refcellbutton = Button(root, text='CellEvolCheck', command = self.callRefCell)
        refcellbutton.grid(row=6,column=14,columnspan=4)
        
            
    def callEQE(self):
        app=EQEfcts.EQEApp()
        app.mainloop()
       
    def callSpectro(self):
        app = spectrofcts.SpectroApp()
        app.mainloop()
        
    def callIV(self):
        app = IVfcts.IVApp()
        app.mainloop()
    
    def callTMM(self):
        app = TMMfcts.TMSimApp()
        app.mainloop()
        
    def callEllipso(self):
        Ellipso.EllipsoSummary()
        
    def callQSSPC(self):
        QSSPC.QSSPCSummary()
    
    def callPL(self):
        PL.PLSummary()
        
    def callHall(self):
        Hall.HallSummary()
    
    def callCMM(self):
        CMM.CMM()
        
    def callRefCell(self):
        JVfollowup.JVfollowup()
                
    def callDB(self):
        DB.DBapp()
        
        
        
root = Tk()
background_image=ImageTk.PhotoImage(file="background2.png")
w = background_image.width()
h = background_image.height()
root.geometry("%dx%d+0+0" % (w, h))
main_window=TheAnalyser(root)    
root.mainloop()    
    