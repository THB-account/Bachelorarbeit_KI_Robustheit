from librosa.effects import pitch_shift
from scipy.signal import firwin, lfilter
import numpy as np

from utils import rms

class PipelineElementVO:  # Baseclass für alle Pipelineelemente

    def __init__(self, nextPipeElement=None, useCache=False, dtype=np.dtype(np.single)):
        self._nextPipeElement = nextPipeElement  # nächstes Element in der Pipeline
        self._useCache = useCache  # für Beschleunigung von Berechnungen ; Werte die bereits berechnet wurden und nur propagiert werden müssen,
        # werden gespeichert und weiter proüagiert
        self._valueCache = None  # für Nutzung von valueCache
        self._dtype = dtype

    # own methods
    def add(self, element):  # zum Hinzufügen von Elementen ; diese werden weiter durch propagiert
        if self._nextPipeElement != None:
            self._nextPipeElement.add(element)
        else:
            self._nextPipeElement = element

    def process(self, element, sr):
        pass

    def increment(self) -> bool:
        pass

    def reset(self):
        self._valueCache = None

    def getRange(self):
        pass

    # getter and setter
    @property
    def nextPipeElement(self):
        return self._nextPipeElement

    @property
    def useCache(self):
        return self._useCache

    @property
    def valueCache(self):
        return self._valueCache

    @property
    def dtype(self):
        return self._dtype

    @nextPipeElement.setter
    def nextPipeElement(self, nextPipeElement):
        self._nextPipeElement = nextPipeElement

    @useCache.setter
    def useCache(self, useCache):
        self._useCache = useCache

    @valueCache.setter
    def valueCache(self, valueCache):
        self._valueCache = valueCache if valueCache is None else np.array(valueCache, dtype=self._dtype)

    @dtype.setter
    def dtype(self, dtype):
        self._dtype = dtype

    def __str__(self):
        return "[ownID: {0} ,nextPipelineElement: {1} , useCache: {2}, valueCache: {3}]".format( hex(id(self)),
                                                                                    hex(id(self._nextPipeElement)),
                                                                                    self._useCache,
                                                                                    self._valueCache[:4] if self._valueCache is not None else self._valueCache)


class StartElementVO(PipelineElementVO):
    # can be initialized as  None for testing purposes
    def __init__(self, baseElement=None, nextPipeElement=None):
        PipelineElementVO.__init__(self,nextPipeElement, useCache=True)
        print("\n\n{0}\n\n".format(PipelineElementVO.nextPipeElement))
        self.samplingRate = None
        self.valueCache = baseElement

    def process(self):
        if self._nextPipeElement is None:
            raise TypeError("\nDie Methode process in StartElementVO kann nicht für None-Elemente aufgerufen werden.")

        return self._nextPipeElement.process(self._valueCache, self.__samplingRate)

    def increment(self) -> bool:
        if self._nextPipeElement is None or self._nextPipeElement.increment():
            return True
        else:
            self._nextPipeElement.reset()
            return False

    def reset(self):
        if self._nextPipeElement is not None:
            temp = self.nextPipeElement
            while temp is not None:
                temp.reset()
                temp = temp.nextPipeElement

    def getRange(self):
        temp = self.nextPipeElement
        dimensions = []
        while temp is not None:
            dimensions.append(temp.getRange())
            temp = temp.nextPipeElement

        return dimensions

    @property
    def samplingRate(self):
        return self.__samplingRate

    @property
    def shape(self):
        temp = self.nextPipeElement
        dimensions = []
        while temp != None:
            dimensions.append(len(temp.valueRange))
            temp = temp.nextPipeElement

        return dimensions

    @samplingRate.setter
    def samplingRate(self, samplingRate):
        self.__samplingRate = samplingRate

    def __str__(self):
        return "[{0}\n, samplingRate: {1}]".format(PipelineElementVO.__str__(self)
                                                 , self.__samplingRate)


class PitchShiftVO(PipelineElementVO):

    # valueRange should be interpreted as Percents ; internally they
    def __init__(self, nextPipeElement=None, useCache=False, valueRange=[0]):
        PipelineElementVO.__init__(self, nextPipeElement, useCache)
        # initialize Range
        self.__valueRange = valueRange
        self.__valueCounter = 0

    def process(self, element, sr):
        if self._useCache and self._valueCache is not None:
            return self._nextPipeElement.process(
                self._valueCache,sr) if self._nextPipeElement is not None else self._valueCache

        # The value 69 leads to a little more than 1 percent shift in frequency. How is it calculated?
        # Shift in percent = old_frequency * n_steps *  2^(1/bins_per_octave)
        result = pitch_shift(element, sr=sr , n_steps=self.__valueRange[self.__valueCounter],
                             bins_per_octave=69)
        if self._useCache:
            self._valueCache = result
        return self._nextPipeElement.process(result, sr) if self._nextPipeElement is not None else result

    def increment(self) -> bool:
        def increment_self():
            # increment yourself
            if self.__valueCounter < len(self.__valueRange) - 1:
                self._valueCache = None
                self.__valueCounter += 1
                return True
            else:
                return False

        if self._nextPipeElement is None:
            return increment_self()
        elif self._nextPipeElement.increment():
            return True
        else:
            # reset next element
            self._nextPipeElement.reset()
            return increment_self()

    def reset(self):
        super().reset()
        self.__valueCounter = 0

    def getRange(self):
        return self.__valueRange.copy()

    @property
    def valueRange(self):
        return self.__valueRange.copy()

    @property
    def actualValue(self):
        return self.__valueRange[self.__valueCounter]

    @valueRange.setter
    def valueRange(self, valueRange):
        self.reset()
        self.__valueRange = valueRange

    def __str__(self):
        return "[{0}\n, valueCounter: {1} , valueRange: {2}  ]".format(super().__str__()
                                                                     , self.__valueCounter
                                                                     , self.__valueRange)


