import Datalayer.ReadObject as ReadObject
import Datalayer.WriteObject as WriteObject

class DatalayerInterface:
    # Read paths
    pathBaseAudio = ".\\Basisgerausche"
    pathNoiseAudio = ".\\Stoergerausche"
    # Write paths
    pathEvalData = ".\\Ergebnisse"

    def __init__(self):
        self.__audioLoadDO = ReadObject.AudioLoadDO()
        self.__dataWriteDO = WriteObject.DataWriteDO()

    def loadBaseAudio(self):
        return self.__audioLoadDO.loadBaseAudio()

    def loadNoiseAudio(self):
        return self.__audioLoadDO.loadNoiseAudio()

    def saveFigure(self, figure, config): # path is defined in config as "fname"
        self.__dataWriteDO.saveFigure(figure, config)

    def saveCSVData(self, path, header, data):
        self.__dataWriteDO.saveCSVData(path, header, data)

    def savePredictions(self, predictions, config):
        self.__dataWriteDO.savePredictions(predictions, config)



