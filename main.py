#===============================================================================
# Programm which displays navigation data from the apt.dat file
#===============================================================================

import lib.conf

import os
import zipfile
import math
import time
import Tkinter as tk

#-------------------------------------------------------------- global variables
# gloabl var for the folder for the navdata
# the same folder is also used for downloaded files
g_dataFolder        = "data"

# for the update a configuration file is needed
g_confFile          = "%s/xp_airports.conf" % g_dataFolder

#------------------------------------------------------------------ Navaid types
"""
dic_rtype: is used to translate the technical key of the navdata to text
"""
dic_rtype = {
            "2":"NDB",
            "3":"VOR",
            "4":"LOC/ILS",
            "5":"LOC",
            "6":"GS/ILS",
            "7":"OM",
            "8":"MM",
            "9":"IM",
            "12":"DME/ILS",
            "13":"DME"}

"""
sup_rtype: supported rtypes
It is used to filter the updated navdata files. Unused entries are deleted
after the download and extraction of the file
"""
sup_rtype = [2,3,4,5,6,12,13]


#------------------------------------------------------------ load configuration
"""
The conf file is loaded and parsed by using the Conf Class
"""
conf = lib.conf.Conf()
conf.addFile(g_confFile)
conf.loadFiles()

# Global Variable for the update process
xpa_update = conf.data["confvar"]["xpa_update"]

def getNavAids(navDat,search,sindex,rowt=[]):    
    """
    Allows to search different navaids in the navigation data file. 
    @param navDat: The content of the navigation data file
    @type navDat: array
    @param search: The search phrase
    @type search: string
    @param sindex: 
    @param rowt: 
    
    """
    navAids = []
    
    for l in navDat:
        navAid = l.strip().split()
        if len(navAid)<=10:
            navAid.append("")
        if len(navAid)>8 and int(navAid[0]) in rowt and navAid[sindex].startswith(search):
            #print "%s:%s:%s" % (navAid[0].strip(),len(navAid),navAid[7])
            if int(navAid[0]) in [2,3]:
                exp = [
                   dic_rtype[navAid[0].strip()],
                   "%s.%s" % (navAid[4][:3],navAid[4][3:]),
                   navAid[7],
                   "",
                   "",
                   navAid[8]]
            elif int(navAid[0]) in [4,5]:
                
                exp = [
                   dic_rtype[navAid[0].strip()],
                   "%s.%s" % (navAid[4][:3],navAid[4][3:]),
                   navAid[7],
                   navAid[6].split(".")[0],
                   navAid[9],
                   navAid[10]]
            elif int(navAid[0]) in [6]:
                exp = [
                   dic_rtype[navAid[0].strip()],
                   "%s.%s" % (navAid[4][:3],navAid[4][3:]),
                   navAid[7],
                   "%s/%s" % (navAid[6][3:6],navAid[6][:3]),
                   navAid[9],
                   navAid[10]]
            else:
                exp = [
                   dic_rtype[navAid[0].strip()],
                   "%s.%s" % (navAid[4][:3],navAid[4][3:]),
                   navAid[7],
                   "",
                   navAid[9],
                   navAid[10]]
            navAids.append(exp)
    return navAids
    

#--------------------------------------------------------------- load file url
def loadData(fileUrl):
    """
    Function loads a file by using the urllib
    @param fileUrl: the URL to load the file
    @return: the path to the downloaded file 
    """
    import urllib
    # load the file with the url of the current apt.dat 
    pfname = "%s/%s" % (g_dataFolder,fileUrl.split("/")[-1])
    webFile = urllib.urlopen(fileUrl)
    meta = webFile.info()
    fileSize = int(meta.getheaders("Content-Length")[0])
    mainApp.printUpdateStatus( "Download: %s (%s Bytes)" % (fileUrl.split("/")[-1],fileSize))
    dl = 0
    block = 8192
    prozentLastOutput = 0
    localFile = open(pfname,"wb")
    while True:
        buffer = webFile.read(block)
        if not buffer:
            break
        localFile.write(buffer)
        dl = float(dl) + float(len(buffer))
        prozent = math.floor(dl*100. / fileSize)
        if (prozent - prozentLastOutput) >= 5:
            mainApp.printUpdateStatus( "Status: %s Prozent" % prozent )
            prozentLastOutput = prozent
    webFile.close()
    localFile.close()
    return pfname

