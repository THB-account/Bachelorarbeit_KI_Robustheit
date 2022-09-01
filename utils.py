from numpy.fft import fft
from numpy import linspace, mean, sqrt, square
import matplotlib.pyplot as plt


def fft_display(n, sr, plot=False, name=None):

    nF = fft(n)
    nF = 2*abs(nF)/len(nF)

    xF = linspace(0,sr,len(nF) + 1)
    nF = nF[:int(len(nF)/2)]
    xF = xF[:len(nF)]

    if plot:
        plt.figure()
        if name is not None:
            plt.title(name)
        plt.plot(xF,nF)

        plt.show()
        plt.close()
    return (xF, nF)

def rms(n):
    return sqrt(mean(square(n)))
