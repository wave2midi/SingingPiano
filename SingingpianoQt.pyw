from os.path import dirname
from PySide2.QtCore import QObject, Slot, SIGNAL, Signal
from PySide2.QtWidgets import QMainWindow, QApplication
from PySide2.QtGui import QGuiApplication
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QUrl, QStringListModel, Qt
from PySide2.QtQml import QQmlEngine, QQmlApplicationEngine
from style import *
import sys
import os
import i18n
import threading
from singingpiano import *
from urllib.request import url2pathname
import locale


version="0.1.0beta"

def wave2MIDI(filepath,basicFreq,tempo,lim,pitchwheel):
    def _print(s,*args,**kwargs):
        WorkDict["outputBuffer"].append(s)
        outputbuffer.setProperty("value",1.0)
    print=_print
    print(i18n.t("generic.conversion.wave2midi.start"))
    inputfname,extension = os.path.splitext(url2pathname(filepath[8:]))
    if extension.lower() == ".wav":
        print(i18n.t("generic.conversion.read.wave"))
        progressbar.setProperty("indeterminate",False)
    
        PCM,framerate=wavefileReadUnpack(url2pathname(filepath[8:]),progressbarObject=progressbar)
        #print(f"长度：{patt.length}")
        progressbar.setProperty("value",0.0)
    
        print(i18n.t("generic.conversion.dft128.start"))
        DFTData=DFT128(PCM,framerate,basicFreq=int(basicFreq),progressbarObject=progressbar)
        print(i18n.t("generic.conversion.dft128.complete"))
    elif extension.lower() == ".etu":
        print(i18n.t("generic.conversion.read.dftdata"))
        with open(url2pathname(filepath[8:]),"rb") as DB:
            DFTBitStream = DB.read()
        DFTData = decodingDFTData(DFTBitStream)
    else:
        print(i18n.t("generic.conversion.failed.file_unsupported",extension=extension))
        enableButtons()
        return False
    print(i18n.t("generic.conversion.generate.midi.start"))
    patt,notec=NFTData2MIDI(DFTData,tempo=int(tempo),
        lim=lim,pitchwheel=pitchwheel,progressbarObject=progressbar)
    print(i18n.t("generic.conversion.generate.midi.complete",notecount=notec))
    progressbar.setProperty("value",0.0)
    progressbar.setProperty("indeterminate",True)
    patt.save(os.path.join(os.path.dirname(__file__),inputfname+".mid"))
    progressbar.setProperty("indeterminate",False)
    print(i18n.t("generic.conversion.wave2midi.complete"))
    enableButtons()
    return True

def wave2DFTData(filepath,basicFreq,tempo,lim,pitchwheel):
    def _print(s,*args,**kwargs):
        WorkDict["outputBuffer"].append(s)
        outputbuffer.setProperty("value",1.0)
    print=_print
    print(i18n.t("generic.conversion.wave2dftdata.start"))
    inputfname,extension = os.path.splitext(url2pathname(filepath[8:]))
    if not extension.lower() == ".wav":
        print(i18n.t("generic.conversion.failed.file_unsupported",extension=extension))
        return False
        enableButtons()
    #print("y")
    print(i18n.t("generic.conversion.read.wave"))
    progressbar.setProperty("indeterminate",False)
    
    PCM,framerate=wavefileReadUnpack(url2pathname(filepath[8:]),progressbarObject=progressbar)
    #print(f"长度：{patt.length}")
    progressbar.setProperty("value",0.0)
    print(i18n.t("generic.conversion.dft128.start"))
    DFTData=DFT128(PCM,framerate,basicFreq=int(basicFreq),progressbarObject=progressbar)
    print(i18n.t("generic.conversion.dft128.complete"))
    print(i18n.t("generic.conversion.generate.dftdata"))
    patt = encodingDFTData(DFTData)
    #print(f"音符数：{notec}")
    progressbar.setProperty("value",0.0)
    progressbar.setProperty("indeterminate",True)
    
    outputpath = os.path.join(os.path.dirname(__file__),inputfname+".etu")
    with open(outputpath, "wb") as outf:
        outf.write(patt)
    progressbar.setProperty("indeterminate",False)
    print(i18n.t("generic.conversion.wave2dftdata.complete"))
    enableButtons()
    return True
    
