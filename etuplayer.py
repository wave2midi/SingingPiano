import libs
import wave
from numpy import array
import struct
from tqdm import trange,tqdm
import pyaudio
import numpy
import scipy.signal
from threading import Thread
import time
def decodingDFTData(DFTData):
    """version=0.1"""
    DFTList = []
    if not len(DFTData)%112 == 0:
        print("Data corrupted .")
    DDList = [DFTData[k*112:(k+1)*112] for k in range(int(len(DFTData)/112))]
    for i in DDList:
        L_i=[]
        for j in range(128):
            if j<16:#filtering low-band noise (f<20hz), used for spectrogram data obtained by STFT with ticklength=0.05 and windowlength=0.1
                L_i.append(0)
                continue
            pos=(j+1)*7//8
            offset=j%8
            #n__1=N_i[j-1]
            n__1 =i[pos-1]
            n_0 =i[pos] if len(i) > pos+1 else 0
            L_i.append(((n__1 >> (8-offset)) + (n_0 << offset))%128)
        DFTList.append(L_i)
    return DFTList


def realtime_distft(stream, framearray, X, fs, T, framesz, hop, sync):
    x = numpy.zeros(int(T*fs))
    framesamp = int(framesz*fs)#X.shape[1]
    hopsamp = int(hop*fs)
    w = scipy.signal.windows.gaussian(framesamp,hopsamp*0.4)#,sym=False)
    hopsamp = int(hop*fs)
    lx=(len(x)-framesamp)
    for n,i in enumerate(range(0, lx, hopsamp)):#t,dynamic_ncols=True,ascii=True,smoothing=1,mininterval=0.25,unit="ticks",unit_scale=False,unit_divisor=1024)):
        x[i:i+framesamp] += w*numpy.real(numpy.array(libs.mydft.idft128(tuple(X[n]) if len(X)>n else tuple(numpy.zeros(128)),fs,440,framesamp,i)))
        if not i == 0:
            framearray[i-framesamp:i] = array([-1 if -1>=j else 1 if 1<=j else j for j in array(x[i-framesamp:i])/16/65536]).astype("float32")
            sync[0] = i+hopsamp-framesamp
    sync[0] = float("inf")
    #return x
def realtime_streamwrite(stream, framearray, fs, T, framesz, hop, sync):
    #framearray = numpy.zeros(int(T*fs),dtype="int16")
    framesamp = int(framesz*fs)
    hopsamp = int(hop*fs)
    i = 0
    i_terminal = len(framearray)-hopsamp
    i_step = hopsamp
    pbar = tqdm(bar_format="{l_bar}{bar}|{n_fmt}/{total_fmt}{unit}{postfix}|",total = int(T),dynamic_ncols=True,ascii=True,smoothing=1,desc="Playing Progress",mininterval=0.25,unit="s",unit_scale=0)
    try:
        while i<i_terminal:
            samp = framearray[i:i+hopsamp*4]
            if sync[0]>=i:
                #print(samp)
                pbar.update(round(i_step/fs))
                stream.write(samp)
                i = i + i_step
            else:
                time.sleep(hop)
                continue
    except Exception as e:
        print(repr(e))
        input()
    finally:
        stream.close()
if __name__ == "__main__":
    import sys
    _name=sys.argv[1]#input("Drag etu file into this window:")
    if _name[0]=='"' and _name[-1] == '"':
        _name=_name[1:-1]
    name=_name[:-4]
    ticklength=0.05
    with open(name+".etu","rb") as fetu:
        X=decodingDFTData(fetu.read())
    for i in range(len(X)):#trange(len(NFTData),dynamic_ncols=True,ascii=True,smoothing=1,mininterval=0.25,unit="ticks",unit_scale=False,unit_divisor=1024):
        for k in range(len(X[0])):
            this_n=(X[i][k]*32)**2
            X[i][k]=this_n
            #imi.append(this_n)
            #if this_n >= 128:notesOverFlow+=1  
    T=len(X)*ticklength
    fs = 48000
    stream = pyaudio.PyAudio().open(format=pyaudio.paFloat32,channels=1,rate=fs,output=True)
    framearray = numpy.zeros(int(T*fs),dtype="float32")
    sync = [0]
    buffertime = 1.00 #seconds
    t1 = Thread(target=realtime_streamwrite,args=(stream,framearray, fs, T, ticklength*2, buffertime, sync))
    t2 = Thread(target=realtime_distft,args=(stream,framearray,array(X), fs, T, ticklength*2, ticklength, sync))
    t1.start()
    t2.start()
    #x=libs.myalgs.distft(array(X), fs, T, ticklength*2, ticklength)
    #w= array([round(j/64) for j in x],dtype="int16")
    #
    #stream.write(w)
    print("Start Playing...\n")
