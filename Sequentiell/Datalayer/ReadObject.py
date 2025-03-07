import json
import csv
import os
from scipy.io import wavfile as wav
from numpy import loadtxt, extract
import Datalayer.Datalayer as Datalayer

class AudioLoadDO:
    def __init__(self):
        pass

    def __loadFromSubdirectory(self, pathToDir, load_acc=False):
        # Dateiendungen. Diese haben eine Priorität von Links nach Rechts
        file_extensions = ["_labels_approved.json", "_labels_modified.json", "_labels.json"]

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
            dirs["\\"] = {}

        for direct in dirs:  # for Fileclass_n
            it = os.scandir("{0}\\{1}".format(pathToDir,
                                              direct))  # opens a stream/iterator which has to be closed ; This is faster than os.listdir
            # for audiofiles ; it is the basis of the analysis
            for audiofile in it:
                if audiofile.name.endswith(".wav"): # if file exists
                    file_found = False
                    uuid = audiofile.name.split("_")[0] # extract identifier for all files

                    for extension in file_extensions:  # check for label
                        labelfile = "{0}\\{1}\\{2}{3}".format(pathToDir, direct, uuid, extension)
                        if os.path.exists(labelfile):  # check wheter label file exists
                            file_found = True

                            # Eintrag mit UUID erstellen
                            dirs[direct][uuid] = {}

                            # Erstellen von Labelobjekt und hinzufügen zu Liste
                            # Laden der Json-Daten
                            with open(labelfile) as stream:
                                json_data = json.loads(stream.read())
                                json_data = [label_dict["offsetNanos"] for label_dict in json_data]

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
                        raise Exception("Die WAVE-Datei {0} bestitzt keine zugehörige Label-Datei.".format(uuid))
                    accfile =  "{0}\\{1}\\{2}_acc.csv".format(pathToDir, direct, uuid)
                    if load_acc and os.path.exists(accfile):
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

            it.close()

        return dirs

    def loadBaseAudio(self):
        if not os.path.exists(Datalayer.DatalayerInterface.pathBaseAudio):
            os.mkdir(Datalayer.DatalayerInterface.pathBaseAudio)
            raise FileNotFoundError(f"Der Ordner {Datalayer.DatalayerInterface.pathBaseAudio} war nicht existent und wurde erstellt.")
        return self.__loadFromSubdirectory(Datalayer.DatalayerInterface.pathBaseAudio, load_acc=True)

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
        return audio

    @property
    def audio(self):
        rate, data = wav.read("{0}\\{1}".format(self.path, self.name))
        return (rate, data)

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

