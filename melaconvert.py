import libs
import wave
from numpy import array,log,e,sqrt
import struct
from tqdm import trange

if __name__ == "__main__":
    import sys
    _name=sys.argv[1]
    if _name[0]=='"' and _name[-1] == '"':
        _name=_name[1:-1]
    name=_name[:-5]
    
    with open(name+".mela","rb") as fetu:
        X, BasicFreq, NFOffset, TicksPerSecond, version = libs.melacodec.decode(fetu.read())
    ticklength=1/TicksPerSecond
    if version == [1,0,0]: 
        def dataConvert(x):return (x*32*256)**2
    elif version == [1,0,1]:
        c = 16.5
        def dataConvert(x):return e**(x*c)

    freqtable = libs.const.pitch
    for i in range(len(X)):
        for k in range(len(X[0])):
            f = freqtable[k]*BasicFreq/440
            this_n = dataConvert(X[i][k])*sqrt(f)/100
            X[i][k] = this_n 
    T=len(X)*ticklength
    fs = 44100
    x=libs.myalgs.distft(array(X), fs, T, ticklength*2, ticklength,basicFreq=BasicFreq)
    def lim(x):
        if x < -32768:return -32768
        elif x >= 32768: return 32767
        else: return x

    w= array([lim(round(j/4)) for j in x],dtype="int16")
    print(max(w),min(w),max(x),min(x))
    #B=b""
    #or i in trange(len(w),dynamic_ncols=True,ascii=True,smoothing=1,mininterval=0.25,unit="ticks",unit_scale=False,unit_divisor=1024):
        #B+= struct.pack("h",int(w[i]))
    W=wave.open(name+".mela.wav",mode='wb')
    W.setframerate(fs)
    W.setnchannels(1)
    W.setsampwidth(2)
    W.writeframes(w)
    input("Complete.")
