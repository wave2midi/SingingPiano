"""DFT and FFT"""
import math
import libs
def iexp(n):
    return complex(math.cos(n), math.sin(n))

def is_pow2(n):
    return False if n == 0 else (n == 1 or is_pow2(n >> 1))

def dft(xs,fs):
    "naive dft"
    f=libs.const.pitch
    nf=len(f)
    n = len(xs)
    return [sum((xs[k] * iexp(-2 * math.pi * k * f[i] / fs) for k in range(n)))
            for i in range(nf)]

def dftinv(xs,fs,framesamp=0):
    "naive dft"
    
    f=libs.const.pitch
    nf=len(f)
    n = len(xs)
    return [sum((xs[k] * iexp(2 * math.pi * i * f[k] / fs) for k in range(nf))) / n
            for i in range(framesamp)]

def fft_(xs, n, start=0, stride=1):
    "cooley-turkey fft"
    if n == 1: return [xs[start]]
    hn, sd = n // 2, stride * 2
    rs = fft_(xs, hn, start, sd) + fft_(xs, hn, start + stride, sd)
    for i in range(hn):
        e = iexp(-2 * math.pi * i / n)
        rs[i], rs[i + hn] = rs[i] + e * rs[i + hn], rs[i] - e * rs[i + hn]
        pass
    return rs

def fft(xs):
    assert is_pow2(len(xs))
    return fft_(xs, len(xs))

def fftinv_(xs, n, start=0, stride=1):
    "cooley-turkey fft"
    if n == 1: return [xs[start]]
    hn, sd = n // 2, stride * 2
    rs = fftinv_(xs, hn, start, sd) + fftinv_(xs, hn, start + stride, sd)
    for i in range(hn):
        e = iexp(2 * math.pi * i / n)
        rs[i], rs[i + hn] = rs[i] + e * rs[i + hn], rs[i] - e * rs[i + hn]
        pass
    return rs

def fftinv(xs):
    assert is_pow2(len(xs))
    n = len(xs)
    return [v / n for v in fftinv_(xs, n)]

if __name__ == "__main__":
    wave = [0, 1, 2, 3, 3, 2, 1, 0]
    dfreq = dft(wave)
    ffreq = fft(wave)
    dwave = dftinv(dfreq)
    fwave= fftinv(ffreq)
    print(dfreq)
    print(ffreq)
    print([v.real for v in dwave])
    print([v.real for v in fwave])
    pass