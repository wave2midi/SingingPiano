#import pickle
import locale#from LANG_zh_CN import *
ver='1.3.0.1'
date='2020/1/12'
M_OICQ=str(3080968787)
M_select_lang=r'''
Lost language file. 
     _,----,_     
    /  /  \  \
   [----------]
  |   |    |   |
   [----------]
    \_ \  / _/
      '----'        
Please (re)type the language name (Example:en_US):'''
M_lostthislanguage=r'''
     _,----,_     
    /        \
   [   |  |   ]
  |            |
   [   /~~\   ]
    \_      _/
      '----'
According language file doesn't exist:'''

import sys
import math
from tqdm import trange
rootdir=sys.argv[0]
args=sys.argv[1:]
isUI=True#DEFAULT
custom_LANG=False
if args:
    isUI=False
    

if not isUI:
    if '--DEBUG' in args:
        while True:
            print('DEBUG MODE:')
            print('CUSTOM LANGUAGE:1\tEXIT:0')
            u_in=input(':')
            if u_in == '0':
                exit()
            elif u_in == '1':
                custom_LANG = True
                isUI = True
                while True:
                    LANG2CONF=input(M_select_lang)
                    try:
                        lang_file=open('LANG.'+LANG2CONF+'.ini','r')
                        #lang_conf_W=open('LANG.conf','w')
                        #lang_conf_W.write(LANG2CONF)
                        exec(lang_file.read(),globals())
                        
                        
                        #lang_conf_W.close()
                        break
                    except Exception as err:
                        print(M_lostthislanguage+'LANG.'+LANG2CONF+'.ini')
                        print('Error code:',err)
                break

try:
    if not custom_LANG:
        envlocale = locale.getdefaultlocale()[0]
        lang_file=open(rootdir+'/../LANG.'+envlocale+'.ini','r')
    exec(lang_file.read(),globals())
    lang_file.close()
except Exception as err__:
    print('Lost language for your area.\nError code:',err__)
    try:
        lang_conf=open(rootdir+'/../LANG.conf','r')
        lang_file=open(rootdir+'/../LANG.'+lang_conf.read()+'.ini','r')
        exec(lang_file.read(),globals())
        lang_file.close()
    except Exception as err_:
        print('Error code:',err_)
        #set_LANG()
        while True:
            LANG2CONF=input(M_select_lang)
            try:
                lang_file=open(rootdir+'/../LANG.'+LANG2CONF+'.ini','r')
                lang_conf_W=open(rootdir+'/../LANG.conf','w')
                lang_conf_W.write(LANG2CONF)
                exec(lang_file.read(),globals())
                lang_file.close()
                lang_conf_W.close()
                break
            except Exception as err:
                print(M_lostthislanguage+'LANG.'+LANG2CONF+'.ini','r')
                print('Error code:',err)
    
readme=M_readme1+M_OICQ+M_readme2    



def rarg(argname,default):
    global args
    try:
        _value=args[args.index(argname)+1]
    except:
        _value=default
    return _value

try:
    import mido
    from pylab import *
    from math import *
    import wave 
    import struct
except:
    print(M_no_depend)
    input()
    exit()


if not isUI:
    print(M_infuncmode)
    print(args)
    if '-h' in args or 'help' in args or '?' in args:
        print(M_help4funcmode)
        input()
        exit()
    else:
        _name=args[0]
        if len(_name.split('"')) == 3:
            _name=_name.split('"')[1]
        name=_name[:-4]
        NT=int(rarg('-t',5))
        BPM=int(rarg('-b',500))
        NFFT=int(rarg('-n',2400))
        lim=int(rarg('-l',8))
        channelLR=rarg("-ch","")
    
        print(M_argstip1+name+M_argstip2+str(
            NT)+M_argstip3+str(NFFT)+M_argstip4+str(lim))
        outfile=name+'-T'+str(NT)+'N'+str(NFFT)+'L'+str(lim)+'V'+ver+channelLR+'.mid'
        print(M_outfile+outfile)
        tempo=mido.bpm2tempo(BPM)
        limvel=1

        