#--------------------------------------------------- extracts files from the zip
def printUpdateStatus(t):
    mainApp.printUpdateStatus(t)
    
def extractData(pfname,fileName,extractedRows):
    mainApp.printUpdateStatus( "Extract: %s" % fileName )
    
    xpaArchive = zipfile.ZipFile(pfname)
    # just the important rows
    # defined over the row codes
    targetFile = "%s/%s" % (g_dataFolder,fileName)
    navDat = xpaArchive.open(fileName,"r")
    targetObj = open(targetFile,"w")
    for l in navDat:
        navAid = l.strip().split()
        if len(l)>8 and int(navAid[0]) in extractedRows:
            targetObj.write("%s\n" % l.strip())
    targetObj.close()
    navDat.close()
    xpaArchive.close()
    mainApp.printUpdateStatus( "Exctract %s ready" % fileName )
    
    
def updateData(event=""):   
    """
    Function which updates the navigation data
    """ 
    # Update xpa_update
    loc_xpa_file = loadData(xpa_update)
    mainApp.printUpdateStatus("Start with Update")
    xpaconf = lib.conf.Conf()
    xpaconf.addFile(loc_xpa_file)
    xpaconf.loadFiles()
    
    xpa_updateUrl  = xpaconf.data["confvar"]["updateUrl"]
    xpa_fname = xpa_updateUrl.split("/")[-1]
    xpa_pfname = "%s/%s" % (g_dataFolder,xpa_fname)
    
    if not os.path.exists(xpa_pfname):
        xpa_pfname = loadData(xpa_updateUrl)
        if not "AptNavVers" in conf.data["conflist"]:
            conf.data["conflist"]["AptNavVers"] = []
        if not xpa_pfname in conf.data["conflist"]["AptNavVers"]:
            conf.data["conflist"]["AptNavVers"].append(xpa_pfname)
            conf.data["confvar"]["CurrentFile"] = xpa_pfname
            conf.data["confvar"]["lastUpdate"] = time.time()
            conf.writeConf(g_confFile)
    extractData(xpa_pfname,"earth_nav.dat",[2,3,4,5,6,12,13])
    extractData(xpa_pfname,"apt.dat",[1,16,17,100,101,102,50,51,52,53,54,55,56])    

#-------------------------------------------------------------- Programmschritte

        
#xpaArchive = zipfile.ZipFile(xpa_pfname)

#navDat = xpaArchive.open("earth_nav.dat","r")
#extractData(xpa_pfname,"earth_nav.dat",[2,3,4,5,6,12,13])
#extractData(xpa_pfname,"apt.dat",[1,16,17,100,101,102,50,51,52,53,54,55,56])
#navDat = open("%s/earth_nav.dat" % g_dataFolder,"r")
#navAids = getNavAids(navDat,"EDDH",range(0,14))
#navDat.close()

#for l in navAids:
#    print l

