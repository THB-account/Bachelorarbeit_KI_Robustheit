import csv
import os
import Datalayer.Datalayer as Datalayer
from matplotlib.pyplot import close
from numpy import save


class DataWriteDO:

    def __init__(self):
        pass

    # create direcotries
    def __createDirectories(self, path):
        tempPath = Datalayer.DatalayerInterface.pathEvalData
        for direct in path.split('\\')[:-1]:
            tempPath += "\\{0}".format(direct)
            if not os.path.exists(tempPath):
                os.mkdir(tempPath)

    def savePredictions(self,predictions,config):
        if not os.path.exists(Datalayer.DatalayerInterface.pathEvalData):
            os.mkdir(Datalayer.DatalayerInterface.pathEvalData)
        self.__createDirectories(config["fname"])
        config["fname"] = "\\".join([Datalayer.DatalayerInterface.pathEvalData, config["fname"]])
        save(config["fname"],predictions, allow_pickle=False)




    # for saving visualizations at the end of calculations
    def saveFigure(self, figure, config):
        """
        example config dictionary:
        {"fname": "{0}\\{2}\\{1}_{0}".format(self._evaluationSpace.name, self._fileName,self._subfolder),
                            "dpi": "figure",
                            "bbox_inches": None,
                            "pad_inches": 0.1}
        """
        # if Ergebnisse-Directory non-existent create it
        if not os.path.exists(Datalayer.DatalayerInterface.pathEvalData):
            os.mkdir(Datalayer.DatalayerInterface.pathEvalData)
        self.__createDirectories(config["fname"])
        config["fname"] = "\\".join([Datalayer.DatalayerInterface.pathEvalData, config["fname"]])
        figure.savefig(**config)
        close(figure)
    # saving the responding csv data to a vizualization
    def saveCSVData(self,path, header, data):
        if not os.path.exists(Datalayer.DatalayerInterface.pathEvalData):
            os.mkdir(Datalayer.DatalayerInterface.pathEvalData)

        self.__createDirectories(path)
        with open("{0}\\{1}".format(Datalayer.DatalayerInterface.pathEvalData, path), 'w', newline="", encoding='UTF8') as stream:
            writer = csv.writer(stream, delimiter=",")

            # write header
            writer.writerow(header)
            writer.writerows(data)
