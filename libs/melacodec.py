import struct
import ctypes
import math
#from tqdm import trange
def trange(*args,**kwargs):
    return range(*args)

MAGIC_NUMBER = b"MelA\xcd\xee\xca\xd3"

"""
File structure version 1.0.0(LE):
    #DEFINE metalength 0x20
    0x00->[magicnumber: char[8] 8B, version: [main: uchar 1B, sub: uchar 1B, patch: ushort 2B] 4B, 
        metalength: uint 4B] 16B
    0x10->[Basicfreq: double 8B, TicksPerSecond: double 8B, 
        NumofTicks: ulonglong 8B, NumofBands: ushort 2B, BitsPerData: ushort 2B, NFOffset: int 4B] 32B
    0x10+metalength->[DFTData: bitStoraged(BE)]
"""
def _getHeaderStruct(structVersion, LittleEndian = True):
    EndianSymbol = '<' if LittleEndian else '>'
    if structVersion == 0:
        HeaderStruct = struct.Struct(EndianSymbol + '8sBBHI')
    elif structVersion == 1: 
        HeaderStruct = struct.Struct(EndianSymbol + 'ddQHHi') 
    else:
        raise ValueError("Invalid or unsupported struct version")
    return HeaderStruct
def encode(DFTList, version, BasicFreq = 440, NFOffset = 0, BitsPerData = 7, TicksPerSecond = 20):
    """
    MELA Data(Bytes) Encoder.

    Args:
        DFTList (Array-like): Input, 2-Dimensional array-like object.
        version (list): The coding version which will be used to encode.
        BasicFreq (int, optional): The frequency of A. Defaults to 440.
        NFOffset (int, optional): Frequency shift related to the standard MIDI frequency table, 
                could be either positive or negative. Defaults to 0.
        BitsPerData (int, optional): parameter for bit storage.
    """    
    if not version:
        version = [1,0,0]
    assert(len(version) == 3)
    if version == [1,0,0]:
        NumofTicks = len(DFTList)
        NumofBands = len(DFTList[0])
        structVersion = 1
        metalength = 0x20
        HS_0 = _getHeaderStruct(0)
        HS = _getHeaderStruct(structVersion)
        BHeader = HS_0.pack(MAGIC_NUMBER, version[0], version[1], version[2], metalength) + \
        HS.pack(BasicFreq, TicksPerSecond, NumofTicks, NumofBands, BitsPerData, NFOffset)
        BBody = _encodingDFTData(DFTList, BitsPerData)
        return BHeader + BBody
    else:
        raise ValueError(f"Invalid version of file format: {version}")

def decode(MelaRaw):
    HS_0 = _getHeaderStruct(0)
    pointer = 0x0
    try:
        version = [0, 0, 0]
        magicnumber_, version[0], version[1], version[2], metalength= HS_0.unpack(MelaRaw[pointer:pointer+HS_0.size])
        pointer += HS_0.size
        if not magicnumber_ == MAGIC_NUMBER:
            raise ValueError("Invalid file format")
        if version == [1,0,0]:
            HS = _getHeaderStruct(1)
            BasicFreq, TicksPerSecond, NumofTicks, NumofBands, BitsPerData, NFOffset \
                = HS.unpack(MelaRaw[pointer:pointer+HS.size])
            pointer += HS.size
            DFTList = _decodingDFTData(MelaRaw[pointer:], NumofTicks, NumofBands, BitsPerData=BitsPerData)
            pass
        else:
            raise ValueError("Invalid version of file format: {version}")
    except Exception as e:
        raise e
    return DFTList, BasicFreq, NFOffset, TicksPerSecond


def _encodingDFTData(DFTList, BitsPerData=7):
    """version=1.0"""
    NumofTicks = len(DFTList)
    NumofBands = len(DFTList[0])
    Compressed = ctypes.create_string_buffer(math.ceil(NumofBands * NumofTicks * BitsPerData / 8))
    BitBuffer = 0
    BitCount = 0
    BufferOffset = 0
    Exp2 = 2**BitsPerData
    n_max = Exp2-1
    n_min = 0
    bPB = 8
    def lim(number):
        if number > n_max:number = n_max
        elif number < n_min:number = n_min
        return number
    def bitstorage(bits,digits):
        nonlocal Compressed,BitBuffer,BitCount,BufferOffset
        while digits:
            if BitCount + digits >= 8:
                storedBits = (8 - BitCount)
                char = (bits >> digits-storedBits) % 2**storedBits + BitBuffer
                digits -= storedBits
                struct.pack_into("!c", Compressed, BufferOffset, bytes([char]))
                BufferOffset += 1
                BitBuffer = 0
                BitCount = 0
            else:
                BitCount += digits
                BitBuffer += (bits << 8-BitCount) % 2**8
                digits = 0
        return BitBuffer, BitCount

    for i in trange(NumofTicks,dynamic_ncols=True,ascii=True,smoothing=1):
        for j in range(NumofBands):
            bit = lim(round(DFTList[i][j] * Exp2))
            BitBuffer,BitCount = bitstorage(bit,BitsPerData)
    if BitBuffer:struct.pack_into("!c", Compressed, BufferOffset, bytes([BitBuffer]))
    return Compressed.raw


def _decodingDFTData(DFTData, NumofTicks, NumofBands, BitsPerData=7):
    """version=1.0"""
    Compressed = DFTData
    Exp2 = 2**BitsPerData
    def bitfetch(dataIndex,digits):
        nonlocal Compressed
        digitsFixed = digits
        position = dataIndex * digitsFixed
        result = 0
        while digits:
            if position%8 + digits >= 8:
                BitsToFetch = (8 - position%8)
                result *= 2**BitsToFetch
                result += Compressed[position//8] % 2**BitsToFetch
                digits -= BitsToFetch
                position += BitsToFetch
            else:
                BitsToFetch = (8 - digits - position%8)
                result *= 2**digits
                result += (Compressed[position//8] % 2**(BitsToFetch+digits))//2**BitsToFetch
                digits = 0
        return result
    DFTList = []
    for i in range(NumofTicks):
        DDList = []
        for j in range(NumofBands):
            DI = i * NumofBands + j
            DDList.append(bitfetch(DI, BitsPerData) / Exp2)
        DFTList.append(DDList)
    return DFTList