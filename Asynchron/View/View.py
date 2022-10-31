from Controller.Controller import PipelineController
import logging

class PipelineControllerInterface:

    def __init__(self):
        self.__controller = None


    def start(self):
        logging.basicConfig(filename="./logs/Server.log", encoding='utf-8', level=logging.ERROR)
        self.__controller = PipelineController()
        self.__controller.runCalculation()

