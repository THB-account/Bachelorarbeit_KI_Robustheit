import numpy as np
import matplotlib.pyplot as plt

from Datalayer.Datalayer import *
from Model.Pipeline import *
from Model.PipelineContainer import *
from Datalayer.Datalayer import *
from utils import fft_display

comp_result_pipe = False
run_calc = True
comp_result_elements = False

if __name__=="__main__":
    """
    Was muss getestet werden?
    - Predictioncontainer
        - Hinzufügen von Elementen
    - Pipeline
        - richtige Funktionsweise
        - Propagierung von Werten
        - richtige Berechnung von Zahlen
    - Pipelinecontainer
        - richtige Funktionsweise
        - Auslesen von Ergebnissen
    
    """
    # Laden der Audiodateien
    # Erstellen des Interfaces und Laden der Dateien
    dl = DatalayerInterface()
    baseAudio = dl.loadBaseAudio()
    noiseAudio = dl.loadNoiseAudio()
    baseSample = list( baseAudio.values() )[0]
    baseSample = list( baseSample.values() )[0]["audio"]

    noiseSample = list( noiseAudio.values() )[0]
    noiseSample = list( noiseSample.values() )[0]["audio"]

    # PipelineElemente erstellen mit Dummywerten
    useCache = True
    pEl = [
        StartElementVO(None, None),
        FrequencyAugmentationVO(None, useCache=useCache, valueRange=np.arange(5) / 5),
        PitchShiftVO(None, useCache=useCache, valueRange=[-6,0,6]),
        NoiseInjectionVO(None, useCache=False, valueRange=np.arange(4)/3, noise=None, sr=None)
    ]

    # Ausgeben Dummy Werte
    for x in pEl:
        print(str(x))

    # Sezten der restlichen Werte
    pEl[0].samplingRate = 44100
    pEl[0].valueCache = baseSample.audio[1][3*pEl[0].samplingRate: 5*pEl[0].samplingRate]
    pEl[3].sr = 44100
    pEl[3].noise = noiseSample.audio[1][3*pEl[0].samplingRate: 5*pEl[0].samplingRate]



    # Übergabe an Container, welche diese zu einer Pipeline verbindet
    # Pipelinecontainer
    pCont= PipelineContainerVO(pEl)

    print("Verbindung der Elemente")
    for x in pEl:
        print(str(x),"\n")

    # Aufruf der process Methode des Startelements
    result = pEl[0].process()

    # Inkrementieren der Pipeline
    print("Zustand der Pipeline {0}".format([x.actualValue for x in pEl[1:]]))
    print("Inkrementieren der Pipeline: {0}".format(pEl[0].increment()))
    print("Zustand der Pipeline {0}".format([x.actualValue for x in pEl[1:]]))

    # Resetten der Pipeline
    pEl[0].reset()
    print("\nZustand der Pipeline nach Reset {0}".format([x.actualValue for x in pEl[1:]]))


    if comp_result_pipe:
        # Length of patch
        _n = 100
        offset = int(44100 * 0.5)

        print("{0}  - {1}".format(offset, offset + _n))

        plt.figure(1)
        plt.title("Ergebnisvergleich")
        plt.subplot(121)
        plt.plot(pEl[0].valueCache[offset:offset + _n])
        plt.subplot(122)
        plt.plot(result[offset:offset + _n])

        plt.figure(2)
        plt.title("direkt Ergebnisvergleich")
        plt.plot(pEl[0].valueCache[offset:offset + _n])
        plt.plot(result[offset:offset + _n])


        # Aufruf der run Methode des Pipelinecontainers

        plt.show()

    if run_calc:
        pCont.run()

    if comp_result_elements:
        pEl = [
            StartElementVO(None, None),
            FrequencyAugmentationVO(None, useCache=useCache, valueRange=[0.3,0.6]),
            PitchShiftVO(None, useCache=useCache, valueRange=[6]),
            NoiseInjectionVO(None, useCache=False, valueRange=[1], noise=None, sr=None)
        ]
        pEl[0].samplingRate, pEl[0].valueCache = 44100, baseSample.audio[1][3*44100: 5*44100]
        pEl[3].sr, pEl[3].noise = 44100, noiseSample.audio[1][3 * pEl[0].samplingRate: 5 * pEl[0].samplingRate]

        plt.style.use('tableau-colorblind10')

        # Filterung von Frequenzen
        temp = pEl[1].process(pEl[0].valueCache, pEl[0].samplingRate)
        fig = plt.figure(3)
        fig.suptitle("Filterung von Frequenzen")

        plt.subplot(211)
        plt.plot(pEl[0].valueCache,color="b", label="og")
        plt.plot(temp, color="orange", label="prcs")

        plt.subplot(212)
        og = fft_display(pEl[0].valueCache, pEl[0].samplingRate)
        pr = fft_display(temp, pEl[0].samplingRate)
        plt.plot(og[0], og[1], color="b", label="og")
        plt.plot(pr[0], pr[1], color="orange", label="prcs")

        # Pitch Shift
        temp = pEl[2].process(pEl[0].valueCache, pEl[0].samplingRate)
        fig = plt.figure(4)
        fig.suptitle("Pitch Shift")
        plt.subplot(211)
        plt.plot(pEl[0].valueCache, color="b", label="og")
        plt.plot(pEl[2].process(pEl[0].valueCache, pEl[0].samplingRate), color="orange", label="prcs")

        plt.subplot(212)
        og = fft_display(pEl[0].valueCache, pEl[0].samplingRate)
        pr = fft_display(temp, pEl[0].samplingRate)
        plt.plot(og[0], og[1], color="b", label="og")
        plt.plot(pr[0], pr[1], color="orange", label="prcs")

        # Frequenzüberlagerung
        temp = pEl[3].process(pEl[0].valueCache, pEl[0].samplingRate)
        fig = plt.figure(5)
        fig.suptitle("Frequenzüberlagerung")
        plt.subplot(211)
        plt.plot(pEl[0].valueCache, color="b", label="og")
        plt.plot(pEl[3].process(pEl[0].valueCache, pEl[0].samplingRate), color="orange", label="prcs")

        plt.subplot(212)
        og = fft_display(pEl[0].valueCache, pEl[0].samplingRate)
        pr = fft_display(temp, pEl[0].samplingRate)
        plt.plot(og[0], og[1], color="b", label="og")
        plt.plot(pr[0], pr[1], color="orange", label="prcs")

        # whole Pipeline
        pCont = PipelineContainerVO(pEl)
        temp = pEl[0].process()
        fig = plt.figure(6)
        fig.suptitle("gesamte Pipeline")
        plt.subplot(211)
        plt.plot(pEl[0].valueCache, color="b", label="og")
        plt.plot(temp, color="orange", label="prcs")

        plt.subplot(212)
        og = fft_display(pEl[0].valueCache, pEl[0].samplingRate)
        pr = fft_display(temp, pEl[0].samplingRate)
        plt.plot(og[0], og[1], color="b", label="og")
        plt.plot(pr[0], pr[1], color="orange", label="prcs")


        plt.show()
