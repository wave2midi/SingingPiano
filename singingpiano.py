import os
import sys
import math
import locale
import libs
from typing import List
modulever = '1.3.2.0'
date = '2020/3/19'
M_OICQ = str(3080968787)


try:
    #from tqdm import trange
    import mido
    from math import sqrt
    import wave
    import struct
    from numpy import zeros, array, frombuffer, shape, log
    import scipy.io.wavfile
    from tap import Tap
except ImportError as e:
    print(f"lack_of_dependencies: {e}")
    input()
    exit()


def wavefileReadUnpack(filename, channelLR="", progressbarObject=None):
    try:
        wavefile = open(filename, 'r')  # open for writing
    except IOError as e:
        print("file_doesntexist")
        print(e)
        return None, None
    framerate, wavarr = scipy.io.wavfile.read(filename)
    if len(shape(wavarr)) != 1:
        if channelLR == "":
            return wavarr.sum(axis=1)/2, framerate
        elif channelLR == "L":
            return wavarr[0], framerate
        elif channelLR == "R":
            return wavarr[0], framerate
        else:
            raise ValueError("Invalid channel value: %s" % channelLR)
    else:
        return array(wavarr), framerate


def wavefileReadUnpack_Obsolete(filename, channelLR="", progressbarObject=None):
    try:
        wavefile = wave.open(filename, 'r')  # open for writing
    except IOError as e:
        print("file_doesntexist")
        print(e)
        return None, None
    #nchannels = wavefile.getnchannels()
    sample_width = wavefile.getsampwidth()
    framerate = wavefile.getframerate()
    numframes = wavefile.getnframes()
    y = zeros(numframes, dtype="float16")
    if sample_width == 2:
        packtype = "h"
    elif sample_width == 4:
        packtype = "l"
    else:
        print("Unsupported Wave File (Sample Width).")
        input()
        raise ValueError
    # trange(numframes,dynamic_ncols=True,ascii=True,smoothing=1,mininterval=0.25,unit="*4B",unit_scale=True,unit_divisor=1024):
    for i in range(numframes):
        # if i%4==0:
        # progress display for gui
        if i % int((numframes/200.0)+0.5) == 0 and not progressbarObject == None:
            # print(column,'\t',int(i/(numframes/100.0)+0.5),'%')
            progressbarObject.setProperty(
                "value", int(i/(numframes/100.0)+0.5)/100.0)
        j = i
        val = wavefile.readframes(1)
        if channelLR == "":
            left = val[0:sample_width]
            right = val[sample_width:2*sample_width]
            y[j] = round((struct.unpack(packtype, left)[0] +
                          struct.unpack(packtype, right)[0])/2)
        elif channelLR == "L":
            left = val[0:sample_width]
            y[j] = round((struct.unpack(packtype, left)[0])/2)
        elif channelLR == "R":
            right = val[sample_width:2*sample_width]
            y[j] = round((struct.unpack(packtype, right)[0])/2)
    wavefile.close()
    if progressbarObject:
        progressbarObject.setProperty("value", 1.0)
    return y, framerate


