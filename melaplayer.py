import libs
import wave
from numpy import array,log2
import struct
from tqdm import trange,tqdm
import pyaudio
import numpy
import scipy.signal
from threading import Thread
import time


def realtime_distft(stream, framearray, X, fs, T, framesz, hop, sync,BasicFreq):
    x = numpy.zeros(int(T*fs))
    framesamp = int(framesz*fs)#X.shape[1]
    hopsamp = int(hop*fs)
    w = scipy.signal.windows.gaussian(framesamp,hopsamp*0.5)#,sym=False)#0.5#scipy.signal.windows.bartlett(framesamp)
    hopsamp = int(hop*fs)
    lx=(len(x)-framesamp)
    for n,i in enumerate(range(0, lx, hopsamp)):#t,dynamic_ncols=True,ascii=True,smoothing=1,mininterval=0.25,unit="ticks",unit_scale=False,unit_divisor=1024)):
        x[i:i+framesamp] += w*numpy.real(numpy.array(libs.mydft.idft128(tuple(X[n]) if len(X)>n else tuple(numpy.zeros(128)),fs,BasicFreq,framesamp,i)))
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
    i_terminal = len(framearray)#-hopsamp
    i_step = hopsamp
    pbar = tqdm(bar_format="{l_bar}{bar}|{n_fmt}/{total_fmt}{unit}{postfix}|",total = int(T),dynamic_ncols=True,ascii=True,smoothing=1,desc="Playing Progress",mininterval=0.25,unit="s",unit_scale=0)
    
    try:
        stream.start_stream()
        while 1:
            samp = framearray[i:i+hopsamp*4]
            if not len(samp):break
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
        print(stream.get_output_latency())
        stream.stop_stream()
        stream.close()
if __name__ == "__main__":
    import sys
    _name=sys.argv[1]#input("Drag etu file into this window:")
    if _name[0]=='"' and _name[-1] == '"':
        _name=_name[1:-1]
    name=_name[:-5]
    
    with open(name+".mela","rb") as fetu:
        X, BasicFreq, NFOffset, TicksPerSecond=libs.melacodec.decode(fetu.read())
    ticklength=1/TicksPerSecond
    for i in range(len(X)):#trange(len(NFTData),dynamic_ncols=True,ascii=True,smoothing=1,mininterval=0.25,unit="ticks",unit_scale=False,unit_divisor=1024):
        for k in range(len(X[0])):
            #freq = libs.const.pitch[k]*BasicFreq/440
            this_n=(X[i][k]*32*256)**2#*log2(freq/8)/3#numpy.sqrt(freq/440)#
            X[i][k]=this_n
            #imi.append(this_n)
            #if this_n >= 128:notesOverFlow+=1  
    T=len(X)*ticklength
    fs = 48000
    stream = pyaudio.PyAudio().open(format=pyaudio.paFloat32,channels=1,rate=fs,output=True)
    framearray = numpy.zeros(int(T*fs),dtype="float32")
    sync = [0]
    buffertime = 1.0 #seconds
    amp = 2 #2
    t1 = Thread(target=realtime_streamwrite,args=(stream,framearray, fs, T, ticklength*amp, buffertime, sync))
    t2 = Thread(target=realtime_distft,args=(stream,framearray,array(X), fs, T, ticklength*amp, ticklength, sync,BasicFreq))
    t1.start()
    t2.start()
    #x=libs.myalgs.distft(array(X), fs, T, ticklength*2, ticklength)
    #w= array([round(j/64) for j in x],dtype="int16")
    #
    #stream.write(w)
    print(f"""Freq.={BasicFreq}\tTick Length={ticklength}\tTicks:{len(X)}""")
    print("Start Playing...\n")
