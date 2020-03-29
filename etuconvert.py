import libs
import wave
from numpy import array
import struct
from tqdm import trange
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

if __name__ == "__main__":
    import sys
    _name=sys.argv[1]#input("Drag etu file into this window:")
    if _name[0]=='"' and _name[-1] == '"':
        _name=_name[1:-1]
    name=_name[:-4]
    
    with open(name+".etu","rb") as fetu:
        X=decodingDFTData(fetu.read())
    for i in range(len(X)):#trange(len(NFTData),dynamic_ncols=True,ascii=True,smoothing=1,mininterval=0.25,unit="ticks",unit_scale=False,unit_divisor=1024):
        for k in range(len(X[0])):
            this_n=(X[i][k]*32)**2
            X[i][k]=this_n
            #imi.append(this_n)
            #if this_n >= 128:notesOverFlow+=1  
    T=len(X)*0.05
    fs = 44100
    x=libs.myalgs.distft(array(X), fs, T, 0.05*2, 0.05)
    w= array([round(j/32) for j in x],dtype="int16")
    print(max(w),min(w),max(x),min(x))
    #B=b""
    #or i in trange(len(w),dynamic_ncols=True,ascii=True,smoothing=1,mininterval=0.25,unit="ticks",unit_scale=False,unit_divisor=1024):
        #B+= struct.pack("h",int(w[i]))
    W=wave.open(name+".etu.wav",mode='wb')
    W.setframerate(fs)
    W.setnchannels(1)
    W.setsampwidth(2)
    W.writeframes(w)
    input("Complete.")
