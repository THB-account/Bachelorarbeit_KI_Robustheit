from Controller.Controller import PipelineController
import logging

class PipelineControllerInterface:

    def __init__(self):
        self.__controller = PipelineController()


    def start(self):
        logging.basicConfig(filename='application.log', encoding='utf-8', level=logging.ERROR)
        self.__controller.runCalculation()