while isUI:
    print(readme,M_versionis+ver+'    '+date+'\n\n')
    _name=input(M_pleaseinput_filename)
    if _name[0]=='"' and _name[-1] == '"':
        _name=_name[1:-1]
    name=_name[:-4]
    try:
        NT=eval(input(M_pleaseinput_ticklong))
    except SyntaxError:
        NT=5
    try:
        BPM=eval(input(M_pleaseinput_BPM))
    except SyntaxError:
        BPM=500
    try:
        NFFT=eval(input(M_pleaseinput_FFTnumber))
    except SyntaxError:
        NFFT=2400
    try:
        lim=eval(input(M_pleaseinput_limit_of_MIDIwriter))
    except SyntaxError:
        lim=8
    try:
        channelLR=input("请键入声道选项:")
        if not channelLR == "L" and not channelLR == "R":
            raise SyntaxError
    except SyntaxError:
        channelLR=""
    
    """try:
        limvel=eval(input("请键入输出MIDI力度的压限倍数:"))
    except SyntaxError:
        """
    limvel=1
    print()
    try:
        print(M_bugs[ver])
    except:
        pass
    print()
    print(M_argstip1+name+M_argstip2+str(
        NT)+M_argstip3+str(NFFT)+M_argstip4+str(lim))
    outfile=name+'-T'+str(NT)+'N'+str(NFFT)+'L'+str(lim)+'V'+ver+channelLR+'.mid'
    print(M_outfile+outfile)
    tempo=mido.bpm2tempo(BPM)
    if NT*tempo%500 != 0:
        while True:
            print(M_warning_BPM)
            u_in =input(M_retype_selection)
            if u_in == '1':
                while True:
                    try:
                        print(M_ticklong_now,NT)
                        t_r=eval(input(M_retype_BPM))
                    except:
                        print(M_invalid_input)
                        continue
                    tempo=mido.bpm2tempo(t_r)
                    if tempo*NT%500==0:
                        break
                    else:
                        print(M_invalid_equation)
                        continue
            elif u_in == '2':
                while True:
                    try:
                        NT_r=eval(input(M_retype_ticklong))
                    except:
                        print(M_invalid_input)
                        continue
                    NT=NT_r
                    if tempo*NT%500==0:
                        break
                    else:
                        print(M_invalid_equation)
                        continue
            elif u_in == '0':
                while True:
                    try:
                        NT_r=eval(input(M_retype_ticklong))
                        t_r=eval(input(M_retype_BPM))
                    except:
                        print(M_invalid_input)
                        continue
                    NT=NT_r
                    tempo=mido.bpm2tempo(t_r)
                    if tempo*NT%500==0:
                        break
                    else:
                        print(M_invalid_equation)

            else:
                print(M_invalid_input)
                continue
    okay=input(M_yes_or_cancel).upper()
    if okay == 'N':
        print(M_canceled)
        continue
    else:
        break
    




def interpolation(lst,pos):
    ipos=int(pos)
    try:
        return lst[ipos]*(ipos+1-pos)+lst[ipos+1]*(pos-ipos)
    except IndexError:
        return 0


filename = name+".wav"
print(M_reading_wavefile)
try:
    wavefile = wave.open(filename, 'r') # open for writing
except IOError as e:
    print(M_file_noexist)
    print(e)
    input()
    exit()
nchannels = wavefile.getnchannels()  
sample_width = wavefile.getsampwidth()  
framerate = wavefile.getframerate()  
numframes = wavefile.getnframes()  
  
print(M_data_wavemeta,M_data_channel,nchannels,M_data_sample_width,
      sample_width,M_data_framerate,framerate,M_data_numofframes,numframes)  
  
 
y = zeros(numframes)
#y=[]
if sample_width == 2:
    packtype="h"
elif sample_width == 4:
    packtype="l"
else:
    print("Unsupported Wave File (Sample Width).")
    input()
    raise ValueError
for i in trange(numframes*4,dynamic_ncols=True,ascii=True,smoothing=1,mininterval=0.25,unit="B",unit_scale=True,unit_divisor=1024):  
    if i%4==0:
        j=i//4
        val = wavefile.readframes(1)
        if channelLR == "":
            left = val[0:sample_width]
            right = val[sample_width:2*sample_width]
            #y.append(struct.unpack(packtype, left )[0])
            y[j]=round((struct.unpack(packtype, left )[0]+struct.unpack(packtype, right )[0] )/2)
        elif channelLR == "L":
            left = val[0:sample_width]
            #right = val[sample_width:2*sample_width]
            #y.append(struct.unpack(packtype, left )[0])
            y[j]=round((struct.unpack(packtype, left )[0] )/2)
        elif channelLR == "R":
            #left = val[0:sample_width]
            right = val[sample_width:2*sample_width]
            #y.append(struct.unpack(packtype, left )[0])
            y[j]=round((struct.unpack(packtype, right )[0] )/2)
        
            


        
wavefile.close()  

#div=1000.0/NT 
Fs = framerate
del framerate,val#,left
print(M_FFT_level_start)
try:
    n=specgram(y, NFFT=NFFT, Fs=Fs,noverlap=NFFT-(float(Fs)/960*NT)) #原数据1024,900#div
except MemoryError:
    print(M_memoryerror)
    input()
    exit()
#show()
print(len(n[0]))
print(len(n[0][0]))
#input()
#exit()
print(M_FFT_level_end)

