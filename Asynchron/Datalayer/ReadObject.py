# file acess and management
import json
import os


# for file accessing and numeric management
from scipy.io import wavfile as wav
from numpy import loadtxt, append, zeros
from math import ceil, floor

# for checking the samplingrate of file
import wave

# own classes for loading and interface to higher layers
import Datalayer.Datalayer as Datalayer

class AudioLoadDO:
    def __init__(self):
        pass

    def __loadFromSubdirectory(self, pathToDir, load_acc=False, check_labecount=False):
        # Dateiendungen. Diese haben eine Priorität von Links nach Rechts
        file_extensions = ["_labels_approved.json", "_labels_modified.json", "_labels.json"]
        samplingRateOriginal = None # used for checking consistent sampling Rate
        samplingRateComp = None # for comparison of sampling rates
        samplingRateRef = None # for referencing reference file
        labelCount = None # for check if all files contain same number of labels
        labelCountRef = None # for referencing reference file

        it = os.scandir(pathToDir)  # opens a stream/iterator which has to be closed ; This is faster than os.listdir
        dirs = {direct.name: {} for direct in it if direct.is_dir()}
        it.close()

        # Dateiordnung: BaseAudio sind Steckgeräusche, Noise sind Stöckgeräusche
        # script/BaseAudio/Fileclass_1/ Audio Files, Labels, etc.
        #                 /Fileclass_2
        #                 ....
        #       /NoiseAudio/Fileclass1/ Audio Files, Labels etc.
        # Dies ist für den Fall, dass es keine Dateiklassen gibt, so dass die Dateien einfach abgelegt werden
        if not dirs:
            dirs[""] = {}

        for direct in dirs:  # for Fileclass_n
            it = os.scandir("{0}\\{1}".format(pathToDir,
                                              direct))  # opens a stream/iterator which has to be closed ; This is faster than os.listdir
            # for audiofiles ; it is the basis of the analysis so they are center of analysis
            # audiofile is just a file of a directory, not the name of an audiofile, unless it ends with .wav
            for audiofile in it:
                if audiofile.name.endswith(".wav"): # if file exists
                    file_found = False # control variable to check for labels
                    uuid = audiofile.name.split("_")[0] # extract identifier for all files

                    for extension in file_extensions:  # check for label
                        labelfile = "{0}\\{1}\\{2}{3}".format(pathToDir, direct, uuid, extension)
                        if os.path.exists(labelfile):  # check whether label-file exists
                            file_found = True # no exception, because file is found

                            # Eintrag mit UUID erstellen
                            dirs[direct][uuid] = {}

                            # Erstellen von Labelobjekt und hinzufügen zu Liste
                            # Laden der Json-Daten
                            with open(labelfile) as stream:
                                json_data = json.loads(stream.read())
                                json_data = [label_dict["offsetNanos"] for label_dict in json_data]
                            # check if file actually contains labels
                            if json_data==[]:
                                raise ValueError(f"Die label-Datei {labelfile} ist leer.")

                            # Erstellen Objekt
                            dirs[direct][uuid]["label"] = LabelTransferObject("".join([pathToDir,"\\",direct]),
                                                                              "".join([uuid,extension]), uuid,
                                                                              json_data)

                            # Erstellen von Waveobjekt und hinzufügen zu Liste
                            dirs[direct][uuid]["audio"] = AudioTransferObject("".join([pathToDir,"\\",direct]),
                                                                              audiofile.name, uuid)

                            break  # Rausspringen aus Schleife, da eine passende Dateien gefunden wurde

                    if not file_found:
                        raise FileNotFoundError(f"Die WAVE-Datei {uuid} bestitzt keine zugehörige Label-Datei.")
                    accfile =  "{0}\\{1}\\{2}_acc.csv".format(pathToDir, direct, uuid)
                    # check accelerometer data
                    if load_acc:
                        if not os.path.exists(accfile):
                            raise FileNotFoundError(f"Die WAVE-Datei {uuid} bestitzt keine zugehörige Accelerometer"
                                                    f"-Datei.")

                        with open(accfile) as stream:
                            next(stream)
                            try:
                                next(stream)
                            except StopIteration:
                                raise ValueError(f"Die Accelerometer-Datei ist {accfile} leer.")

                        dirs[direct][uuid]["accelerometer"] = AccelerometerTransferObject("{0}\\{1}".
                                                                                      format(pathToDir, direct),
                                                                                      ''.join([uuid, "_acc.csv"]),
                                                                                      uuid)
                    # check whether sampling rates are equal for all files
                    if samplingRateOriginal is not None:
                        samplingRateComp, _ = wav.read(f"{pathToDir}\\{direct}\\{uuid}_mic.wav")
                        _ = None
                        if samplingRateOriginal != samplingRateComp:
                            raise ValueError(f"Die Aufnahme {uuid} hat eine andere Sampling Rate"
                                             f" als {samplingRateRef} und kann daher nicht verwendet werden.")
                    else:
                        samplingRateOriginal, _ = wav.read(f"{pathToDir}\\{direct}\\{uuid}_mic.wav")
                        _ = None
                        samplingRateRef = uuid

                    # check if number of labels are equal for all files
                    if check_labecount and labelCount is None:
                        labelCount = len(json_data)
                        labelCountRef = labelfile
                    elif check_labecount and labelCount != len(json_data):
                        raise ValueError(f"Die label-Datei {labelfile} hat {len(json_data)} Label und\n damit eine "
                                         f" andere Anzahl von Labeln als die Referenzdatei {labelCountRef}.")

            it.close()
            if dirs[direct] == {}:
                raise ValueError(f"Im Directory {direct} sind keine erkennbaren WAVE-Dateien.")

        return dirs

    def loadBaseAudio(self):
        if not os.path.exists(Datalayer.DatalayerInterface.pathBaseAudio):
            os.mkdir(Datalayer.DatalayerInterface.pathBaseAudio)
            raise FileNotFoundError(f"Der Ordner {Datalayer.DatalayerInterface.pathBaseAudio} war nicht existent und wurde erstellt.")
        return self.__loadFromSubdirectory(Datalayer.DatalayerInterface.pathBaseAudio, load_acc=True, check_labecount=True)

    def loadNoiseAudio(self):
        if not os.path.exists(Datalayer.DatalayerInterface.pathNoiseAudio):
            os.mkdir(Datalayer.DatalayerInterface.pathNoiseAudio)
            raise FileNotFoundError(f"Der Ordner {Datalayer.DatalayerInterface.pathNoiseAudio} war nicht existent und wurde erstellt.")
        return self.__loadFromSubdirectory(Datalayer.DatalayerInterface.pathNoiseAudio)

