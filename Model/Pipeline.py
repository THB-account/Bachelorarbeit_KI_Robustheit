from librosa.effects import pitch_shift
from scipy.signal import firwin, lfilter
import numpy as np
from scipy.ndimage import shift

from utils import rms

# TODO Skalierung der Eingangssignale, so dass diese nicht zum Overflow führen können
# TODO Skalierung der Noisesignale, so dass diese nicht zum Overflow führen können

class PipelineElementVO:  # Baseclass für alle Pipelineelemente

    def __init__(self, nextPipeElement=None, useCache=False, dtype=np.dtype(np.int32), dimName=None):
        self._nextPipeElement = nextPipeElement  # nächstes Element in der Pipeline
        self._useCache = useCache  # für Beschleunigung von Berechnungen ; Werte die bereits berechnet wurden und nur propagiert werden müssen,
        # werden gespeichert und weiter proüagiert
        self._valueCache = None  # für Nutzung von valueCache
        self._dtype = dtype
        self._dimName = dimName

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

    @property
    def dimName(self):
        return self._dimName

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
        self.valueCache = self.valueCache.astype(self._dtype, copy=False)

    def __str__(self):
        return "[ownID: {0} ,nextPipelineElement: {1} , useCache: {2}, valueCache: {3}]".format( hex(id(self)),
                                                                                    hex(id(self._nextPipeElement)),
                                                                                    self._useCache,
                                                                                    self._valueCache[:4] if self._valueCache is not None else self._valueCache)


class StartElementVO(PipelineElementVO):
    # can be initialized as  None for testing purposes
    def __init__(self, baseElement=None, nextPipeElement=None, dtype= np.int32):
        PipelineElementVO.__init__(self,nextPipeElement, useCache=True, dtype=dtype, dimName="Startelement")
        print("\n\n{0}\n\n".format(PipelineElementVO.nextPipeElement))
        self.__samplingRate = None
        self._valueCache = baseElement

    def process(self, element=None, sr=None):
        if self._nextPipeElement is None:
            raise TypeError("\nDie Methode process in StartElementVO kann nicht für None-Elemente aufgerufen werden.")
        if element is None or sr is None:
            return self._nextPipeElement.process(self._valueCache, self.__samplingRate)
        else:
            return self._nextPipeElement.process(element, sr)

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

    def getRanges(self):
        temp = self.nextPipeElement
        dimensions = []
        while temp is not None:
            dimRange = temp.getRange()
            if dimRange is not None:
                dimensions.append(dimRange)
            temp = temp.nextPipeElement

        return dimensions

    def getNames(self):
        temp = self.nextPipeElement
        dimensions = []
        while temp is not None:
            name = temp.dimName
            if name is not None:
                dimensions.append(name)
            temp = temp.nextPipeElement

        return dimensions

    def getTypes(self):
        temp = self.nextPipeElement
        dimensions = []
        while temp is not None:
            # name is not set in non-dimension objects
            name = temp.dimName
            classType = type(temp)
            if name is not None:
                dimensions.append(classType)
            temp = temp.nextPipeElement

        return dimensions

    def getValues(self):
        temp = self.nextPipeElement
        dimensions = []
        while temp is not None:
            # name is not set in non-dimension objects
            vrange = temp.valueRange
            if vrange is not None:
                dimensions.append(temp.actualValue)
            temp = temp.nextPipeElement

        return dimensions

    @property
    def samplingRate(self):
        return self.__samplingRate

    @property
    def shape(self):
        temp = self.nextPipeElement
        dimensions = []
        while temp is not None:
            if temp.valueRange is not None:
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
    def __init__(self, nextPipeElement=None, useCache=False, valueRange=[0], dtype=np.int32):
        PipelineElementVO.__init__(self, nextPipeElement, useCache, dtype=dtype, dimName="PitchShift in %")
        # initialize Range
        self.__valueRange = valueRange
        self.__valueCounter = 0

    def process(self, element, sr):
        if self._useCache and self._valueCache is not None:
            return self._nextPipeElement.process(
                self._valueCache,sr) if self._nextPipeElement is not None else self._valueCache


        # The value 69 leads to a little more than 1 percent shift in frequency. How is it calculated?
        # Shift in percent = old_frequency * n_steps *  2^(1/bins_per_octave)
        if self.__valueRange[self.__valueCounter] != 0:
            if element.dtype != np.single:
                result = pitch_shift(element.astype(np.single), sr=sr, n_steps=self.__valueRange[self.__valueCounter],
                                     bins_per_octave=69)
            else:
                result = pitch_shift(element, sr=sr, n_steps=self.__valueRange[self.__valueCounter],
                                     bins_per_octave=69)

            result = result.astype(self._dtype)
        else: # if no shifting needed, skip the function call
            result = element
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

    def __init__(self, nextPipeElement=None, useCache=False, valueRange=[1], dtype=np.int32):
        PipelineElementVO.__init__(self, nextPipeElement, useCache, dtype=dtype, dimName="FrequencyCutout % of Nyquist-Frequency")
        # initialize Range
        self.__valueRange = valueRange
        self.__valueCounter = 0

    def process(self, element, sr):
        if self._useCache and self._valueCache is not None:
            return self._nextPipeElement.process(
                self._valueCache,sr) if self._nextPipeElement is not None else self._valueCache
        # if the value is 1 = you cannot cut out
        if self.__valueRange[self.__valueCounter] != 0:
            f1 = self.__valueRange[self.__valueCounter - 1]
            f2 = self.__valueRange[self.__valueCounter]

            if f2 != f1 and f2 <= 1:
                # Based on: https://www.dsprelated.com/showthread/comp.dsp/62286-1.php
                # --> N*(1/FS) = 2/(fs - fp)  ; The factor at the beginning was just adapted
                lenFilt = int(0.1 * int(sr / 2 * (f2 - f1)))
                lenFilt |= 1
                # if lower boundary is 0 use highpass, so everything until f2 is blocked
                if f1==0:
                    filWin = firwin(lenFilt, f2, pass_zero="highpass")
                elif f2==1:
                    filWin = firwin(lenFilt, f1, pass_zero="lowpass")
                else:
                    filWin = firwin(lenFilt, [f1, f2], pass_zero="bandstop")
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
    def __init__(self, nextPipeElement=None, useCache=False, valueRange=[0], noise=None, sr=None, dtype=np.int32):
        PipelineElementVO.__init__(self, nextPipeElement, useCache, dtype=dtype, dimName="NoiseInjection in % of baseSignal")
        # initialize Range
        self.__valueRange = valueRange
        self.__valueCounter = 0
        self.noise = noise
        self.__sr = sr
        self.__corrShift = 0

    def process(self, element, sr):
        if self._useCache and self._valueCache is not None:
            return self._nextPipeElement.process(
                self._valueCache,sr) if self._nextPipeElement != None else self._valueCache

        dtype = np.single
        # result = signal noise ratio * scaling value * shifted noise + signal
        result = (rms(element.astype(dtype, copy=False))/rms(self.__noise.astype(dtype, copy=False))) \
                 * float(self.__valueRange[self.__valueCounter]) * shift(self.__noise, self.__corrShift).astype(dtype) \
                 + element.astype(dtype,copy=False)
        result = result.astype(self._dtype)
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

    def calcCorr(self, audio):
        if self.__noise is None:
            raise ValueError("Noise cannot be a None value for calcCorr to run.")
        # data types need to be atleast float 64 or long int so that no overflow is produced
        # "average" values can be in the 10.000-100.000, but are usually 30.000-45.000
        cor = np.correlate(np.absolute(audio.astype(np.int64)), np.absolute(self.__noise).astype(np.int64), 'full')
        i = np.argmax(cor)
        self.__corrShift = i - int(len(cor) / 2)

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

    @property
    def corrShift(self):
        return self.__corrShift

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