class XpaGui:
    import lib.multilb
    def __init__(self,parent):
        #--------------------------------------------------------- search fields
        self.inputArea = tk.Frame(parent,borderwidth=1)
        self.inputArea.pack(fill=tk.X,padx=10,pady=10)
        self.icaoFieldLabel = tk.Label(self.inputArea,text="ICAO Code: ")
        self.icaoFieldLabel.grid(row=0,column=0)        
        self.icaoField = tk.Entry(self.inputArea,width=6)
        self.icaoField.grid(row=0,column=1)
        self.identFieldLabel = tk.Label(self.inputArea,text="Identifier: ")
        self.identFieldLabel.grid(row=0,column=2)
        self.identField = tk.Entry(self.inputArea,width=6)
        self.identField.grid(row=0,column=3)
        self.searchMode = "icao"    # icao or ident Reference to the search function
        #--------------------------------------------------------- NavAid Output
        self.outputArea1 = tk.Frame(parent)
        self.outputArea1.pack()
        self.mlb = lib.multilb.MultiListbox(self.outputArea1,(
                        ("Type",10),
                        ("Freq.",8),
                        ("Ident",10),
                        ("LOC/GS",10),
                        ("Rwy",8),
                        ("Name",20),))
        self.mlb.pack(expand=tk.YES,fill=tk.BOTH)
        self.icaoField.bind("<KeyRelease>", self.icaoSearch)
        self.identField.bind("<KeyRelease>", self.identSearch)
        #--------------------------------------------------------- NavAid Filter
        self.rowtypes = []
        self.filterArea1 = tk.Frame(parent,relief=tk.GROOVE,borderwidth=2)
        self.cfilter = {}
        rowv = 0
        colv = 0
        maxcol = 4
        # Rowtypes to filter
        rowtypes = sup_rtype
        for k,v in dic_rtype.items():
            if not int(k) in rowtypes:
                continue
            self.cfilter[k] = {}
            self.cfilter[k]["val"] = tk.IntVar()
            self.cfilter[k]["box"] = tk.Checkbutton(
                               self.filterArea1,
                               text = v,
                               variable=self.cfilter[k]["val"],
                               state=tk.NORMAL,
                               command=self.search,
                               onvalue=int(k),
                               offvalue=0)
            self.cfilter[k]["box"].grid(row=rowv,column=colv,sticky=tk.W)
            #self.cfilter[k]["box"].bind("<ButtonRelease-1>", self.search)
            self.cfilter[k]["box"].select()
            colv += 1
            if colv >= maxcol:
                colv = 0
                rowv += 1
        self.filterArea1.pack(fill=tk.X,pady=10)

        #self.table1 = TkScrollTabelle(self.outputArea1,16,8,80)
#        self.buttomArea = tk.Frame(parent)
#        self.buttomArea.pack(fill=tk.X)
#        self.updateButton = tk.Button(self.buttomArea,text="Update NavData")
#        self.updateButton.grid(row=0,column=0)
#        self.updateStatus = tk.Text(self.buttomArea,width=40,height=20)
#        self.updateStatus.grid(row=0,column=1)
#        self.updateButton.bind("<Button-1>", updateData)
        #self.messageArea = tk.Frame(parent,relief=tk.GROOVE,borderwidth=2)
        #tk.Label(self.messageArea,text="Status",height=10).pack(side=tk.LEFT)
        #self.messageArea.pack(side=tk.LEFT,padx=10,pady=10)
        
    def getRowtypes(self):
        self.rowtypes = []
        for k,v in self.cfilter.items():
            rt = v["val"].get()
            if rt in sup_rtype:
                self.rowtypes.append(rt)
        return self.rowtypes
            
        
    def icaoSearch(self,event=0):
        self.searchMode = "icao"
        icao = self.icaoField.get().upper()
        self.identField.delete(0, tk.END)
        self.icaoField.delete(0, tk.END)
        self.icaoField.insert(0, icao)
        if len(icao)>4:
            icao = icao[:4]
        elif len(icao)==4:
            navDat = open("%s/earth_nav.dat" % g_dataFolder,"r")
            navAids = getNavAids(navDat,icao,8,self.getRowtypes())
            navDat.close()
            self.mlb.delete(0, tk.END)
            for n in navAids:
                self.mlb.insert(tk.END,n)
        elif len(icao)<4:
            self.mlb.delete(0, tk.END)
        
        
    def identSearch(self,event=0):
        self.searchMode = "ident"
        ident = self.identField.get().upper()
        self.identField.delete(0, tk.END)
        self.icaoField.delete(0, tk.END)
        self.identField.insert(0, ident)
        if len(ident)>1:
            navDat = open("%s/earth_nav.dat" % g_dataFolder,"r")
            navAids = getNavAids(navDat,ident,7,self.getRowtypes())
            navDat.close()
            self.mlb.delete(0, tk.END)
            for n in navAids:
                self.mlb.insert(tk.END,n)
                
    def search(self,event=0):
        if self.searchMode == "ident":
            return self.identSearch(event)
        else:
            return self.icaoSearch(event)
        
                
    def printUpdateStatus(self,t):
        #self.updateStatus.delete(0)
        self.updateStatus.insert(tk.END, t)

        
        


                
root = tk.Tk()
root.title("XP-Airports")
root.minsize(400, 250)
mainApp = XpaGui(root)
root.mainloop()
    