def DFT128(RawPCM, framerate, basicFreq=440, ticklength=50, memoryerror="throw", progressbarObject=None):
    """
    Use native lib to convert waveform into Spectrogram which have 128 specific frequencies 
    according to MIDI specification (Equal Temp., modern tuning 440Hz).
    Support analysing based on other Tuning Standard, eg. 432Hz.
    Returning: 2D Numpy Array Object with size T x F , where F=128
    """
    sampleLength = len(RawPCM)/framerate
    print(f"sampleLength={sampleLength}")

    def melspec(y, fr, nfft, frame_size=0.100, frame_stride=0.050, basicFreq=440, progressbarObject=None):
        if progressbarObject:
            progressbarObject.setProperty("indeterminate", True)
            progressbarObject.setProperty("value", 0.0)
        import numpy
        NFFT = nfft
        sample_rate = fr
        nfilt = 128
        # algorithm from https://haythamfayek.com/2016/04/21/speech-processing-for-machine-learning.html
        frame_length, frame_step = frame_size * sample_rate, frame_stride * \
            sample_rate  # Convert from seconds to samples
        signal_length = len(y)
        frame_length = int(round(frame_length))
        frame_step = int(round(frame_step))
        # Make sure that we have at least 1 frame
        num_frames = int(numpy.ceil(
            float(numpy.abs(signal_length - frame_length)) / frame_step))

        pad_signal_length = num_frames * frame_step + frame_length
        z = numpy.zeros((pad_signal_length - signal_length))
        # Pad Signal to make sure that all frames have equal number of samples without truncating any samples from the original signal
        pad_signal = numpy.append(y, z)

        indices = numpy.tile(numpy.arange(0, frame_length), (num_frames, 1)) + numpy.tile(
            numpy.arange(0, num_frames * frame_step, frame_step), (frame_length, 1)).T
        frames = pad_signal[indices.astype(numpy.int32, copy=False)]
        frames *= numpy.hamming(frame_length)
        mag_frames = numpy.absolute(numpy.fft.rfft(
            frames, NFFT))  # Magnitude of the FFT
        pow_frames = ((1.0 / NFFT) * ((mag_frames) ** 2))  # Power Spectrum
        # --------
        hz_points = numpy.array([0]+libs.const.pitch+[22050])*basicFreq/440
        bin = numpy.floor((NFFT + 1) * hz_points / sample_rate)
        fbank = numpy.zeros((nfilt, int(numpy.floor(NFFT / 2 + 1))))
        for m in range(1, nfilt + 1):
            f_m_minus = int(bin[m - 1])   # left
            f_m = int(bin[m])             # center
            f_m_plus = int(bin[m + 1])    # right

            for k in range(f_m_minus, f_m):
                fbank[m - 1, k] = (k - bin[m - 1]) / (bin[m] - bin[m - 1])
            for k in range(f_m, f_m_plus):
                fbank[m - 1, k] = (bin[m + 1] - k) / (bin[m + 1] - bin[m])
        filter_banks = numpy.dot(pow_frames, fbank.T)
        filter_banks = numpy.where(filter_banks == 0, numpy.finfo(
            float).eps, filter_banks)  # Numerical Stability
        filter_banks = filter_banks/nfft*2.6e7
        # filter_banks = 20 * numpy.log10(filter_banks)  # dB
        if progressbarObject:
            progressbarObject.setProperty("indeterminate", False)
            progressbarObject.setProperty("value", 1.0)
        return filter_banks
    try:
        NFTData = melspec(RawPCM, framerate, 16384, frame_size=2*ticklength/1000,
                          frame_stride=ticklength/1000, basicFreq=basicFreq, progressbarObject=progressbarObject)
        # libs.myalgs.specgram(RawPCM, framerate, ticklength/1000.0,#*2,
        # ticklength/1000.0, basicFreq=basicFreq,progressbarObject=progressbarObject)
    except MemoryError as e:
        print("memoryerror")
        if memoryerror == "throw":
            raise e
        return None
    print(f"F:{len(NFTData[0])},T:{len(NFTData)}")
    notesOverFlow = 0
    c = 16.5  # empirical

    def dataPickle(x):
        return log(sqrt(x))/c if not sqrt(x) == 0 else -2147483648
    n_max, n_min = 0, 1
    # *# n = 1/c*ln(sqrt(x))
    # *# c : constant
    # *# x : spectrogram value
    # trange(len(NFTData),dynamic_ncols=True,ascii=True,smoothing=1,mininterval=0.25,unit="ticks",unit_scale=False,unit_divisor=1024):
    for i in range(len(NFTData)):
        for k in range(len(NFTData[0])):
            this_n = dataPickle(NFTData[i][k])
            pitch = libs.const.pitch[k]*basicFreq/440
            # imi.append(this_n)
            if this_n < n_min and not this_n == -2147483648:
                n_min = this_n
            if this_n > n_max:
                n_max = this_n
            if this_n >= 1:
                notesOverFlow += 1
                this_n = 1
            if this_n < 0:
                this_n = 0
            if pitch > 1/ticklength*1000 and pitch < framerate/2:  # Information Theory Bounds
                NFTData[i][k] = this_n
            else:
                NFTData[i][k] = 0
    print(f"Overflowed:{notesOverFlow},min:{n_min},max:{n_max}")
    if progressbarObject:
        progressbarObject.setProperty("value", 1.0)
    return NFTData


