import scipy.signal

import numpy 

import libs
from . import mydft
from tqdm import trange

def specgram(x, fs, framesz, hop, basicFreq=440,progressbarObject=None):
    return [[pow(numpy.abs(j),2) for j in i] for i in dstft(x, fs, framesz, hop, basicFreq=basicFreq,progressbarObject=progressbarObject)]
def stft(x, fs, framesz, hop, freqsize):
    framesamp = int(framesz*fs)
    hopsamp = int(hop*fs)
    w = scipy.signal.windows.hann(framesamp)
    X = numpy.array([scipy.fft.hfft(w*x[i:i+framesamp],n=freqsize) 
                     for i in range(0, len(x)-framesamp, hopsamp)])
    return X

def dstft(x, fs, framesz, hop, basicFreq=440,progressbarObject=None):
    framesamp = int(framesz*fs)
    hopsamp = int(hop*fs)
    w = scipy.signal.windows.hann(framesamp)
    X = []
    for i in range(0, len(x)-framesamp, hopsamp):
        if (i//hopsamp)%int((((len(x)-framesamp)//hopsamp)/100.0)+0.5) == 0 and not progressbarObject==None:#progress display for gui
            #print(column,'\t',int(column/(len(NFTData)/100.0)+0.5),'%')
            progressbarObject.setProperty("value",i/(len(x)-framesamp))
        X.append(mydft.dft128(tuple(w*x[i:i+framesamp]),fs,basicFreq))
    X=numpy.array(X)
    if progressbarObject: progressbarObject.setProperty("value",1.0)
    return X

def distft(X, fs, T, framesz, hop):
    x = numpy.zeros(int(T*fs))
    framesamp = int(framesz*fs)#X.shape[1]
    w = scipy.signal.windows.hann(framesamp)
    hopsamp = int(hop*fs)
    lx=(len(x)-framesamp)
    for n,i in enumerate(trange(0, lx, hopsamp,dynamic_ncols=True,ascii=True,smoothing=1,mininterval=0.25,unit="ticks",unit_scale=False,unit_divisor=1024)):
        x[i:i+framesamp] += w*numpy.real(numpy.array(libs.mydft.idft128(tuple(X[n]),fs,440,framesamp,i)))
    return x

def istft(X, fs, T, hop):
    x = numpy.zeros(T*fs)
    framesamp = X.shape[1]
    hopsamp = int(hop*fs)
    for n,i in enumerate(range(0, len(x)-framesamp, hopsamp)):
        x[i:i+framesamp] += numpy.real(scipy.ifft(X[n]))
    return x

if __name__ == '__main__':
    #import pylab,nfft
    f0 = 440         # Compute the STFT of a 440 Hz sinusoid
    fs = 8000        # sampled at 8 kHz
    T = 5            # lasting 5 seconds
    framesz = 0.050  # with a frame size of 50 milliseconds
    hop = 0.025      # and hop size of 25 milliseconds.

    # Create test signal and STFT.
    t = numpy.linspace(0, T, T*fs, endpoint=False)
    x = numpy.sin(2*numpy.pi*f0*t)
    X = dstft(x, fs, framesz, hop, 4410)
    print(len(X))
    print(len(X[0]))
    # Plot the magnitude spectrogram.
    pylab.figure()
    pylab.imshow(numpy.absolute(X.T), origin='lower', aspect='auto',
                 interpolation='nearest')
    pylab.xlabel('Time')
    pylab.ylabel('Frequency')
    pylab.show()

    # Compute the ISTFT.
    xhat = istft(X, fs, T, hop)

    # Plot the input and output signals over 0.1 seconds.
    T1 = int(0.1*fs)

    pylab.figure()
    pylab.plot(t[:T1], x[:T1], t[:T1], xhat[:T1])
    pylab.xlabel('Time (seconds)')

    pylab.figure()
    pylab.plot(t[-T1:], x[-T1:], t[-T1:], xhat[-T1:])
    pylab.xlabel('Time (seconds)')
