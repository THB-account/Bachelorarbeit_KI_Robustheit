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
white_noise = True
normalization = False

# define realistisch parameters
freq = 8
noise = 10
frequencyCutouts = np.arange(freq+1)/(freq if freq!= 0 else 1) # [0,0.2,0.4,0.6,0.8,1]
pitchshiftPercents=[-1,0,1]
noisePercents =  np.arange(noise+1)/(noise if noise!= 0 else 1) # [0,0.2,0.4,0.6,0.8,1]

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
                             noise=None, sr=None, normalization=normalization),
            Model.Pipeline.AudioTyping(nextPipeElement=None, useCache=False)
        ]

pEl[3].sr = 44100
pEl[3].noise = noiseAudio

# --------------------------------------------------------------------------------------------------------------------
# Plot the original Signal, for Analysis
fig1 = plt.figure(figsize=(10,8))
fig1.tight_layout(pad=40.0)
ax = fig1.add_subplot(311)
ax.plot(baseAudio, label='Steckgeräusch')
plt.axhline(rms(baseAudio), color='orange', label='rms Stecken')
plt.legend()
plt.title("Originalaufnahme für den Versuch")


ax = fig1.add_subplot(312)
plt.title("Noise für den Versuch")
ax.plot(noiseAudio)
plt.axhline(rms(noiseAudio), color='orange', label='rms Noise')

ax = fig1.add_subplot(313)
plt.title("Vergleich Noise und Steckger#usch")
ax.plot(baseAudio)
plt.axhline(rms(baseAudio), color='blue', label="rms Base Audio")
ax.plot(noiseAudio, color='orange', label='noise')
plt.axhline(rms(noiseAudio), color='red', label="rms Noise")
plt.legend()

fig2 = plt.figure(figsize=(10,8))
fig2.tight_layout(pad=40.0)
ax = fig2.add_subplot(311)
ax.plot(baseAudio, label='Steckgeräusch')
plt.axhline(rms(baseAudio), color='orange', label='rms Stecken')
plt.legend()
plt.title("Originalaufnahme für den Versuch")

modAudio = rms(baseAudio)/rms(noiseAudio)*noiseAudio
ax = fig2.add_subplot(312)
plt.title("Noise für den Versuch")
ax.plot(modAudio)
plt.axhline(rms(modAudio), color='orange', label='rms Noise')

ax = fig2.add_subplot(313)
plt.title("Normierte Noise im Vergleich")
ax.plot(baseAudio)
#plt.axhline(rms(baseAudio), color='blue', label="rms Base Audio")
ax.plot(modAudio, color='orange', label='noise')
#plt.axhline(rms(modAudio), color='red', label="rms Noise")
plt.legend()

plt.show()
plt.close(fig1)
plt.close(fig2)

# --------------------------------------------------------------------------------------------------------------------
# plot modified Audio for pipeline segments
for pipePiece in pEl[2:2]:
    temp = []
    for _ in range(len(pipePiece.valueRange)):
        modAudio = pipePiece.process(baseAudio,sr)

        fig = plt.figure(2,figsize=(10,8))
        fig.suptitle(pipePiece.dimName + "  " + str(pipePiece.actualValue))

        ax = fig.add_subplot(211)
        ax.plot(modAudio)
        ax.xaxis.set_major_locator(ticker.IndexLocator(base=8820, offset=.0))

        ax = fig.add_subplot(212)
        x, y = fft_display(modAudio, sr)
        temp.append(y)
        ax.xaxis.set_major_locator(ticker.IndexLocator(base=2205, offset=.0))
        plt.plot(x,y)

        plt.show()
        plt.close(fig)
        print(pipePiece.increment())
    plt.figure(figsize=(10,8))
    for i,x in enumerate(temp):
        plt.plot(x,label=pipePiece.valueRange[i])
    plt.legend()
    plt.title("Alle Veränderungen einer Dimension im Vergleich")
    plt.show()
    plt.close()

# check whether casting of elements work
tempAudio = baseAudio.astype(np.int32)
if tempAudio.max() <= 32767:
    tempAudio = tempAudio * 32767 / tempAudio.max() * 2


fig = plt.figure()
ax = fig.add_subplot(311)
plt.plot(tempAudio)
plt.title("Signal, das außerhalb vom Wertebereich liegt [-32767,32767]")

ax = fig.add_subplot(312)
temp = pEl[4].process(tempAudio, sr)
plt.plot(temp)
plt.title(f"angepasstes Signal, was in [-32767,32767] liegt, Maximum: {temp.max()}")

ax = fig.add_subplot(313)
plt.plot(tempAudio, label="zu großes Signal")
plt.plot(pEl[4].process(tempAudio, sr), label="normiertes angepasstes Signal")

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
container = Model.PipelineContainer.PipelineContainerVO([None],None,None,normalization=normalization)
normValue = container.calcNormalization(list(baseCopy.values())[0])
print(normValue)

container = Model.PipelineContainer.PipelineContainerVO(pEl,None,None)
pEl[0].reset()

while True:
    modAudio = pEl[0].process(baseAudio, sr)
    fig = plt.figure()
    ax = fig.add_subplot(211)
    fig.suptitle(' '.join(map(str, pEl[0].getValues())))
    ax.plot(modAudio)

    ax = fig.add_subplot(212)
    xf,yf = fft_display(modAudio, sr)
    ax.plot(xf,yf)

    plt.show()
    plt.close(fig)
    if not pEl[0].increment():
        break