def NFTData2MIDI(NFTData, lim=0, tempo=500, trackcount=8, ticklength=50, basicFreq=440, pitchwheel=True, progressbarObject=None):
    pitch = log(basicFreq/440.0)/log(2)*12*4096
    offlist = [[] for i in range(trackcount)]
    inst = 0
    # tempo=480
    ratio = 1
    patt = mido.MidiFile(type=1)
    patt.ticks_per_beat = 500
    notec = 0
    last_col = 0
    notesvolrange = 256
    notespartial = 0.25
    tracksplitter = 64
    onetick = round(ticklength*(tempo/500))
    notesoverflowed = 0
    for i in range(trackcount):
        l = i if i < 4 else 8 + i
        patt.add_track()
        patt.tracks[i].append(mido.Message(
            "program_change", channel=l, program=74))
        patt.tracks[i].append(mido.Message(
            "control_change", channel=l, control=7, value=30))  # change volume 40-10
        if -8192 <= pitch < 8192 and pitchwheel:
            patt.tracks[i].append(mido.Message(
                "pitchwheel", channel=l, pitch=int(round(pitch))))
    evenCol = False
    first_row = [0 for i in range(trackcount)]
    tc = [0 if i >= 4 else onetick for i in range(trackcount)]
    # trange(len(NFTData),dynamic_ncols=True,ascii=True,smoothing=1,mininterval=0.25,unit="ticks",unit_scale=False,unit_divisor=1024):
    for column in range(len(NFTData)):
        # progress display for gui
        if column % int((len(NFTData)/100.0)+0.5) == 0 and not progressbarObject == None:
            # print(column,'\t',int(column/(len(NFTData)/100.0)+0.5),'%')
            progressbarObject.setProperty("value", int(
                column/(len(NFTData)/100.0)+0.5)/100.0)
        for row in range(len(NFTData[0])):
            # print(0)
            vol = max(0, (NFTData[column][row] -
                          (1-notespartial))*notesvolrange/notespartial)
            if round(vol) > lim and vol >= 0:
              # if row >= 24 and row <= 107:
                thisnoteoverflowed = True
                for l in range(4):
                    if vol <= tracksplitter*(l+1) and vol > tracksplitter*l:
                        thisnoteoverflowed = False
                        notec += 1
                        _v = int(round(vol/ratio))
                        m1, m2 = 0, 0
                        channel = l if evenCol else 15 - l
                        num = l if evenCol else 7 - l
                        if first_row[num]:
                            m1 = tc[num]-onetick*2
                            m2 = onetick*2
                            tc[num] = 0
                            first_row[num] = False

                        patt.tracks[num].append(
                            mido.Message('note_on', channel=channel, note=row, time=m1,
                                         velocity=_v if _v < 128 else 127))
                        offlist[num].append(
                            mido.Message('note_off', channel=channel, note=row, time=m2,
                                         velocity=_v if _v < 128 else 127))
                if thisnoteoverflowed:
                    notesoverflowed += 1
            continue

        for l in range(4):
            channel = l if evenCol else 15 - l
            num = l if evenCol else 7 - l
            tc[num] += onetick*2
            patt.tracks[num].extend(offlist[num])
            offlist[num] = []
            first_row[num] = True
        evenCol = not evenCol
    if progressbarObject:
        progressbarObject.setProperty("value", 1.0)
    print(f"OverFlowedInMIDIGeneration:{notesoverflowed}")
    return patt, notec


