import struct
import ctypes
import math
import numpy as np
#from tqdm import trange
def trange(*args,**kwargs):
    return range(*args)

MAGIC_NUMBER = b"MelA\xcd\xee\xca\xd3"

"""
File structure version 1.0(LE):
    #DEFINE metalength 0x20
    0x00->[magicnumber: char[8] 8B, version: [main: uchar 1B, sub: uchar 1B, patch: ushort 2B] 4B, 
        metalength: uint 4B] 16B
    0x10->[Basicfreq: double 8B, TicksPerSecond: double 8B, 
        NumofTicks: ulonglong 8B, NumofBands: ushort 2B, BitsPerData: ushort 2B, NFOffset: int 4B] 32B
    0x10+metalength->[DFTData: bitStoraged(BE)]
File structure version 2.0(LE):
    #DEFINE metalength 0x20
    0x00->[magicnumber: char[8] 8B, version: [main: uchar 1B, sub: uchar 1B, patch: ushort 2B] 4B, 
        metalength: uint 4B] 16B
    0x10->[Basicfreq: double 8B, TicksPerSecond: double 8B, 
        NumofTicks: ulonglong 8B, NumofBands: ushort 2B, BitsPerData: ushort 2B, NFOffset: ushort 2B, isMapped: ushort 2B] 32B
    0x10+metalength->[Map(optional): bytes varied, DFTData: bitStoraged(BE)]
"""
def _getHeaderStruct(structVersion, LittleEndian = True):
    EndianSymbol = '<' if LittleEndian else '>'
    if structVersion == 0:
        HeaderStruct = struct.Struct(EndianSymbol + '8sBBHI')
    elif structVersion == 1: 
        HeaderStruct = struct.Struct(EndianSymbol + 'ddQHHi') 
    elif structVersion == 2: 
        HeaderStruct = struct.Struct(EndianSymbol + 'ddQHHHH') 
    else:
        raise ValueError("Invalid or unsupported struct version")
    return HeaderStruct
