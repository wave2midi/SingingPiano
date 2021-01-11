import libs
import wave
from numpy import array,log,e,sqrt
import struct
from tqdm import trange,tqdm
import pyaudio
import numpy
import scipy.signal
from threading import Thread
import time
import math
import matplotlib.pyplot as plt
def invmelspec(mel,fr,nfft,frame_size=0.100,frame_stride=0.050,basicFreq=440,progressbarObject=None):
        if progressbarObject: progressbarObject.setProperty("value",1.0)
        import numpy
        NFFT = nfft
        sample_rate = fr
        nfilt = 128
        #--------
        hz_points = numpy.array([22050,0]+libs.const.pitch)*basicFreq/440
        #print(hz_points)
        bin = numpy.floor(sample_rate * hz_points / (NFFT + 1))
        #plt.imshow(mel.T)
        #plt.show()
        fbank = numpy.zeros((int(numpy.floor(NFFT/2 + 1)),nfilt))
        for m in range(1, nfilt + 1):
            f_m_minus = int(bin[m - 1])   # left
            f_m = int(bin[m])             # center
            f_m_plus = int(bin[m + 1])    # right
            try:
                for k in range(f_m_minus, f_m):
                    fbank[m - 1, k] = (k - bin[m - 1]) / (bin[m] - bin[m - 1])
                for k in range(f_m, f_m_plus):
                    fbank[m - 1, k] = (bin[m + 1] - k) / (bin[m + 1] - bin[m])
            except:pass
        #print(numpy.shape(fbank))
        #print(fbank)
        #plt.imshow(fbank)
        #plt.show()
        #
        filter_banks = mel
        filter_banks /= (2e7/nfft)
        pow_frames = numpy.dot(filter_banks, fbank.T)
        mag_frames = (pow_frames*NFFT) ** 0.5  # Power Spectrum
        #mag_frames = numpy.zeros((668,8192))
        #for i in range(len(mag_frames)): mag_frames[i][500] = 64
        #pad_signal = scipy.signal.istft(mag_frames.T, fs=48000, window = 'hamm', nfft = 8192, nperseg = sample_rate*frame_size)
        
        plt.imshow(mag_frames)
        plt.show()
        
        frame_length, frame_step = frame_size * sample_rate, frame_stride * sample_rate  # Convert from seconds to samples
        frame_length = int(round(frame_length))
        frame_step = int(round(frame_step))
        num_frames = len(mel)  # Make sure that we have at least 1 frame
        pad_signal_length = num_frames * frame_step + frame_length
        pad_signal = numpy.zeros((pad_signal_length))
        indices = numpy.tile(numpy.arange(0, frame_length), (num_frames, 1)) + numpy.tile(numpy.arange(0, num_frames * frame_step, frame_step), (frame_length, 1)).T
        print(numpy.shape(indices))
        frames = numpy.fft.irfft(mag_frames, n=frame_length)
        frames *= numpy.hamming(frame_length)
        pad_signal[indices.astype(numpy.int32, copy=False)] += frames
        print(numpy.shape(pad_signal))
        return pad_signal[1]/400000
        # algorithm from https://haythamfayek.com/2016/04/21/speech-processing-for-machine-learning.html
        """
        indices = numpy.tile(numpy.arange(0, frame_length), (num_frames, 1)) + numpy.tile(numpy.arange(0, num_frames * frame_step, frame_step), (frame_length, 1)).T
        frames = pad_signal[indices.astype(numpy.int32, copy=False)]"""
        
        
        
         
        
        #filter_banks = 20 * numpy.log10(filter_banks)  # dB
        #return filter_banks
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
            framearray[i-framesamp:i] = array([-1 if -1>=j else 1 if 1<=j else j for j in array(x[i-framesamp:i])/32/32768]).astype("float32")
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
    _name=sys.argv[1]
    if _name[0]=='"' and _name[-1] == '"':
        _name=_name[1:-1]
    name=_name[:-5]
    
    with open(name+".mela","rb") as fetu:
        X, BasicFreq, NFOffset, TicksPerSecond,version = libs.melacodec.decode(fetu.read())
    ticklength=1/TicksPerSecond
    fs = 48000
    framerate = fs
    if version == [1,0,0]: 
        def dataConvert(x):return (x*32*256)**2
    else:#if version == [1,0,1]:
        c = 16.5
        def dataConvert(x):return e**((x)*c) if not x == 0 else 0

    freqtable = libs.const.pitch
    for i in range(len(X)):
        for k in range(len(X[0])):
            f = freqtable[k]*BasicFreq/440
            this_n = dataConvert(X[i][k])#*sqrt(f)/100
            X[i][k] = this_n if not (f>4000 or f<20) else 0
    T=len(X)*ticklength
    
    stream = pyaudio.PyAudio().open(format=pyaudio.paFloat32,channels=1,rate=fs,output=True)
    #framearray = numpy.zeros(int(T*fs),dtype="float32")
    framearray = invmelspec(array(X),fs,8192)
    print(max(framearray),min(framearray))
    sync = [0]
    sync[0] = float("inf")
    buffertime = 1.0 #seconds
    amp = 2 #2
    """W=wave.open(name+".mela.wav",mode='wb')
    W.setframerate(fs)
    W.setnchannels(1)
    W.setsampwidth(2)
    W.writeframes(framearray)
    input("Complete.")"""
    stream.write(framearray)
    #t1 = Thread(target=realtime_streamwrite,args=(stream,framearray, fs, T, ticklength*amp, buffertime, sync))
    #t2 = Thread(target=realtime_distft,args=(stream,framearray,array(X), fs, T, ticklength*amp, ticklength, sync,BasicFreq))
    #t1.start()
    #t2.start()
    #x=libs.myalgs.distft(array(X), fs, T, ticklength*2, ticklength)
    #w= array([round(j/64) for j in x],dtype="int16")
    #
    #stream.write(w)
    print(f"""File Version: {".".join([str(i) for i in version])}
Freq.={BasicFreq}\tTick Length={ticklength}\tTicks:{len(X)}""")
    print("Start Playing...\n")
    input(":")
