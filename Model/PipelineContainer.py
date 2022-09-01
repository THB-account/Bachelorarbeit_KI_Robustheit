import numpy as np # used for the memory intensive operations on arrays
from tqdm import tqdm


# own modules
from Datalayer.Datalayer import DatalayerInterface
from Model.PredictionContainer import *

class PipelineContainerVO:

    def __init__(self, PipelineElements):
        self.__dataLayerInterface = DatalayerInterface()
        self.__evalCollection = EvaluationCollection()

        it = iter(PipelineElements)
        self.__PipelineHead = next(it)
        for e in it:
            self.__PipelineHead.add(e)

        # TODO Überlegen, ob alle Vorhersagenräume in Objekt gesammelt werden sollen
        #self.__dataContainer =

    # own methods
    def run(self):
        """
        1. Load data
        2. Apply Pipeline
        3. Give Result to AI
        4. Calculate Metrics based on Result
        All Matrices should be kept in Memory (for one noisetype). Thus can statistics be calculated
        """
        # 1. Load data
        # Format { direct: { uuid: { "label": obj , "audio": obj } } }
        baseAudio = self.__dataLayerInterface.loadBaseAudio()
        noiseAudio = self.__dataLayerInterface.loadNoiseAudio()
        intervalWidth = 2
        shape = self.__PipelineHead.shape

        for direct_noise in noiseAudio:
            # TODO Überarbeiten, so dass für alle Iterationen Arrays erstellt werden
            predictionSpace = PredictionSpaceContainer( len(noiseAudio[direct_noise]) *
                                                   len(list(baseAudio.values())[0])
                                                   ,shape=tuple(shape),name= direct_noise)

            for direct_audio in baseAudio:
                for uuid_noise in noiseAudio[direct_noise]:
                    tempNoiseRate, tempNoiseAudio = noiseAudio[direct_noise][uuid_noise]["audio"].audio
                    noisePeakOffsets = noiseAudio[direct_noise][uuid_noise]["label"].labelOffsets  # peakOffsets is number in Nanoseconds

                    _offset = int(noisePeakOffsets[0] / 10 ** 9 * tempNoiseRate)
                    noiseInjectionTO = self.getElement(-1)
                    noiseInjectionTO.noise = tempNoiseAudio[_offset - int( intervalWidth * tempNoiseRate / 2 ):
                                                            _offset + int( intervalWidth * tempNoiseRate / 2 ) ]
                    noiseInjectionTO.sr = tempNoiseRate

                    # 2. Apply Pipeline
                    for uuid_audio in tqdm(baseAudio[direct_audio]):
                        # Laden des Audio Objekts
                        tempBaseRate, tempBaseAudio = baseAudio[direct_audio][uuid_audio]["audio"].audio
                        basePeakOffsets = baseAudio[direct_audio][uuid_audio][
                            "label"].labelOffsets  # peakOffsets is number in Nanoseconds

                        # Extrahieren des relevanten Bereichs
                        for offset in basePeakOffsets:
                            _offset = int(offset / 10 ** 9 * tempBaseRate)
                            # Übergeben der Audioinformationen an die Pipeline
                            self.__PipelineHead.valueCache = tempBaseAudio[_offset - int( intervalWidth * tempBaseRate / 2):
                                                                           _offset + int( intervalWidth * tempBaseRate / 2)]

                            i = 0
                            predictionAr = np.ndarray(shape)
                            while (True):

                                # run calculation
                                modifiedAudio = self.__PipelineHead.process()

                                # feed to gRPC
                                confidence = 100  # TODO insert random values

                                # add to ndarray
                                d1 = int(i / (shape[1] * shape[2]))
                                d2 = int((i - d1) / shape[2])
                                d3 = i - (d1 + d2) % shape[2]
                                predictionAr[d1][d2][d3] = confidence

                                if not self.__PipelineHead.increment():
                                    # add n-dimensional Prediction space to container
                                    predictionSpace.add(predictionAr)

                                    break

            # Calculate Values of Datacontainer
            self.__evalCollection.add(predictionSpace.createAnalysis())



    def getElement(self, i):
        if i >= 0:
            temp = self.__PipelineHead
            while i := i - 1:
                temp = temp.nextPipeElement
            return temp
        else:
            temp = self.__PipelineHead
            while temp.nextPipeElement != None:
                temp = temp.nextPipeElement
            return temp

    # set and get
    @property
    def dataLayerInterface(self):
        return self.__dataLayerInterface