class AudioTyping(PipelineElementVO):
    def __init__(self,nextPipeElement=None, useCache=False):
        PipelineElementVO.__init__(self, nextPipeElement, useCache=useCache,dtype=np.int16)
        self.__valueRange = None
        self.__valueCounter = 0

    def process(self, element, sr):
        if self._useCache and self._valueCache is not None:
            return self._nextPipeElement.process(
                self._valueCache,sr) if self._nextPipeElement is not None else self._valueCache

        maxima = np.absolute(element).max()
        # reference for value range: https://numpy.org/doc/stable/reference/arrays.scalars.html#numpy.short
        if maxima > 32767:
            result = 32767/maxima * element  # new copy of element will be created
            result = result.astype(np.int16, copy=False) # aka short
        else:
            result = element.astype(np.int16, copy=False)

        if self._useCache:
            self._valueCache = result
        return self._nextPipeElement.process(result, sr) if self._nextPipeElement is not None else result

    def increment(self) -> bool:
        if self._nextPipeElement is None:
            return False
        elif self._nextPipeElement.increment():
            return True
        else:
            # reset next element
            self._nextPipeElement.reset()
            return False

    def reset(self):
        pass

    def getRange(self):
        None

    @property
    def valueRange(self):
        return None

    @property
    def actualValue(self):
        None

    @valueRange.setter
    def valueRange(self, valueRange):
        pass

    def __str__(self):
        return "[{0}\n, valueCounter: {1} , valueRange: {2}  ]".format(super().__str__()
                                                                     , self.__valueCounter
                                                                     , self.__valueRange)