pitch=[8.17, 8.662, 9.177, 9.723, 10.301, 10.913, 11.562, 12.25, 12.978,
       13.75, 14.568, 15.434, 16.352, 17.324, 18.354, 19.445, 20.602, 21.827,
       23.125, 24.5, 25.957, 27.5, 29.135, 30.868, 32.703, 34.648, 36.708,
       38.891, 41.203, 43.654, 46.249, 48.999, 51.913, 55.0, 58.27, 61.735,
       65.406, 69.296, 73.416, 77.782, 82.407, 87.307, 92.499, 97.999,
       103.826, 110.0, 116.541, 123.471, 130.813, 138.591, 146.832, 155.563,
       164.814, 174.614, 184.997, 195.998, 207.652, 220.0, 233.082, 246.942,
       261.626, 277.183, 293.665, 311.127, 329.628, 349.228, 369.994, 391.995,
       415.305, 440.0, 466.164, 493.883, 523.251, 554.365, 587.33, 622.254,
       659.255, 698.456, 739.989, 783.991, 830.609, 880.0, 932.328, 987.767,
       1046.502, 1108.731, 1174.659, 1244.508, 1318.51, 1396.913, 1479.978,
       1567.982, 1661.219, 1760.0, 1864.655, 1975.533, 2093.005, 2217.461,
       2349.318, 2489.016, 2637.02, 2793.826, 2959.955, 3135.963, 3322.438,
       3520.0, 3729.31, 3951.066, 4186.009, 4434.922, 4698.636, 4978.032,
       5274.041, 5587.652, 5919.911, 6271.927, 6644.875, 7040.0, 7458.62,
       7902.133, 8372.018, 8869.844, 9397.273, 9956.063, 10548.082, 11175.303,
       11839.822, 12543.854]
im=[]

print(M_mapping_level_start)
for i in trange(len(n[0][0]),dynamic_ncols=True,ascii=True,smoothing=1,mininterval=0.25,unit="ticks",unit_scale=False,unit_divisor=1024):
    imi=[]
    n0i=[]
    for k in range(len(n[0])):
        n0i.append(n[0][k][i])
    for j in range(128):
        #imi.append(log(interpolation(n0i,pitch[j]/Fs*NFFT))*8/limvel)
        imi.append(sqrt(sqrt(interpolation(n0i,pitch[j]/Fs*NFFT)))*4/limvel)
    im.append(imi)
n,n0i = None,None
print(M_mapping_level_end)
####pic2midi
inst=0
tempo=500
ratio=2

#from PIL import Image
#from pylab import *
print(M_generate_level_start)



offlist=[[],[],[],[],[],[],[],[]]

notec=0
last_col=0

___t=int(NT*(tempo/500.0)+0.5)

print(M_creating_tracks)

patt=mido.MidiFile(type=1)
patt.add_track()
patt.add_track()
patt.add_track()
patt.add_track()
patt.add_track()
patt.add_track()
patt.add_track()
patt.add_track()
T1=patt.tracks[0]
T2=patt.tracks[1]
T3=patt.tracks[2]
T4=patt.tracks[3]
T5=patt.tracks[4]
T6=patt.tracks[5]
T7=patt.tracks[6]
T8=patt.tracks[7]
print(M_created_tracks)
first_row=[0,0,0,0,0,0,0,0]
tc=[0,0,0,0,0,0,0,0]
l_i=len(im)
oldlist=[T1,T2,T3,T4,T5,T6,T7,T8]


for column in trange(l_i,dynamic_ncols=True,ascii=True,smoothing=1,mininterval=0.25,unit="ticks",unit_scale=False,unit_divisor=1024):
    #if column%int((l_i/100.0)+0.5) == 0:
    #    print(column,'\t',int(column/(l_i/100.0)+0.5),'%')
    for row in range(len(im[0])):
        #print(0)
        vol = im[column][row]
        if vol > lim:
            #print(1)
            for l in range(8):
                if vol <= 32+32*l and vol > 32*l:
                    notec+=1
                    _v=int(vol/ratio+0.5)
                    m1,m2=0,0
                    if first_row[l]:
                        m1=tc[l]-___t
                        m2=___t
                        tc[l]=0
                        first_row[l]=False
                    oldlist[l].append(
                        mido.Message('note_on', note=row,time=m1,
                        velocity=_v if _v<128 else 127))        
                    offlist[l].append(
                        mido.Message('note_off', note=row,time=m2,
                        velocity=_v if _v<128 else 127))           
        continue
    for num in range(8):
        tc[num]+= ___t       
        oldlist[num].extend(offlist[num])
        offlist[num]=[]
        first_row[num]=True
for l in range(8):
    m1=tc[l]-___t
    tc[l]=0
    first_row[l]=False
    oldlist[l].append(
        mido.Message('note_on', note=row,time=m1,
        velocity=1))        
    offlist[l].append(
        mido.Message('note_off', note=row,time=0,
        velocity=1))
    oldlist[l].extend(offlist[num])
    offlist[l]=[]

(T1,T2,T3,T4,T5,T6,T7,T8)=oldlist
print(M_generate_level_end)
#eot = midi.EndOfTrackEvent(tick=1)
T1.append(mido.MetaMessage('end_of_track'))
T2.append(mido.MetaMessage('end_of_track'))
T3.append(mido.MetaMessage('end_of_track'))
T4.append(mido.MetaMessage('end_of_track'))
T5.append(mido.MetaMessage('end_of_track'))
T6.append(mido.MetaMessage('end_of_track'))
T7.append(mido.MetaMessage('end_of_track'))
T8.append(mido.MetaMessage('end_of_track'))

print(M_notes+str(notec))
#print(f"长度：{patt.length}")
print(M_writing_file)
patt.save(outfile)
print(M_outputed,outfile)        
input()
####end


