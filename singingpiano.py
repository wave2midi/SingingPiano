import locale
import libs
modulever='1.3.1.0'
date='2020/3/19'
M_OICQ=str(3080968787)

import sys,os
import math
#from tqdm import trange


    






try:
    import mido
    #from pylab import *
    from math import sqrt
    import wave 
    import struct
    from numpy import zeros,array,frombuffer,shape,log
    import scipy.io.wavfile
except:
    print("lack_of_dependencies")
    input()
    exit()


def wavefileReadUnpack(filename,channelLR="",progressbarObject=None):
    try:
        wavefile = open(filename, 'r') # open for writing
    except IOError as e:
        print("file_doesntexist")
        print(e)
        return None,None
    framerate,wavarr = scipy.io.wavfile.read(filename)
    if len(shape(wavarr))!=1:
        return wavarr.sum(axis=1)/2,framerate  
    else: 
        return array(wavarr),framerate

def wavefileReadUnpack_Obsolete(filename,channelLR="",progressbarObject=None):
    try:
        wavefile = wave.open(filename, 'r') # open for writing
    except IOError as e:
        print("file_doesntexist")
        print(e)
        return None,None
    #nchannels = wavefile.getnchannels()  
    sample_width = wavefile.getsampwidth()  
    framerate = wavefile.getframerate()  
    numframes = wavefile.getnframes()  
    y = zeros(numframes,dtype="float16")
    if sample_width == 2:
        packtype="h"
    elif sample_width == 4:
        packtype="l"
    else:
        print("Unsupported Wave File (Sample Width).")
        input()
        raise ValueError
    for i in range(numframes):#trange(numframes,dynamic_ncols=True,ascii=True,smoothing=1,mininterval=0.25,unit="*4B",unit_scale=True,unit_divisor=1024):  
        #if i%4==0:
            if i%int((numframes/200.0)+0.5) == 0 and not progressbarObject==None:#progress display for gui
                #print(column,'\t',int(i/(numframes/100.0)+0.5),'%')
                progressbarObject.setProperty("value",int(i/(numframes/100.0)+0.5)/100.0)
            j=i
            val = wavefile.readframes(1)
            if channelLR == "":
                left = val[0:sample_width]
                right = val[sample_width:2*sample_width]
                y[j]=round((struct.unpack(packtype, left )[0]+struct.unpack(packtype, right )[0] )/2)
            elif channelLR == "L":
                left = val[0:sample_width]
                y[j]=round((struct.unpack(packtype, left )[0] )/2)
            elif channelLR == "R":
                right = val[sample_width:2*sample_width]
                y[j]=round((struct.unpack(packtype, right )[0] )/2)            
    wavefile.close()  
    if progressbarObject: progressbarObject.setProperty("value",1.0)
    return y,framerate


def DFT128(RawPCM,framerate,basicFreq=440,ticklength=50,memoryerror="throw",progressbarObject=None):
    """
    Use native lib to convert waveform into Spectrogram which have 128 specific frequencies 
    according to MIDI specification (Equal Temp., modern tuning 440Hz).
    Support analysing based on other Tuning Standard, eg. 432Hz.
    Returning: 2D Numpy Array Object with size T x F , where F=128
    """
    sampleLength=len(RawPCM)/framerate
    print(f"sampleLength={sampleLength}")
    try:
        NFTData=libs.myalgs.specgram(RawPCM, framerate, ticklength/1000.0,#*2, 
        ticklength/1000.0, basicFreq=basicFreq,progressbarObject=progressbarObject)
    except MemoryError as e:
        print("memoryerror")
        if memoryerror == "throw":
            raise e
        return None
    print(f"F:{len(NFTData[0])},T:{len(NFTData)}")
    notesOverFlow=0
    c = 16.5 # empirical
    def dataPickle(x):
        return log(sqrt(x))/c if not sqrt(x) == 0 else -2147483648
    n_max,n_min=0,1
    #*# n = 1/c*ln(sqrt(x))
    #*# c : constant
    #*# x : spectrogram value
    for i in range(len(NFTData)):#trange(len(NFTData),dynamic_ncols=True,ascii=True,smoothing=1,mininterval=0.25,unit="ticks",unit_scale=False,unit_divisor=1024):
        for k in range(len(NFTData[0])):
            this_n = dataPickle(NFTData[i][k])
            pitch = libs.const.pitch[k]*basicFreq/440
            #imi.append(this_n)
            if this_n < n_min and not this_n == -2147483648:n_min = this_n
            if this_n > n_max:n_max = this_n
            if this_n >= 1:
                notesOverFlow+=1  
                this_n = 1
            if this_n < 0:this_n = 0
            if pitch > 1/ticklength*1000 and pitch < framerate/2:                   #Information Theory Bounds
                NFTData[i][k]=this_n
            else:NFTData[i][k]=0
    print(f"Overflowed:{notesOverFlow},min:{n_min},max:{n_max}")
    if progressbarObject: progressbarObject.setProperty("value",1.0)
    return NFTData

















