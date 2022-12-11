from Controller.Controller import PipelineController
import logging
from os.path import exists
from os import mkdir

class PipelineControllerInterface:

    def __init__(self):
        self.__controller = None


    def start(self):
        if not exists(".\\logs\\"):
            mkdir(".\\logs\\")

        logging.basicConfig(filename=".\\logs\\Server.log", encoding='utf-8', level=logging.ERROR)
        self.__controller = PipelineController()
        self.__controller.runCalculation()