class BaseTransferObject:
    def __init__(self, path, name, uuid):
        self._path = path  # Pfad zu Datei
        self._name = name  # Name der Datei
        self._uuid = uuid  # uuid

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name

    @property
    def uuid(self):
        return self._uuid

    @name.setter
    def name(self, name):
        self._name = name

    @uuid.setter
    def uuid(self, uuid):
        self._uuid = uuid

    @path.setter
    def path(self, path):
        self._path = path

class LabelTransferObject(BaseTransferObject):
    def __init__(self, path, name, uuid, labelOffsets):
        BaseTransferObject.__init__(self, path, name, uuid)
        self.__labelOffsets = labelOffsets  # Offsets für Spur ; [int in nanoseconds, ...]

    @property
    def labelOffsets(self):
        return self.__labelOffsets.copy()

    @property
    def numberOffsets(self):
        return len(self.__labelOffsets)

    @labelOffsets.setter
    def labelOffsets(self, labelOffsets):
        self.labelOffsets = labelOffsets

    def __str__(self):
        return "[ path: {0} , name: {1} , uuid: {2} , labelOffsets: {3}]".format(self._path, self._name, self._uuid,
                                                                                 str(self.__labelOffsets))


class AudioTransferObject(BaseTransferObject):

    def __init__(self, path, name, uuid):
        BaseTransferObject.__init__(self, path, name, uuid)

    def extractAudiorange(self, offsetNanos, seconds):
        sr, audio = self.audio
        _offset = offsetNanos/1000000000 * sr
        audio = audio[ max(int(_offset - sr*seconds/2),0):min(int(_offset + sr*seconds/2),len(audio))]

        if len(audio) < sr*seconds:
            # if the audio is less than required, pad with zeros
            missingAudio =  int(sr*seconds) - len(audio)
            audio = append(audio, zeros(floor(missingAudio/2)))
            audio = append(zeros(ceil(missingAudio/2)), audio)

        return audio

    @property
    def audio(self):
        rate, data = wav.read(f"{self.path}\\{self.name}")
        return (rate, data)

    @property
    def samplingRate(self):
        rate, _ = wav.read(f"{self.path}\\{self.name}")
        return rate

    def __str__(self):
        return "[ path: {0} , name: {1} , uuid: {2}]".format(self._path, self._name, self._uuid)

class AccelerometerTransferObject(BaseTransferObject):

    def __init__(self, path, name, uuid):
        BaseTransferObject.__init__(self, path, name, uuid)

    def extractAccrange(self, offsetNanos, seconds):
        acc = self.acc # returns numpy array
        # values of acc have to be greater 0 for later processing ; values below zero cannot be interpreted
        condition = (offsetNanos-int(seconds/2*1000000000)<=acc[:,0]) & (acc[:,0] <= offsetNanos+int(seconds/2*1000000000))
        return acc[condition,:]

    @property
    def acc(self):
        return loadtxt("{0}\\{1}".format(self.path, self.name), delimiter=',', skiprows=1)

    def __str__(self):
        return "[ path: {0} , name: {1} , uuid: {2}]".format(self._path, self._name, self._uuid)