def encode(DFTList, version, BasicFreq = 440, NFOffset = 0, BitsPerData = 7, TicksPerSecond = 20,
 PlainText = False):
    """
    MELA Data(Bytes) Encoder.

    Args:
        DFTList (Array-like): Input, 2-Dimensional array-like object.(3-Dimensional if the field channels is specified)
        version (list): The coding version which will be used to encode.
        BasicFreq (int, optional): The frequency of A. Defaults to 440.
        NFOffset (int, optional): Frequency shift related to the standard MIDI frequency table, 
                could be either positive or negative. Defaults to 0.
        BitsPerData (int, optional): parameter for bit storage.
        PlainText (bool, optional): if so, it will use a plain text representation to encode data (bitsperdata will be forced to 6).
    """    
    if not version:
        version = [1,2,0]
    assert(len(version) == 3)
    #args verification start
    if np.ndim(DFTList) == 3 and not version >= [1,2,0]:raise ValueError(f"Multichannel unsupported for the specified version.")
    #args verification end
    if version[:2] == [1,0]:
        structVersion = 1
        metalength = 0x20
        NumofTicks = len(DFTList)
        NumofBands = len(DFTList[0])
        HS_0 = _getHeaderStruct(0)
        HS = _getHeaderStruct(structVersion)
        BHeader = HS_0.pack(MAGIC_NUMBER, version[0], version[1], version[2], metalength) + \
        HS.pack(BasicFreq, TicksPerSecond, NumofTicks, NumofBands, BitsPerData, NFOffset)
        BBody = _encodingDFTData(DFTList, BitsPerData)
        return BHeader + BBody
    elif version[:2] == [1,1]:
        structVersion, metalength = 2, 0x20
        NumofTicks, NumofBands = len(DFTList), len(DFTList[0])
        HS_0 = _getHeaderStruct(0)
        HS = _getHeaderStruct(structVersion)
        Mapped = True if PlainText else False
        BHeader = HS_0.pack(MAGIC_NUMBER, version[0], version[1], version[2], metalength) + \
        HS.pack(BasicFreq, TicksPerSecond, NumofTicks, NumofBands, BitsPerData, NFOffset, Mapped)
        if Mapped:
            maptext = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
            #maptext = b' \\^",:;Il!i><~+_-?][}{1)(|\\/jrxnuvczUJCLQ0OZmwqpdbkhao*#MW&8%B@$'
            Map = maptext
            BBody = _encodingDFTData(DFTList, 6, MapTable = maptext)
        else:
            Map=b""
            BBody = _encodingDFTData(DFTList, BitsPerData)
        return BHeader + Map + BBody
    elif version[:2] == [1,2]:
        pass
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
        if version[:2] == [1,0]:
            HS = _getHeaderStruct(1)
            BasicFreq, TicksPerSecond, NumofTicks, NumofBands, BitsPerData, NFOffset \
                = HS.unpack(MelaRaw[pointer:pointer+HS.size])
            pointer += HS.size
            DFTList = _decodingDFTData(MelaRaw[pointer:], NumofTicks, NumofBands, BitsPerData=BitsPerData)
        elif version[:2] == [1,1]:
            HS = _getHeaderStruct(2)
            BasicFreq, TicksPerSecond, NumofTicks, NumofBands, BitsPerData, NFOffset, Mapped \
                = HS.unpack(MelaRaw[pointer:pointer+HS.size])
            pointer += HS.size
            if Mapped:
                MapTable, = struct.unpack("64s", MelaRaw[pointer:pointer+64])
                pointer += 64
                DFTList = _decodingDFTData(MelaRaw[pointer:], NumofTicks, NumofBands, BitsPerData=BitsPerData, MapTable=MapTable)
            else:
                DFTList = _decodingDFTData(MelaRaw[pointer:], NumofTicks, NumofBands, BitsPerData=BitsPerData)
        else:
            raise ValueError("Invalid version of file format: {version}")
    except Exception as e:
        raise e
    return DFTList, BasicFreq, NFOffset, TicksPerSecond, version


def _encodingDFTData(DFTList, BitsPerData=7, MapTable=None):
    """version=1.0"""
    NumofTicks = len(DFTList)
    NumofBands = len(DFTList[0])
    if MapTable: 
        Compressed = ctypes.create_string_buffer(math.ceil(NumofBands * NumofTicks * 8 / 8))
    else:
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
    if not MapTable:
        for i in trange(NumofTicks,dynamic_ncols=True,ascii=True,smoothing=1):
            for j in range(NumofBands):
                bit = lim(int(round(DFTList[i][j] * Exp2)))
                BitBuffer,BitCount = bitstorage(bit,BitsPerData)
        if BitBuffer:struct.pack_into("!c", Compressed, BufferOffset, bytes([BitBuffer]))
    else:
        for i in trange(NumofTicks,dynamic_ncols=True,ascii=True,smoothing=1):
            for j in range(NumofBands):
                bit = lim(int(round(DFTList[i][j] * Exp2)))
                struct.pack_into("!c", Compressed, BufferOffset, bytes([MapTable[bit]]))
                BufferOffset += 1
    return Compressed.raw


def _decodingDFTData(DFTData, NumofTicks, NumofBands, BitsPerData=7, MapTable=None):
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
    if not MapTable:
        for i in range(NumofTicks):
            DDList = []
            for j in range(NumofBands):
                DI = i * NumofBands + j
                DDList.append(bitfetch(DI, BitsPerData) / Exp2)
            DFTList.append(DDList)
    else:
        InvMapTable = [0 for i in range(256)]
        for i in range(len(MapTable)):
            InvMapTable[MapTable[i]] = i
        Exp2 = 2**6
        for i in range(NumofTicks):
            DDList = []
            for j in range(NumofBands):
                DI = i * NumofBands + j
                DDList.append(InvMapTable[Compressed[DI]] / Exp2)
            DFTList.append(DDList)
    return DFTList