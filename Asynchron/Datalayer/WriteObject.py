import csv
import os
import Datalayer.Datalayer as Datalayer
from matplotlib.pyplot import close


class DataWriteDO:

    def __init__(self):
        pass

    def __createDirs(self, path):
        tempPath = Datalayer.DatalayerInterface.pathEvalData
        for direct in path.split('\\')[:-1]:
            tempPath += "\\{0}".format(direct)
            if not os.path.exists(tempPath):
                os.mkdir(tempPath)

    def saveFigure(self, figure, config):
        if not os.path.exists(Datalayer.DatalayerInterface.pathEvalData):
            os.mkdir(Datalayer.DatalayerInterface.pathEvalData)
        self.__createDirs(config["fname"])
        config["fname"] = "\\".join([Datalayer.DatalayerInterface.pathEvalData, config["fname"]])
        figure.savefig(**config)
        close(figure)

    def saveCSVData(self,path, header, data):
        if not os.path.exists(Datalayer.DatalayerInterface.pathEvalData):
            os.mkdir(Datalayer.DatalayerInterface.pathEvalData)

        self.__createDirs(path)
        with open("{0}\\{1}".format(Datalayer.DatalayerInterface.pathEvalData, path), 'w', newline="", encoding='UTF8') as stream:
            writer = csv.writer(stream, delimiter=",")

            # write header
            writer.writerow(header)
            writer.writerows(data)