def NFTData2MIDI_Obsolete(NFTData, lim=0, tempo=500, trackcount=8, ticklength=50, basicFreq=440, pitchwheel=True, progressbarObject=None):
    pitch = log(basicFreq/440.0)/log(2)*12*4096
    offlist = [[] for i in range(trackcount)]
    inst = 0
    # tempo=480
    ratio = 1
    patt = mido.MidiFile(type=1)
    patt.ticks_per_beat = 500
    notec = 0
    last_col = 0
    amplifier = 128
    tracksplitter = 8
    onetick = round(ticklength*(tempo/500))
    for i in range(trackcount):
        l = i if i < 4 else 8 + i
        patt.add_track()
        patt.tracks[i].append(mido.Message(
            "program_change", channel=l, program=74))
        if -8192 <= pitch < 8192 and pitchwheel:
            patt.tracks[i].append(mido.Message(
                "pitchwheel", channel=l, pitch=int(round(pitch))))
    evenCol = False
    first_row = [0 for i in range(trackcount)]
    tc = [0 if i >= 4 else onetick for i in range(trackcount)]
    # trange(len(NFTData),dynamic_ncols=True,ascii=True,smoothing=1,mininterval=0.25,unit="ticks",unit_scale=False,unit_divisor=1024):
    for column in range(len(NFTData)):
        # progress display for gui
        if column % int((len(NFTData)/100.0)+0.5) == 0 and not progressbarObject == None:
            # print(column,'\t',int(column/(len(NFTData)/100.0)+0.5),'%')
            progressbarObject.setProperty("value", int(
                column/(len(NFTData)/100.0)+0.5)/100.0)
        for row in range(len(NFTData[0])):
            # print(0)
            vol = max(0, NFTData[column][row]*amplifier-96)
            if round(vol) > lim and vol >= 0:
              # if row >= 24 and row <= 107:
                for l in range(4):
                    if vol <= tracksplitter*(l+1) and vol > tracksplitter*l:
                        notec += 1
                        _v = int(round(vol/ratio))
                        m1, m2 = 0, 0
                        channel = l if evenCol else 15 - l
                        num = l if evenCol else 7 - l
                        if first_row[num]:
                            m1 = tc[num]-onetick*2
                            m2 = onetick*2
                            tc[num] = 0
                            first_row[num] = False

                        patt.tracks[num].append(
                            mido.Message('note_on', channel=channel, note=row, time=m1,
                                         velocity=_v if _v < 128 else 127))
                        offlist[num].append(
                            mido.Message('note_off', channel=channel, note=row, time=m2,
                                         velocity=_v if _v < 128 else 127))
            continue

        for l in range(4):
            channel = l if evenCol else 15 - l
            num = l if evenCol else 7 - l
            tc[num] += onetick*2
            patt.tracks[num].extend(offlist[num])
            offlist[num] = []
            first_row[num] = True
        evenCol = not evenCol
    if progressbarObject:
        progressbarObject.setProperty("value", 1.0)
    return patt, notec


def getTidrec(req):
    """Credit MnJS"""
    return getTidrec.__doc__

class SingingPianoAP(Tap):
    filenames:      List[str]       # Audio file name(s) as input.
    basicfreq:      int = 440       # The frequency of A3 in the audio file, cannot be too large or too small.
    lim:            int = 0         # Notes has the veocity greater than this will be added to MIDI output.
    ticklength:     int = 50        # The length of one tick(ms).
    channel:        str = "mixed"   # Channel(s) to be read from the audio file. could be either "L", "R" or "mixed".
    tempo:          int = 500       # Special value, for experimental use.
    nopitchwheel:   bool = False    # If the pitch wheel is enabled to adjust the basic frequency of MIDI output.
    showargs:       bool = False    # If the args will be displayed.

    def configure(self):
        self.add_argument('filenames')
        self.add_argument('-bf','--basicfreq')
        self.add_argument('-l','--lim')
        self.add_argument('-t','--ticklength')
        self.add_argument('--tempo')
        self.add_argument('--nopitchwheel')
        self.add_argument('--showargs')



if __name__ == "__main__":
    args = SingingPianoAP().parse_args()
    if args.showargs:
        print(args.__str__())
    
    if len(args.filenames) == 0:
        raise ValueError("No file inputed.")
    for filename in args.filenames:
        try:
            print("Unpacking audio file: " + filename)
            PCM, framerate = wavefileReadUnpack(filename, channelLR= "" if args.channel == "mixed" else args.channel)
            print(f"Transforming data...")
            DFTData = DFT128(PCM, framerate, basicFreq=args.basicfreq, ticklength=args.ticklength)
            print(f"Writing out MIDI...")
            patt, notec = NFTData2MIDI(DFTData,
             lim=args.lim, tempo=args.tempo, ticklength=args.ticklength, basicFreq=args.basicfreq, pitchwheel= not args.nopitchwheel)
            out = os.path.splitext(filename)[0] + ".mid"
            print(f"Notes：{notec}")
            patt.save(out)
            print(f"MIDI output：{out}")
            print("----------------------------------------------------------------")
        except Exception as e:
            print(repr(e))
    print("All files processed.")
    