class FrequencyAugmentationVO(PipelineElementVO):

    def __init__(self, nextPipeElement=None, useCache=False, valueRange=[1]):
        PipelineElementVO.__init__(self, nextPipeElement, useCache)
        # initialize Range
        self.__valueRange = valueRange
        self.__valueCounter = 0

    def process(self, element, sr):
        if self._useCache and self._valueCache is not None:
            return self._nextPipeElement.process(
                self._valueCache,sr) if self._nextPipeElement is not None else self._valueCache
        # if the value is 1 = you cannot cut o
        if self.__valueRange[self.__valueCounter] != 1:
            # Based on: https://www.dsprelated.com/showthread/comp.dsp/62286-1.php
            # --> N*(1/FS) = 2/(fs - fp)  ; The factor at the beginning was just adapted
            if self.__valueCounter < len(self.__valueRange) - 1:
                f1 = self.__valueRange[self.__valueCounter]
                f2 = self.__valueRange[self.__valueCounter + 1]
            else:
                f1 = self.__valueRange[self.__valueCounter]
                f2 = int(sr / 2)

            if f2 != f1 and f2 < 1:
                lenFilt = int( 0.1 * int(sr/2 * (f2 - f1)) )# TODO credit source for scaling
                lenFilt |= 1
                # if lower boundary is 0 use highpass, so everything until f2 is blocked
                filWin = firwin(lenFilt, [f1, f2], pass_zero="bandstop") if f1 != 0 else firwin(lenFilt, f2, pass_zero="highpass")
                result = lfilter(filWin, 1, element)
            else:
                result = element
        else:
            result = element

        if self._useCache:
            self._valueCache = result
        return self._nextPipeElement.process(result,sr) if self._nextPipeElement is not None else result

    def increment(self) -> bool:
        def increment_self():
            # increment yourself
            if self.__valueCounter < len(self.__valueRange) - 1:
                self._valueCache = None
                self.__valueCounter += 1
                return True
            else:
                return False

        if self._nextPipeElement is None:
            return increment_self()
        elif self._nextPipeElement.increment():
            return True
        else:
            # reset next element
            self._nextPipeElement.reset()
            return increment_self()

    def reset(self):
        super().reset()
        self.__valueCounter = 0

    def getRange(self):
        return self.__valueRange.copy()

    @property
    def valueRange(self):
        return self.__valueRange.copy()

    @property
    def actualValue(self):
        return self.__valueRange[self.__valueCounter]

    @valueRange.setter
    def valueRange(self, valueRange):
        self.reset()
        self.__valueRange = valueRange

    def __str__(self):
        return "[{0}\n, valueCounter: {1} , valueRange: {2}  ]".format(super().__str__()
                                                                     , self.__valueCounter
                                                                     , self.__valueRange)


class NoiseInjectionVO(PipelineElementVO):
    # TODO ergänze Attribut für Noise-Aufnahme
    def __init__(self, nextPipeElement=None, useCache=False, valueRange=[0], noise=None, sr=None):
        PipelineElementVO.__init__(self, nextPipeElement, useCache)
        # initialize Range
        self.__valueRange = valueRange
        self.__valueCounter = 0
        self.noise = noise
        self.__sr = sr

    def process(self, element, sr):
        if self._useCache and self._valueCache is not None:
            return self._nextPipeElement.process(
                self._valueCache,sr) if self._nextPipeElement != None else self._valueCache

        # TODO Ergänze Normalisierung basierend auf SNR oder Maximum
        result = (rms(element)/rms(self.__noise)) * self.__valueRange[self.__valueCounter] * self.__noise + element

        if self._useCache:
            self._valueCache = result
        return self._nextPipeElement.process(result,sr) if self._nextPipeElement is not None else result

    def increment(self) -> bool:
        def increment_self():
            # increment yourself
            if self.__valueCounter < len(self.__valueRange) - 1:
                self._valueCache = None
                self.__valueCounter += 1
                return True
            else:
                return False

        if self._nextPipeElement is None:
            return increment_self()
        elif self._nextPipeElement.increment():
            return True
        else:
            # reset next element
            self._nextPipeElement.reset()
            return increment_self()

    def reset(self):
        super().reset()
        self.__valueCounter = 0

    def getRange(self):
        return self.__valueRange.copy()

    @property
    def valueRange(self):
        return self.__valueRange.copy()

    @property
    def actualValue(self):
        return self.__valueRange[self.__valueCounter]

    @property
    def noise(self):
        return self.__noise

    @property
    def sr(self):
        return self.__sr

    @valueRange.setter
    def valueRange(self, valueRange):
        self.reset()
        self.__valueRange = valueRange

    @noise.setter
    def noise(self, noise):
        self.reset()
        self.__noise =  np.array(noise, dtype=self._dtype) if noise is not None else None


    @sr.setter
    def sr(self, sr):
        self.__sr = sr

    def __str__(self):
        return "[{0}\n, valueCounter: {1} , valueRange: {2}, samplingRate: {3}, noise: {4} ]". \
            format(super().__str__()
                   , self.__valueCounter
                   , self.__valueRange
                   , self.__sr
                   , self.__noise[:4] if self.__noise is not None else None)