def encodingDFTData(DFTList):
    """version=0.1"""
    Compressed = b""
    def lim(number):
        if number >= 128:
            number = 127
        elif number < 0:
            number = 0
        return number
    for i in range(len(DFTList)):
        N_i=DFTList[i]
        D_i=b""
        for j in range(112):
            pos=j*8//7
            offset=j%7
            #n__1=N_i[j-1]
            n_0 =round(N_i[pos])
            n_1 =round(N_i[pos+1] if len(N_i) > pos+1 else 0)
            n_0=lim(n_0)
            n_1=lim(n_1)
            B = (n_0 >> offset) + (n_1 << (7-offset))
            D_i += bytes([B%256])
        Compressed += D_i
    return Compressed

def decodingDFTData(DFTData):
    """version=0.1"""
    DFTList = []
    if not len(DFTData)%112 == 0:
        print("Data corrupted .")
    DDList = [DFTData[k*112:(k+1)*112] for k in range(int(len(DFTData)/112))]
    for i in DDList:
        L_i=[]
        for j in range(128):
            pos=(j+1)*7//8
            offset=j%8
            #n__1=N_i[j-1]
            n__1 =i[pos-1]
            n_0 =i[pos] if len(i) > pos+1 else 0
            L_i.append(((n__1 >> (8-offset)) + (n_0 << offset))%128)
        DFTList.append(L_i)
    return DFTList





class Bridge(QObject):
    def __init__(self):
        super(Bridge, self).__init__()
        self.sfreqs = [440, 432, 415]

    @Slot(int, result=str)
    def getSF(self, i):
        return str(self.sfreqs[i])

    @Slot(str, result=str)
    def t(self, text, *args, **kwargs):
        return i18n.t(text, *args, **kwargs)


    @Slot(str,str,str,int,bool,result=bool)
    def wave2MIDIWithoutProgressbar(self,filepath,basicFreq,tempo,lim,pitchwheel):
        s = threading.Thread(target = wave2MIDI, args = (filepath,basicFreq,tempo,lim,pitchwheel))
        s.start()
        
    @Slot(str,str,str,int,bool,result=bool)
    def wave2DataWithoutProgressbar(self,filepath,basicFreq,tempo,lim,pitchwheel):
        s = threading.Thread(target = wave2DFTData, args = (filepath,basicFreq,tempo,lim,pitchwheel))
        s.start()
    @Slot(result=str)
    def getT(self):
        return "".join(["V",version," ",getTidrec("MnJS")])
    @Slot(result=str)
    def getBufferTextFull(self):
        return "\n".join(WorkDict["outputBuffer"])

# Multithread vars and locking
WorkDict={
    "progress":0.0,
    "status":"",            #"unpack","dft","midigen","complete"
    "outputBuffer":[]
}

def enableButtons():
    buttons.setProperty("enabled",True)
    


if __name__ == "__main__":
    print(locale.getdefaultlocale()[0])
    i18n.set('locale',locale.getdefaultlocale()[0])
    i18n.set('fallback',"en")
    try:
        i18n.load_path.append(os.path.join(dirname(__file__), 'languages'))
    except:
        pass
    
    APP = QGuiApplication(sys.argv)
    view = QQuickView()
    view.setTitle(i18n.t("generic.title.main"))
    engine = view.engine()
    engine.addImportPath(os.path.join(dirname(__file__), "uidef/imports"))
    print(engine.importPathList())
    bridge = Bridge()
    
    url = QUrl("uidef/Screen01.ui.qml")

    context = engine.rootContext()
    context.setContextProperty("con", bridge)
    view.setSource(url)
    view.setMinimumHeight(360)
    view.setMinimumWidth(480)
    # view.setMaximumHeight(view.height())
    # view.setMaximumWidth(view.width())
    view.setHeight(480)
    view.setWidth(640)

    progressbar = view.rootObject().findChild(QObject,"global").findChild(QObject,"ProgressBar")#
    progressbar.setProperty("value",0.0)
    outputbuffer = view.rootObject().findChild(QObject,"global").findChild(QObject,"output")
    outputbuffer.setProperty("text",i18n.t("generic.conversion.ready"))

    buttons = view.rootObject().findChild(QObject,"global").findChild(QObject,"buttons")
    #print(outputbuffer.property("text"))
    #outputbuffer.outputSignal=Signal(str)
    #outputbuffer.outputSignal.emit("text")
    
    view.show()
    
    APP.exec_()
    # print(9)