def NFTData2MIDI(NFTData,lim=0,tempo=500,trackcount=8,ticklength=50,basicFreq=440,pitchwheel=True,progressbarObject=None):
    pitch = log(basicFreq/440.0)/log(2)*12*4096
    offlist=[[] for i in range(trackcount) ]
    inst=0
    #tempo=480
    ratio=1
    patt=mido.MidiFile(type=1)
    patt.ticks_per_beat=500
    notec=0
    last_col=0
    amplifier=128
    tracksplitter=8
    onetick=round(ticklength*(tempo/500))
    for i in range(trackcount):
        l=i if i<4 else 8 + i
        patt.add_track()
        patt.tracks[i].append(mido.Message("program_change",channel=l, program=74))
        patt.tracks[i].append(mido.Message("control_change",channel=l, control=7, value=40))
        if -8192 <= pitch < 8192 and pitchwheel:
            patt.tracks[i].append(mido.Message("pitchwheel",channel=l, pitch=int(round(pitch))))
    evenCol = False
    first_row=[0 for i in range(trackcount) ]
    tc=[0 if i>=4 else onetick for i in range(trackcount) ]
    for column in range(len(NFTData)):#trange(len(NFTData),dynamic_ncols=True,ascii=True,smoothing=1,mininterval=0.25,unit="ticks",unit_scale=False,unit_divisor=1024):
        if column%int((len(NFTData)/100.0)+0.5) == 0 and not progressbarObject==None:#progress display for gui
            #print(column,'\t',int(column/(len(NFTData)/100.0)+0.5),'%')
            progressbarObject.setProperty("value",int(column/(len(NFTData)/100.0)+0.5)/100.0)
        for row in range(len(NFTData[0])):
            #print(0)
            vol = max(0,NFTData[column][row]*amplifier-95)
            if round(vol) > lim and vol >= 0:
              #if row >= 24 and row <= 107:
                for l in range(4):
                    if vol <= tracksplitter*(l+1) and vol > tracksplitter*l:
                        notec+=1
                        _v=int(round(vol/ratio))
                        m1,m2=0,0
                        channel=l if evenCol else 15 - l
                        num = l if evenCol else 7 - l
                        if first_row[num]:
                            m1=tc[num]-onetick*2
                            m2=onetick*2
                            tc[num]=0
                            first_row[num]=False


                        patt.tracks[num].append(
                            mido.Message('note_on', channel=channel, note=row,time=m1,
                            velocity=_v if _v<128 else 127))        
                        offlist[num].append(
                            mido.Message('note_off', channel=channel, note=row,time=m2,
                            velocity=_v if _v<128 else 127))           
            continue

        for l in range(4):
            channel = l if evenCol else 15 - l
            num = l if evenCol else 7 - l
            tc[num]+= onetick*2       
            patt.tracks[num].extend(offlist[num])
            offlist[num]=[]
            first_row[num]=True
        evenCol = not evenCol
    if progressbarObject: progressbarObject.setProperty("value",1.0)
    return patt,notec


def NFTData2MIDI_Obsolete(NFTData,lim=0,tempo=500,trackcount=8,ticklength=50,basicFreq=440,pitchwheel=True,progressbarObject=None):
    pitch = log(basicFreq/440.0)/log(2)*12*4096
    offlist=[[] for i in range(trackcount) ]
    inst=0
    #tempo=480
    ratio=1
    patt=mido.MidiFile(type=1)
    patt.ticks_per_beat=500
    notec=0
    last_col=0
    amplifier=128
    tracksplitter=8
    onetick=round(ticklength*(tempo/500))
    for i in range(trackcount):
        l=i if i<4 else 8 + i
        patt.add_track()
        patt.tracks[i].append(mido.Message("program_change",channel=l, program=74))
        if -8192 <= pitch < 8192 and pitchwheel:
            patt.tracks[i].append(mido.Message("pitchwheel",channel=l, pitch=int(round(pitch))))
    evenCol = False
    first_row=[0 for i in range(trackcount) ]
    tc=[0 if i>=4 else onetick for i in range(trackcount) ]
    for column in range(len(NFTData)):#trange(len(NFTData),dynamic_ncols=True,ascii=True,smoothing=1,mininterval=0.25,unit="ticks",unit_scale=False,unit_divisor=1024):
        if column%int((len(NFTData)/100.0)+0.5) == 0 and not progressbarObject==None:#progress display for gui
            #print(column,'\t',int(column/(len(NFTData)/100.0)+0.5),'%')
            progressbarObject.setProperty("value",int(column/(len(NFTData)/100.0)+0.5)/100.0)
        for row in range(len(NFTData[0])):
            #print(0)
            vol = max(0,NFTData[column][row]*amplifier-96)
            if round(vol) > lim and vol >= 0:
              #if row >= 24 and row <= 107:
                for l in range(4):
                    if vol <= tracksplitter*(l+1) and vol > tracksplitter*l:
                        notec+=1
                        _v=int(round(vol/ratio))
                        m1,m2=0,0
                        channel=l if evenCol else 15 - l
                        num = l if evenCol else 7 - l
                        if first_row[num]:
                            m1=tc[num]-onetick*2
                            m2=onetick*2
                            tc[num]=0
                            first_row[num]=False


                        patt.tracks[num].append(
                            mido.Message('note_on', channel=channel, note=row,time=m1,
                            velocity=_v if _v<128 else 127))        
                        offlist[num].append(
                            mido.Message('note_off', channel=channel, note=row,time=m2,
                            velocity=_v if _v<128 else 127))           
            continue

        for l in range(4):
            channel = l if evenCol else 15 - l
            num = l if evenCol else 7 - l
            tc[num]+= onetick*2       
            patt.tracks[num].extend(offlist[num])
            offlist[num]=[]
            first_row[num]=True
        evenCol = not evenCol
    if progressbarObject: progressbarObject.setProperty("value",1.0)
    return patt,notec

def getTidrec(req):
    """Credit MnJS"""
    return getTidrec.__doc__



if __name__ == "__main__":
    #print(__file__)
    PCM,framerate=wavefileReadUnpack(os.path.join(os.path.dirname(__file__),"in.wav"))
    
    
    #print(f"长度：{patt.length}")
    patt,notec=NFTData2MIDI(DFT128(PCM,framerate))
    print(f"音符数：{notec}")
    patt.save(os.path.join(os.path.dirname(__file__),"out.mid"))
     
    input()
    ####end


