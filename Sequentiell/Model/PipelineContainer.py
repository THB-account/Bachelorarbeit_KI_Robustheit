# for visualization
import numpy
from tqdm import tqdm
from itertools import product
# for data handling

# own modules ; used for instantiating the Pipeline and Results
from Datalayer.Datalayer import DatalayerInterface
from Model.PredictionContainer import *
from Model.Pipeline import NoiseInjectionVO

class PipelineContainerVO:

    def __init__(self, PipelineElements, outqueue, inqueue):
        self.__dataLayerInterface = DatalayerInterface()
        self.__evalCollection = EvaluationCollection()
        self.__classOutQueue = outqueue # puts job into this
        self.__classInQueue = inqueue   # gets result from this
        self.__intervalWidth = 2 # private attribute, that

        it = iter(PipelineElements)
        self.__PipelineHead = next(it)
        for e in it:
            self.__PipelineHead.add(e)

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

        shape = self.__PipelineHead.shape

        # cant handle multiple base audios at once
        if len(baseAudio)>1:
            raise ValueError("Der Basisgerausche Ordner darf maximal einen Ordner mit Dateien beinhalten")
        elif len(baseAudio)==0:
            raise ValueError("Der Basisgerausche Ordner muss mindestens "
                             "einen Ordner mit Dateien oder die Gerausche selber beinhalten")

        # calculate normalization value
        normalizationValue = self.calcNormalization(list(baseAudio.values())[0])

        for direct_noise in tqdm(noiseAudio,desc="Noiseklassen", position=0):
            # TODO Überarbeiten, so dass für alle Iterationen Arrays erstellt werden
            # at the moment only one base audio set is loaded
            predictionSpace = PredictionSpaceContainerVO(n=len(noiseAudio[direct_noise])*len(list(baseAudio.values())[0])
                                                   ,shape=tuple(shape)
                                                   ,dims=self.__PipelineHead.getRanges()
                                                   ,dimNames=self.__PipelineHead.getNames()
                                                   ,dimTypes=self.__PipelineHead.getTypes()
                                                   ,name=direct_noise)
            for direct_audio in baseAudio:
                pbar = tqdm(total=len(noiseAudio[direct_noise])*len(baseAudio[direct_audio]), desc="Audiodateien", position=1, leave=False)
                for uuid_noise, uuid_audio in product(noiseAudio[direct_noise], baseAudio[direct_audio]):
                #for uuid_noise in noiseAudio[direct_noise]:
                    tempNoiseRate, tempNoiseAudio = noiseAudio[direct_noise][uuid_noise]["audio"].audio
                    noisePeakOffsets = noiseAudio[direct_noise][uuid_noise]["label"].labelOffsets  # peakOffsets is number in Nanoseconds
                    noiseInjectionTO = self.findElement(lambda n: True if isinstance(n, NoiseInjectionVO) else False)
                    noiseInjectionTO.noise = noiseAudio[direct_noise][uuid_noise]["audio"].extractAudiorange(
                        noisePeakOffsets[0], self.__intervalWidth)
                    noiseInjectionTO.sr = tempNoiseRate


                    # 2. Apply Pipeline
                    #for uuid_audio in tqdm(baseAudio[direct_audio], desc="Audiodateien", position=1, leave=False):
                        # Laden des Audio Objekts
                    tempBaseRate, tempBaseAudio = baseAudio[direct_audio][uuid_audio]["audio"].audio
                    basePeakOffsets = baseAudio[direct_audio][uuid_audio]["label"].labelOffsets  # peakOffsets is number in Nanoseconds
                    # Extrahieren des relevanten Bereichs
                    for offset in basePeakOffsets:
                        # Übergeben der Audioinformationen an die Pipeline
                        self.__PipelineHead.valueCache = baseAudio[direct_audio][uuid_audio]["audio"].\
                            extractAudiorange(offset,self.__intervalWidth)
                        # normalize audio input to calculated maximum ; audio * normVal/max(abs(audioudio))
                        self.__PipelineHead.valueCache = self.__PipelineHead.valueCache\
                                                         * normalizationValue/ \
                                                         (np.absolute(self.__PipelineHead.valueCache).max())
                        # set correlation for noise
                        noiseInjectionTO.calcCorr(self.__PipelineHead.valueCache)
                        # Accelerometerdaten für Verarbeitung
                        baseAcc = baseAudio[direct_audio][uuid_audio]["accelerometer"].\
                            extractAccrange(offset,self.__intervalWidth)
                        # setzen der Sampling Rate
                        self.__PipelineHead.samplingRate = tempBaseRate

                        # counter für indexe
                        i = 0
                        predictionAr = np.ndarray(shape)
                        while (True):
                            # run calculation
                            modifiedAudio = self.__PipelineHead.process()
                            # post to queue
                            self.__classOutQueue.put((tempBaseRate,modifiedAudio, baseAcc))
                            # read from queue
                            classResult = self.__classInQueue.get()
                            #returns [[confidence, result, pointOfInterestNano],...]
                            # process classification result
                            confidence = self.interpretResult(classResult)

                            # add to ndarray
                            d1 = int(i / (shape[1] * shape[2]))
                            d2 = int((i - d1 * shape[1] * shape[2]) / shape[2])
                            d3 = (i - (d1 * shape[1] * shape[2]+ d2 * shape[2])) # % shape[2]
                            predictionAr[d1][d2][d3] = confidence
                            i += 1
                            print(i)
                            if not self.__PipelineHead.increment():
                                i=0
                                # add n-dimensional Prediction space to container
                                predictionSpace.add(predictionAr)
                                break
                    pbar.update(1)
                pbar.close()
            # Calculate Values of Datacontainer
            self.__evalCollection.add(predictionSpace.createAnalysis(self.__dataLayerInterface))

    def calcNormalization(self, files):
        """
        :param files: directory with uuids of files. which consist of "audio", "label", "accelerometer"
        :return: integer value defining the maximum value to which every audio should be normalized
        """
        maximas = []
        # iterate over audio files
        for uuid in files:
            for offset in files[uuid]["label"].labelOffsets:
                audio = files[uuid]["audio"].extractAudiorange(offset, self.__intervalWidth)
                maximas.append(np.absolute(audio).max())
        return np.mean(maximas)

    def interpretResult(self,results):
        """
        :param results: [[confidence, result, pointOfInterestNano],...]
        :return: confidence: as integer value
        """
        """
        1. finde ok --> wenn gegeben, dann kann man weiterverfahren 
        2. kein  ok --> 
        3. Leeres  Array --> returne 0
        """
        if results==[]:
            return 0
        oks = []
        for result in results:
            if result[1].HasField("ok"):
                oks.append(result)
        if oks!=[]:
            return np.mean(oks,axis=0)[0] if len(oks)>1 else oks[0][0]
        else:
            return 0 # TODO check if 0 or -1 would be a more ideal Interpretation



    def getElementat(self, i):
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

    def findElement(self, cond):
        temp = self.__PipelineHead
        while temp.nextPipeElement != None:
            if cond(temp):
                break
            temp = temp.nextPipeElement
        return temp

    # set and get
    @property
    def dataLayerInterface(self):
        return self.__dataLayerInterface

    @property
    def evalCollection(self):
        return self.__evalCollection

    @property
    def classOutQueue(self):
        return self.__classOutQueue

    @property
    def classInQueue(self):
        return self.__classInQueue
