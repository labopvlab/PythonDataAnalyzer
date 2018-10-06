# -*- coding: utf-8 -*-
#! python3

from tkinter import filedialog, messagebox
import sqlite3



class mergingapp():
    def __init__(self, *args, **kwargs):        
        self.initUI()
    def initUI(self):
        #ask to load the main database
        try:
            pathtomain =filedialog.askopenfilenames(title="Please select the main Database .db file")[0]
            
            if pathtomain!="":
                if pathtomain[-3:]==".db":
                    self.db_conn=sqlite3.connect(pathtomain)
                    self.theCursor=self.db_conn.cursor()
                    print("connected to DB")
                    listTable = self.getTableNames() 
                else:
                    print("not correct file extension")
        except IndexError:
            print("you did not select a file") 
        
        
        #ask to select the DBs to be merged with the main
        checkedtocontinue=0
        try:
            pathstootherdbs = list(filedialog.askopenfilenames(title="Please select the other Databases .db file"))
        #    print(len(pathstootherdbs))
            #check integrity: do the two dbs have the same schema, same number of tables, same names, and same columns ? 
            #if no, stop and refuse the merge
        
            if pathstootherdbs!=[]:
                listofDbtoremove=[]
                for item in pathstootherdbs:
                    if item[-3:]==".db":
                        self.db_conn=sqlite3.connect(item)
                        self.theCursor=self.db_conn.cursor()
                        temptables = self.getTableNames() 
                        if (len(listTable) > len(temptables)):
                            print("Table is missing from non-primary database: %s" % item)
                            print("Database will NOT BE MERGED with the main database.")
                            listofDbtoremove.append(item)
                            continue
                    
                        if (len(listTable) < len(temptables)):
                            print("Extra table(s) in non-primary database: %s" % item)
                            print("TABLES that are NOT in main database will NOT be added.")
                    
                        if (listTable != temptables):
                            print("Tables do not match in non-primary database: %s" % item)
                            print("The database will NOT BE MERGED with the main database.")
                            listofDbtoremove.append(item)                
                            continue
                        checkedtocontinue=1
                        self.theCursor.close()
                        self.db_conn.close()
                    else:
                        print("not correct file extension")
            else:
                print("No databases to merge")
                checkedtocontinue=0
            for item in listofDbtoremove:
                pathstootherdbs.remove(item)
        #    print(len(pathstootherdbs))
        except IndexError:
            print("you did not select a file")     
        
        #do the ATTACH statement to connect to the main db and one of the selected (loop on the selected dbs)
        
        dbCount = 0                    # Variable to count the number of databases
        listDB = []                    # Variable to store the names of the databases
        
        if checkedtocontinue:
            self.db_conn=sqlite3.connect(pathtomain)
            self.theCursor=self.db_conn.cursor()
            for i in range(0,len(pathstootherdbs)):   
                self.theCursor.execute("ATTACH DATABASE ? as ? ;", (pathstootherdbs[i], 'db' + str(i)))
                listDB.append('db' + str(dbCount))
                dbCount += 1
                
            # Merge databases
            
            #check first the "easy tables" without foreign keys: Pcontact, substtype, Ncontact, PkAbsorber, electrode, recombjct, users,
            easytables=["environment","takencharacsetups","Pcontact", "substtype", "Ncontact", "PkAbsorber", "PkAbsorberMethod", "electrode", "recombjct", "users", "characsetups"]
        #    easytables=["Pcontact"]
