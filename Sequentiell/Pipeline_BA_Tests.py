"""
Pipelinetest

Was soll mit diesem Test erreicht werden?
- Es soll aufgewiesen werden, dass die implementierten Klassen die gegebene Berechnung anforderungsgemäß implementieren.
- Es sollen Werte visualisiert werden, damit die Berechnungen verständlicher werden.

Folgende Punkte sollen getestet werden:
- Einzelne Modifikation eines Pipelineelements--> visualisieren
- Das richtige Berechnen von Korrelation für NoiseInjection
- Das richtige Datentypcasting

"""
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import Model.Pipeline
import Model.PipelineContainer
import numpy as np
import Datalayer.Datalayer
from utils import fft_display, rms
from scipy.ndimage import shift

dummyAudio = False
white_noise = False

# define realistisch parameters
frequencyCutouts = np.arange(6)/5 # [0,0.2,0.4,0.6,0.8,1]
pitchshiftPercents=[-1,0,1]
noisePercents =  np.arange(6)/5 # [0,0.2,0.4,0.6,0.8,1]

# Load Audio extracted Audio
dli= Datalayer.Datalayer.DatalayerInterface()

sr = 44100
baseAudio = dli.loadBaseAudio()
noiseAudio = dli.loadNoiseAudio()
baseCopy = baseAudio

baseAudio = list(baseAudio.values())
noiseAudio = list(noiseAudio.values())

baseAudio = list(baseAudio[0].values())[0]
noiseAudio = list(noiseAudio[0].values())[0]

baseAudio = baseAudio["audio"].extractAudiorange(baseAudio["label"].labelOffsets[0], 2)
noiseAudio = noiseAudio["audio"].extractAudiorange(noiseAudio["label"].labelOffsets[0], 2)

if dummyAudio:
    t = np.linspace(0,2,2*sr)
    f = 1000
    baseAudio = np.sin(t*2*np.pi*f)


pEl = [
            Model.Pipeline.StartElementVO(baseElement=None, nextPipeElement=None), # standard dtype np.single=float
            Model.Pipeline.FrequencyAugmentationVO(nextPipeElement=None, useCache=True,
                                    valueRange=frequencyCutouts),
            Model.Pipeline.PitchShiftVO(nextPipeElement=None, useCache=True, valueRange=pitchshiftPercents),
            Model.Pipeline.NoiseInjectionVO(nextPipeElement=None, useCache=False,
                             valueRange=noisePercents,
                             noise=None, sr=None),
            Model.Pipeline.AudioTyping(nextPipeElement=None, useCache=False)
        ]

pEl[3].sr = 44100
pEl[3].noise = noiseAudio


# Plot the original Signal, for Analysis
fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(311)
ax.plot(baseAudio)
plt.axhline(rms(baseAudio), color='blue')
plt.title("Originalaufnahme für den Versuch")

ax = fig.add_subplot(312)
plt.title("Noise für den Versuch")
ax.plot(noiseAudio)

ax = fig.add_subplot(313)
plt.title("Noise für den Versuch")
ax.plot(baseAudio)
plt.axhline(rms(baseAudio), color='blue', label="rms Base Audio")
ax.plot(noiseAudio)
plt.axhline(rms(noiseAudio), color='red', label="rms Noise")

plt.legend()
plt.show()
plt.close(fig)


for pipePiece in pEl[3:3]:
    for _ in range(len(pipePiece.valueRange)):
        modAudio = pipePiece.process(baseAudio,sr)

        fig = plt.figure(figsize=(10,8))
        fig.suptitle(pipePiece.dimName + "  " + str(pipePiece.actualValue))

        ax = fig.add_subplot(211)
        ax.plot(modAudio)
        ax.xaxis.set_major_locator(ticker.IndexLocator(base=8820, offset=.0))

        ax = fig.add_subplot(212)
        x, y = fft_display(modAudio, sr)
        ax.xaxis.set_major_locator(ticker.IndexLocator(base=2205, offset=.0))
        plt.plot(x,y)

        plt.show()
        plt.close(fig)
        print(pipePiece.increment())

# check whether casting of elements work
tempAudio = baseAudio.astype(np.int32) * 2
fig = plt.figure()
ax = fig.add_subplot(311)
plt.plot(tempAudio)
ax.yaxis.set_major_locator(ticker.IndexLocator(base=5000, offset=.0))
plt.title("Signal, das außerhalb vom Wertebereich liegt [-32767,32767]")

ax = fig.add_subplot(312)
plt.plot(pEl[4].process(tempAudio, sr))
ax.yaxis.set_major_locator(ticker.IndexLocator(base=5000, offset=.0))
plt.title("angepasstes Signal, was in [-32767,32767] liegt")

ax = fig.add_subplot(313)
plt.plot(tempAudio, label="zu großes Signal")
plt.plot(pEl[4].process(tempAudio, sr), label="normiertes angepasstes Signal")

ax.yaxis.set_major_locator(ticker.IndexLocator(base=5000, offset=.0))
plt.legend()
plt.title("Vergleich beider Signale")
plt.show()

# check correlation with signal
if white_noise:
    y = np.random.normal(0,9000,44100*2)
else:
    t = np.linspace(0,0.5,22050)
    y = 20000*np.sin(2*np.pi*t)
    y = np.append(y,np.zeros(66150))

pEl[3].sr = 44100
pEl[3].noise = y

pEl[3].calcCorr(baseAudio)

# set noise to the highest level
while pEl[3].increment():
    pass

plt.figure(figsize=(10,8))
plt.subplot(311)
plt.title("dummy Signal für Noise")
plt.plot(y)

plt.subplot(312)
plt.plot(baseAudio)
plt.plot(y)
plt.title("Base Signal und Noise im Vergleich")

plt.subplot(313)
plt.plot(baseAudio, label='originales Signal')
plt.plot(pEl[3].process(baseAudio,sr), label='verarbeiteter Sound')
plt.plot(shift(y, pEl[3].corrShift), label='korrelierte Noise')
plt.legend()

plt.show()

cor = np.correlate(np.absolute(baseAudio.astype(np.int64)), np.absolute(pEl[3].noise).astype(np.int64), 'full')
i = np.argmax(cor)
corrShift = i - int(len(cor) / 2)

fig = plt.figure()
plt.plot(cor)
plt.title("Korrelationsraph")
plt.show()
plt.close(fig)


# test normalization of input signal
container = Model.PipelineContainer.PipelineContainerVO([None],None,None)
normValue = container.calcNormalization(list(baseCopy.values())[0])
print(normValue)

container = Model.PipelineContainer.PipelineContainerVO(pEl,None,None)
pEl[0].reset()

while True:
    fig = plt.figure()
    plt.title(' '.join(map(str, pEl[0].getValues())))
    plt.plot(pEl[0].process(baseAudio, sr))

    plt.show()
    plt.close(fig)
    if not pEl[0].increment():
        break




