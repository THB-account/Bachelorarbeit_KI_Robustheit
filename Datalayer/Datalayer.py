import json
import os
from scipy.io import wavfile as wav


class DatalayerInterface:
    pathBaseAudio = ".\\Basisgerausche"
    pathNoiseAudio = ".\\Stoergerausche"

    def __init__(self):
        self.__AudioLoadDO = AudioLoadDO()

    def loadBaseAudio(self):
        return self.__AudioLoadDO.loadBaseAudio()

    def loadNoiseAudio(self):
        return self.__AudioLoadDO.loadNoiseAudio()


class AudioLoadDO:
    def __init__(self):
        pass

    def __loadFromSubdirectory(self, pathToDir):
        """
    1. Lade die Liste der Objekte
    2. Enziehe diesen die nötigen Informationen
    3. Erstelle die Objekte

    Die Idee ist für jede Klasse von Störgeräusch einen eigenen Unterordner zu erstellen
    """
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

        for direct in dirs:  # for Fileclasse_x
            it = os.scandir("{0}\\{1}".format(pathToDir,
                                              direct))  # opens a stream/iterator which has to be closed ; This is faster than os.listdir
            # for audiofiles ; it is the basis of the analysis
            for audiofile in it:
                if audiofile.name.endswith(".wav"):
                    file_found = False
                    uuid = audiofile.name.split("_")[0]

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
                            # Erstellen Objekt
                            dirs[direct][uuid]["label"] = LabelTransferObject("{0}\\{1}".format(pathToDir, direct),
                                                                              "{0}{1}".format(uuid,extension), uuid, json_data)

                            # Erstellen von Waveobjekt und hinzufügen zu Liste
                            dirs[direct][uuid]["audio"] = AudioTransferObject("{0}\\{1}".format(pathToDir, direct),
                                                                              audiofile.name, uuid)

                            break  # Rausspringen aus Schleife, da eine passende Dateien gefunden wurde

                    if not file_found:
                        raise Exception("\nDie WAVE-Datei {0} bestitzt keine zugehörige Label-Datei.".format(uuid))

            it.close()

        return dirs

    def loadBaseAudio(self):  # TODO Implementieren, dass keine Subordner füür Basisgeräusche erzeugt werden müssen
        return self.__loadFromSubdirectory(DatalayerInterface.pathBaseAudio)

    def loadNoiseAudio(self):
        return self.__loadFromSubdirectory(DatalayerInterface.pathNoiseAudio)


class LabelTransferObject:
    def __init__(self, path, name, uuid, labelOffsets):
        self.__path = path  # Pfad zu Datei
        self.__name = name  # Name der Datei
        self.__uuid = uuid  # uuid
        self.__labelOffsets = labelOffsets  # Offsets für Spur

    @property
    def path(self):
        return self.__path

    @property
    def name(self):
        return self.__name

    @property
    def uuid(self):
        return self.__uuid

    @property
    def labelOffsets(self):
        return self.__labelOffsets.copy()

    @name.setter
    def name(self, name):
        self.__name = name

    @uuid.setter
    def uuid(self, uuid):
        self.__uuid = uuid

    @labelOffsets.setter
    def labelOffsets(self, labelOffsets):
        self.labelOffsets = labelOffsets

    def __str__(self):
        return "[ path: {0} , name: {1} , uuid: {2} , labelOffsets: {3}]".format(self.__path, self.__name, self.__uuid,
                                                                                 str(self.__labelOffsets))


class AudioTransferObject:

    def __init__(self, path, name, uuid):
        self.__path = path  # path without the name
        self.__name = name  # name of file
        self.__uuid = uuid  # hex identificator

    @property
    def path(self):
        return self.__path

    @property
    def name(self):
        return self.__name

    @property
    def uuid(self):
        return self.__uuid

    @property
    def audio(self):
        rate, data = wav.read("./{0}/{1}".format(self.path, self.name))
        return (rate, data)

    @name.setter
    def name(self, name):
        self.__name = name

    @uuid.setter
    def uuid(self, uuid):
        self.__uuid = uuid

    def __str__(self):
        return "[ path: {0} , name: {1} , uuid: {2}]".format(self.__path, self.__name, self.__uuid)