#            self.theCursor.execute("SELECT contactstackP FROM Pcontact")
        #    print(('asgasga',) in self.theCursor.fetchall())
            for i in range(0, len(listDB)):
                for j in range(0, len(easytables)):
                    self.theCursor.execute("PRAGMA table_info(%s);" % str(easytables[j]))
                    temp = self.theCursor.fetchall()
                    numbcolumns=len(temp)-1
        #            print(numbcolumns)
                    columns = self.listToString(self.getColumnNames(easytables[j]))# get columns
        #            print(columns)
        #            print(easytables[j])
        #            print(listDB[i]) 
                    self.theCursor.execute("SELECT "+columns+" FROM "+listDB[i]+'.'+easytables[j] )
        #            dat=[(str(x[0]),str(x[1])) for x in self.theCursor.fetchall()]
                    dat=[]
                    for x in self.theCursor.fetchall():
                        strtemp="('"
                        for y in range(numbcolumns):
                            strtemp+=str(x[y])+"','"
                        strtemp=strtemp[:-2]+")"
                        dat.append(strtemp)
        #            print(dat)
                    for item in dat:
                        try:
                            self.theCursor.execute("INSERT INTO "+easytables[j]+"("+columns+") VALUES "+item)
                            self.db_conn.commit()
                        except:
        #                    print("exception")
                            pass
        
                  
            #then tripletop
            for db in listDB:
                
                ###################
                # merge the tripletop table
                self.theCursor.execute("SELECT topstack FROM tripletop")
                topstackdbmain = [x[0] for x in self.theCursor.fetchall()]
            #    print(topstackdbmain)
                self.theCursor.execute("SELECT topstack FROM "+db+"."+"tripletop")
                topstackdb1 = [x[0] for x in self.theCursor.fetchall()]
            #    print(topstackdb1)
                if topstackdb1!=[] and topstackdbmain != topstackdb1: #continue if something to add from db to main and if not everything is already in there (if they are different)
                    
            #        for item in topstackdb1:
            #            theCursor.execute("SELECT Pcontact.id FROM Pcontact, "+db+"."+"tripletop WHERE ")
            #            newPcontact_id=
            #            "INSERT INTO tripletop (topstack, Pcontact_id, Ncontact_id, PkAbsorber_id, electrode_id) VALUES (?,?,?,?,?)"
                    for item in topstackdb1: 
                        self.theCursor.execute("SELECT "+db+".Pcontact.contactstackP FROM "+db+".Pcontact, "+db+".tripletop WHERE "+db+".tripletop.Pcontact_id = "+db+".Pcontact.id AND "+db+".tripletop.topstack = '"+item+"'")
                        fromdb1 = self.theCursor.fetchone()[0]
            #            print(fromdb1)
                        self.theCursor.execute("SELECT id FROM Pcontact WHERE contactstackP = '"+fromdb1+"'")
                        Pcontactidmain = self.theCursor.fetchone()[0]
        #                print(Pcontactidmain)
                        self.theCursor.execute("SELECT "+db+".Ncontact.contactstackN FROM "+db+".Ncontact, "+db+".tripletop WHERE "+db+".tripletop.Ncontact_id = "+db+".Ncontact.id AND "+db+".tripletop.topstack = '"+item+"'")
                        fromdb1 = self.theCursor.fetchone()[0]
            #            print(fromdb1)
                        self.theCursor.execute("SELECT id FROM Ncontact WHERE contactstackN = '"+fromdb1+"'")
                        Ncontactidmain = self.theCursor.fetchone()[0]
        #                print(Ncontactidmain)
                        self.theCursor.execute("SELECT "+db+".PkAbsorber.absorbercomposition FROM "+db+".PkAbsorber, "+db+".tripletop WHERE "+db+".tripletop.PkAbsorber_id = "+db+".PkAbsorber.id AND "+db+".tripletop.topstack = '"+item+"'")
                        fromdb1 = self.theCursor.fetchone()[0]
            #            print(fromdb1)
                        self.theCursor.execute("SELECT id FROM PkAbsorber WHERE absorbercomposition = '"+fromdb1+"'")
                        PkAbsorberidmain = self.theCursor.fetchone()[0]
        #                print(PkAbsorberidmain)
                        self.theCursor.execute("SELECT "+db+".electrode.electrodestack FROM "+db+".electrode, "+db+".tripletop WHERE "+db+".tripletop.electrode_id = "+db+".electrode.id AND "+db+".tripletop.topstack = '"+item+"'")
                        fromdb1 = self.theCursor.fetchone()[0]
            #            print(fromdb1)
                        self.theCursor.execute("SELECT id FROM electrode WHERE electrodestack = '"+fromdb1+"'")
                        electrodestackidmain = self.theCursor.fetchone()[0]
        #                print(electrodestackidmain)
                        
                        self.theCursor.execute("INSERT INTO tripletop (topstack, Pcontact_id, Ncontact_id, PkAbsorber_id, electrode_id) VALUES (?,?,?,?,?)", 
                                          (item, Pcontactidmain, Ncontactidmain, PkAbsorberidmain, electrodestackidmain))
                self.db_conn.commit()         
                ###################
                # merge the batch table
                # complete if batchname does not exist 
                self.theCursor.execute("SELECT batchname FROM batch")
                namesmain = [x[0] for x in self.theCursor.fetchall()]
            #    print(topstackdbmain)
                self.theCursor.execute("SELECT batchname FROM "+db+"."+"batch")
                namesdb1 = [x[0] for x in self.theCursor.fetchall()]
            #    print(topstackdb1)
                if namesdb1!=[] and namesmain != namesdb1: #continue if something to add from db to main and if not everything is already in there (if they are different)
                    for item in namesdb1:
                        if item not in namesmain:
                            self.theCursor.execute("SELECT "+db+".batch.users_id, "+db+".batch.environment_id, "+db+".batch.takencharacsetups_id FROM "+db+".batch WHERE "+db+".batch.batchname = '"+item+"'")
                            data = self.theCursor.fetchall()
                            users_id=data[0][0]
                            environment_id=data[0][1]
                            takencharacsetups_id=data[0][2]
                            
                            #get info from db1 for corresponding ids in a list
        
                            self.theCursor.execute("SELECT "+db+".users.username FROM "+db+".users WHERE "+db+".users.id = "+str(users_id))
                            newusersid=self.theCursor.fetchone()[0]
                            self.theCursor.execute("SELECT id FROM users WHERE users.username = '"+newusersid+"'")
                            newusersid=self.theCursor.fetchone()[0]
                            
                            self.theCursor.execute("SELECT "+db+".takencharacsetups.takencharacsetupsname FROM "+db+".takencharacsetups WHERE "+db+".takencharacsetups.id = "+str(takencharacsetups_id))
                            newtakencharacsetupsid=self.theCursor.fetchone()[0]
                            self.theCursor.execute("SELECT id FROM takencharacsetups WHERE takencharacsetups.takencharacsetupsname = '"+newtakencharacsetupsid+"'")
                            newtakencharacsetupsid=self.theCursor.fetchone()[0]
                            
                            self.theCursor.execute("SELECT * FROM "+db+".environment WHERE "+db+".environment.id = "+str(environment_id))
                            newenvironmentid=self.theCursor.fetchall()[0]
                            self.theCursor.execute("SELECT id FROM environment WHERE environment.RHyellowroom = '"+str(newenvironmentid[1])+"' AND environment.RHMC162 = '"+str(newenvironmentid[2])+"' AND environment.Tempyellowroom = '"+str(newenvironmentid[3])+"' AND environment.Tempmc162 = '"+str(newenvironmentid[4])+"' AND environment.gloveboxsolvent = '"+str(newenvironmentid[5])+"' AND environment.solventGBwatervalue = '"+str(newenvironmentid[6])+"' AND environment.solventGBoxygenvalue = '"+str(newenvironmentid[7])+"' AND environment.evapGBwatervalue = '"+str(newenvironmentid[8])+"' AND environment.evapGBoxygenvalue = '"+str(newenvironmentid[9])+"' AND environment.commentenvir = '"+str(newenvironmentid[10])+"'")
                            newenvironmentid=self.theCursor.fetchone()[0]
                                                
                            #put everything together in maindb
                            self.theCursor.execute("SELECT batchname, topic, startdate, commentbatch FROM "+db+"."+"batch WHERE "+db+".batch.batchname = '"+item+"'")
                            datadb1 = list(self.theCursor.fetchall()[0])
                            
                            self.theCursor.execute("INSERT INTO batch (batchname, topic, startdate, commentbatch, users_id, environment_id, takencharacsetups_id) VALUES (?,?,?,?,?,?,?)", 
                                          (datadb1[0],datadb1[1],datadb1[2],datadb1[3],newusersid,newenvironmentid,newtakencharacsetupsid))
                self.db_conn.commit() 
                ################
                #merge samples 
                self.theCursor.execute("SELECT samplename FROM samples")
                namesmain = [x[0] for x in self.theCursor.fetchall()]
                self.theCursor.execute("SELECT samplename FROM "+db+"."+"samples")
                namesdb1 = [x[0] for x in self.theCursor.fetchall()]
                if namesdb1!=[] and namesmain != namesdb1: #continue if something to add from db to main and if not everything is already in there (if they are different)
                    for item in namesdb1:
                        if item not in namesmain:
                            self.theCursor.execute("SELECT "+db+".samples.tripletop_id, "+db+".samples.Pcontact_id, "+db+".samples.Ncontact_id, "+db+".samples.PkAbsorber_id, "+db+".samples.substtype_id, "+db+".samples.electrode_id, "+db+".samples.recombjct_id, "+db+".samples.batch_id FROM "+db+".samples WHERE "+db+".samples.samplename = '"+item+"'")
                            [tripletop_id,Pcontact_id,Ncontact_id,PkAbsorber_id,substtype_id,electrode_id,recombjct_id,batch_id] = theCursor.fetchall()[0]
                            
                            try:
                                self.theCursor.execute("SELECT "+db+".tripletop.topstack FROM "+db+".tripletop WHERE "+db+".tripletop.id = "+str(tripletop_id))
                                newtripletop_id=self.theCursor.fetchone()[0]
                                self.theCursor.execute("SELECT id FROM tripletop WHERE tripletop.topstack = '"+newtripletop_id+"'")
                                newtripletop_id=self.theCursor.fetchone()[0]
                            except:
                                newtripletop_id=tripletop_id
                            self.theCursor.execute("SELECT "+db+".Pcontact.contactstackP FROM "+db+".Pcontact WHERE "+db+".Pcontact.id = "+str(Pcontact_id))
                            newPcontact_id=self.theCursor.fetchone()[0]
                            self.theCursor.execute("SELECT id FROM Pcontact WHERE Pcontact.contactstackP = '"+newPcontact_id+"'")
                            newPcontact_id=self.theCursor.fetchone()[0]
                            self.theCursor.execute("SELECT "+db+".Ncontact.contactstackN FROM "+db+".Ncontact WHERE "+db+".Ncontact.id = "+str(Ncontact_id))
                            newNcontact_id=self.theCursor.fetchone()[0]
                            self.theCursor.execute("SELECT id FROM Ncontact WHERE Ncontact.contactstackN = '"+newNcontact_id+"'")
                            newNcontact_id=self.theCursor.fetchone()[0]
                            self.theCursor.execute("SELECT "+db+".PkAbsorber.absorbercomposition FROM "+db+".PkAbsorber WHERE "+db+".PkAbsorber.id = "+str(PkAbsorber_id))
                            newPkAbsorber_id=self.theCursor.fetchone()[0]
                            self.theCursor.execute("SELECT id FROM PkAbsorber WHERE PkAbsorber.absorbercomposition = '"+newPkAbsorber_id+"'")
                            newPkAbsorber_id=self.theCursor.fetchone()[0]
                            self.theCursor.execute("SELECT "+db+".substtype.substratetype FROM "+db+".substtype WHERE "+db+".substtype.id = "+str(substtype_id))
                            newsubsttype_id=self.theCursor.fetchone()[0]
                            self.theCursor.execute("SELECT id FROM substtype WHERE substtype.substratetype = '"+newsubsttype_id+"'")
                            newsubsttype_id=self.theCursor.fetchone()[0]
                            self.theCursor.execute("SELECT "+db+".electrode.electrodestack FROM "+db+".electrode WHERE "+db+".electrode.id = "+str(electrode_id))
                            newelectrode_id=self.theCursor.fetchone()[0]
                            self.theCursor.execute("SELECT id FROM electrode WHERE electrode.electrodestack = '"+newelectrode_id+"'")
                            newelectrode_id=self.theCursor.fetchone()[0]
                            self.theCursor.execute("SELECT "+db+".recombjct.recombjctstack FROM "+db+".recombjct WHERE "+db+".recombjct.id = "+str(recombjct_id))
                            newrecombjct_id=self.theCursor.fetchone()[0]
                            self.theCursor.execute("SELECT id FROM recombjct WHERE recombjct.recombjctstack = '"+newrecombjct_id+"'")
                            newrecombjct_id=self.theCursor.fetchone()[0]
                            self.theCursor.execute("SELECT "+db+".batch.batchname FROM "+db+".batch WHERE "+db+".batch.id = "+str(batch_id))
                            newbatch_id=self.theCursor.fetchone()[0]
                            self.theCursor.execute("SELECT id FROM batch WHERE batch.batchname = '"+newbatch_id+"'")
                            newbatch_id=self.theCursor.fetchone()[0]
                            
                            self.theCursor.execute("SELECT * FROM "+db+".samples WHERE "+db+".samples.samplename = '"+item+"'")
                            sampdat=self.theCursor.fetchall()[0]
                            
                            self.theCursor.execute("INSERT INTO samples (samplename,cellarchitecture,samplefullstack,polarity,bottomCellDBRef,commentsamples,tripletop_id,Pcontact_id,Ncontact_id,PkAbsorber_id,substtype_id,electrode_id,recombjct_id,batch_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                                          (sampdat[1],sampdat[2],sampdat[3],sampdat[4],sampdat[5],sampdat[6],newtripletop_id,newPcontact_id,newNcontact_id,newPkAbsorber_id,newsubsttype_id,newelectrode_id,newrecombjct_id,newbatch_id))
                self.db_conn.commit()     
                ################
                #merge cells
                self.theCursor.execute("SELECT cellname, samples_id, batch_id FROM "+db+"."+"cells")
        #        namesdb1=self.theCursor.fetchall()
                namesdb1 = [list(x) for x in self.theCursor.fetchall()]
                
                self.theCursor.execute("SELECT "+db+".samples.id, main.samples.id  FROM main.samples, "+db+".samples WHERE main.samples.samplename = "+db+".samples.samplename")
                dicsamplescorres={}
                listsamplesidcorrespondance=self.theCursor.fetchall()  
                for item in listsamplesidcorrespondance:
                    dicsamplescorres[str(item[0])]=item[1]
                self.theCursor.execute("SELECT "+db+".batch.id, main.batch.id  FROM main.batch, "+db+".batch WHERE main.batch.batchname = "+db+".batch.batchname")
                dicbatchcorres={}
                listbatchidcorrespondance=self.theCursor.fetchall()  
                for item in listbatchidcorrespondance:
                    dicbatchcorres[str(item[0])]=item[1]
        
                for item in namesdb1:
                    self.theCursor.execute("INSERT INTO cells (cellname,samples_id,batch_id) VALUES (?,?,?)", 
                                  (item[0], dicsamplescorres[str(item[1])],dicbatchcorres[str(item[2])]))
            
                
                self.db_conn.commit() 
                ################
                #merge eqemeas 
                self.theCursor.execute("SELECT EQEmeasnameDateTimeEQEJsc, samples_id, batch_id, cells_id FROM "+db+"."+"eqemeas")
                eqedat=[list(x) for x in self.theCursor.fetchall()]
        #        print(eqedat)
                if eqedat!=[]:
                    for item in eqedat:
                        self.theCursor.execute("SELECT batch.batchname, samples.samplename, cells.cellname FROM "+db+".samples, "+db+".batch,"+db+".cells WHERE "+db+".samples.id = "+str(item[1])+" AND "+db+".batch.id = "+str(item[2])+" AND "+db+".cells.id = "+str(item[3]))
                        db1names=self.theCursor.fetchall()[0]
        #                print(db1names)
                        self.theCursor.execute("SELECT batch.id, samples.id FROM samples, batch WHERE samples.samplename = '"+str(db1names[1])+"' AND batch.batchname = '"+str(db1names[0])+"'")
                        mainid=self.theCursor.fetchall()[0]
        #                print(mainid)
                        self.theCursor.execute("SELECT cells.id FROM cells, samples, batch WHERE samples.id = '"+str(mainid[1])+"' AND batch.id = '"+str(mainid[0])+"' AND cells.cellname = '"+str(db1names[2])+"'")
                        cellid=self.theCursor.fetchall()[0][0]
        #                print(item[0])
                        self.theCursor.execute("SELECT EQEmeasname,DateTimeEQE,integJsc,Eg,EgTauc,EgLn,Vbias,filter,LEDbias,linktofile,commenteqe  FROM "+db+".eqemeas WHERE "+db+".eqemeas.EQEmeasnameDateTimeEQEJsc = '"+str(item[0])+"'")
                        db1dat=self.theCursor.fetchall()[0]
        #                print(db1dat)
                        try:
                            self.theCursor.execute("INSERT INTO eqemeas (EQEmeasname,EQEmeasnameDateTimeEQEJsc,DateTimeEQE,integJsc,Eg,EgTauc,EgLn,Vbias,filter,LEDbias,linktofile,commenteqe,samples_id,batch_id,cells_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                                      (db1dat[0],str(item[0]),db1dat[1],db1dat[2],db1dat[3],db1dat[4],db1dat[5],db1dat[6],db1dat[7],db1dat[8],db1dat[9],db1dat[10],mainid[1],mainid[0],cellid))
                        except:
                            pass
                self.db_conn.commit()         
                ################
                #merge JVmeas
                self.theCursor.execute("SELECT linktorawdata FROM "+db+"."+"JVmeas")
                jvuniquesdb1=self.theCursor.fetchall()
                self.theCursor.execute("SELECT linktorawdata FROM JVmeas")
                jvuniquesmain=self.theCursor.fetchall()
        #        print(jvuniquesdb1)
                if jvuniquesdb1!=[] and jvuniquesdb1!=jvuniquesmain:
                    for item in jvuniquesdb1:
                        if item not in jvuniquesmain:
                            self.theCursor.execute("SELECT samples_id,batch_id FROM "+db+".JVmeas WHERE "+db+".JVmeas.linktorawdata = '"+str(item[0])+"'")
                            db1ids=self.theCursor.fetchall()[0]
                            self.theCursor.execute("SELECT samples.samplename,batch.batchname FROM "+db+".batch,"+db+".samples WHERE "+db+".samples.id = "+str(db1ids[0])+" AND "+db+".batch.id = "+str(db1ids[1]))
                            db1names=self.theCursor.fetchall()[0]
                            self.theCursor.execute("SELECT samples.id,batch.id FROM batch,samples WHERE samples.samplename = '"+str(db1names[0])+"' AND batch.batchname = '"+str(db1names[1])+"'")
                            mainids=self.theCursor.fetchall()[0]
        #                    print(mainids)
                            
                            self.theCursor.execute("SELECT cells_id FROM "+db+".JVmeas WHERE "+db+".JVmeas.linktorawdata = '"+str(item[0])+"'")
                            db1cellid=self.theCursor.fetchall()[0][0]
        #                    print(db1cellid)
                            self.theCursor.execute("SELECT cells.cellname FROM "+db+".cells WHERE "+db+".cells.id = "+str(db1cellid))
                            db1cellname=self.theCursor.fetchall()[0][0]
        #                    print(db1cellname)
                            self.theCursor.execute("SELECT cells.id FROM cells WHERE cells.batch_id = "+str(mainids[1])+" AND cells.samples_id = "+str(mainids[0])+" AND cells.cellname = '"+str(db1cellname)+"'")
                            maincellid=self.theCursor.fetchall()[0][0]
        #                    print(maincellid)
                            
                            self.theCursor.execute("SELECT * FROM "+db+".JVmeas WHERE "+db+".JVmeas.linktorawdata = '"+str(item[0])+"'")
                            alljvdb1=list(self.theCursor.fetchall()[0])[1:]
        #                    print(alljvdb1)
                            alljvdb1[-1]=maincellid
                            alljvdb1[-2]=mainids[1]
                            alljvdb1[-3]=mainids[0]
                            try:
                                self.theCursor.execute("INSERT INTO JVmeas (DateTimeJV,Eff,Voc,Jsc,FF,Vmpp,Jmpp,Pmpp,Roc,Rsc,ScanDirect,Delay,IntegTime,CellArea,Vstart,Vend,Setup,NbPoints,ImaxComp,Isenserange,Operator,GroupJV,IlluminationIntensity,commentJV,linktorawdata,samples_id,batch_id,cells_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                                          tuple(alljvdb1))
                            except:
                                pass
                self.db_conn.commit()             
                ################
                #merge MPPmeas
                self.theCursor.execute("SELECT linktorawdata FROM "+db+"."+"MPPmeas")
                jvuniquesdb1=self.theCursor.fetchall()
                self.theCursor.execute("SELECT linktorawdata FROM MPPmeas")
                jvuniquesmain=self.theCursor.fetchall()
        #        print(jvuniquesdb1)
                if jvuniquesdb1!=[] and jvuniquesdb1!=jvuniquesmain:
                    for item in jvuniquesdb1:
                        if item not in jvuniquesmain:
                            self.theCursor.execute("SELECT samples_id,batch_id FROM "+db+".MPPmeas WHERE "+db+".MPPmeas.linktorawdata = '"+str(item[0])+"'")
                            db1ids=self.theCursor.fetchall()[0]
                            self.theCursor.execute("SELECT samples.samplename,batch.batchname FROM "+db+".batch,"+db+".samples WHERE "+db+".samples.id = "+str(db1ids[0])+" AND "+db+".batch.id = "+str(db1ids[1]))
                            db1names=self.theCursor.fetchall()[0]
                            self.theCursor.execute("SELECT samples.id,batch.id FROM batch,samples WHERE samples.samplename = '"+str(db1names[0])+"' AND batch.batchname = '"+str(db1names[1])+"'")
                            mainids=self.theCursor.fetchall()[0]
        #                    print(mainids)
                            
                            self.theCursor.execute("SELECT cells_id FROM "+db+".MPPmeas WHERE "+db+".MPPmeas.linktorawdata = '"+str(item[0])+"'")
                            db1cellid=self.theCursor.fetchall()[0][0]
        #                    print(db1cellid)
                            self.theCursor.execute("SELECT cells.cellname FROM "+db+".cells WHERE "+db+".cells.id = "+str(db1cellid))
                            db1cellname=self.theCursor.fetchall()[0][0]
        #                    print(db1cellname)
                            self.theCursor.execute("SELECT cells.id FROM cells WHERE cells.batch_id = "+str(mainids[1])+" AND cells.samples_id = "+str(mainids[0])+" AND cells.cellname = '"+str(db1cellname)+"'")
                            maincellid=self.theCursor.fetchall()[0][0]
        #                    print(maincellid)
                            
                            self.theCursor.execute("SELECT * FROM "+db+".MPPmeas WHERE "+db+".MPPmeas.linktorawdata = '"+str(item[0])+"'")
                            alljvdb1=list(self.theCursor.fetchall()[0])[1:]
        #                    print(alljvdb1)
                            alljvdb1[-1]=maincellid
                            alljvdb1[-2]=mainids[1]
                            alljvdb1[-3]=mainids[0]
                            try:
                                self.theCursor.execute("INSERT INTO MPPmeas (DateTimeMPP,TrackingAlgo,TrackingDuration,Vstart,Vstep,CellArea,Operator,PowerEnd,PowerAvg,commentmpp,linktorawdata,samples_id,batch_id,cells_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                                          tuple(alljvdb1))
                            except:
                                pass
            
            
            self.db_conn.commit()                    # commit the changes
            self.theCursor.close()
            self.db_conn.close()
            print("merged and disconnected")
            messagebox.showinfo("", "merged and disconnected")
            

#the following function are inspired from an SQLite Merge Script written by Charles Duso, in 2016
        
    def getTableNames(self):
        self.theCursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        temp = self.theCursor.fetchall()
        tables = []
        for i in range(0, len(temp)):
            tables.append(temp[i][0])
        return tables
    def listToString(self, listObj ):
        listString = ""
        for i in range(0, len(listObj)):
            if (i == (len(listObj) - 1)):
                listString = listString + listObj[i]
            else:
                listString = listString + listObj[i] + ", "
        return listString
    def getColumnNames(self, tableName ):
        self.theCursor.execute("PRAGMA table_info(%s);" % str(tableName))
        temp = self.theCursor.fetchall()
        columns = []
        for i in range(0, len(temp)):
            if (("id" in temp[i][1]) | ("ID" in temp[i][1])):
                continue
            else:
                columns.append(temp[i][1])
        return columns
        
        
        
###############################################################################        
if __name__ == '__main__':
    
    app = mergingapp()       




 