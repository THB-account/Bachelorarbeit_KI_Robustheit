# Data transformation
import Model.PipelineContainer
from Model.Pipeline import StartElementVO, PitchShiftVO, FrequencyAugmentationVO, NoiseInjectionVO, AudioTyping
from numpy import arange
# File handling and consistancy checks
from os.path import exists
from yaml import load, Loader
import re
# Threading and Data transmission
from concurrent import futures
import queue
import asyncio
# grpc and proto-python files
import grpc
import GrpcKommunikation.classifications_manager_pb2_grpc as classifications_manager_pb2_grpc
import GrpcKommunikation.logging_collector_pb2_grpc as logging_collector_pb2_grpc
import GrpcKommunikation.Services as Services

class PipelineController:

    def __init__(self):
        self.__pipelineContainer = None
        classInQueue = queue.Queue()
        classOutQueue = queue.Queue()
        self.__initializePipeline(classOutQueue,classInQueue)
        self.__pool = futures.ThreadPoolExecutor(max_workers=11)  # 11 = 10 + app Thread ; No idea why 10
        self.__server = grpc.server(self.__pool)
        # add services to server
        classifications_manager_pb2_grpc.add_ClassificationsManagerServicer_to_server(
            Services.ClassificationManager(classOutQueue,classInQueue), self.__server)
        logging_collector_pb2_grpc.add_LoggingCollectorServicer_to_server(Services.LoggingCollector(),
                                                                 self.__server)

        self.__server.add_insecure_port('[::]:5001')
        

    def __initializePipeline(self, classOutQueue, classInQueue):
        # Einlesen von Werten des .ini-Files
        if not exists("config.yaml"):
            with open("config.yaml",'w') as stream:
                stream.write("""
# Shifted den Frequenzbereich um n% nach Rechts
# muss 0 als Wert enthalten für Fehlerberechnung
pitchshiftPercents : "[-1,0,1]"

# Anzahl der Abschnitte für das Entfernen von Frequenzanteilen
# 5 würde in [0,0.2,0.4,0.6,0.8] resultieren, wobei ein Intervall und der
# nächsthöheren Nummer besteht e.g. (0-0.2),(0.2-0.4)...(0.8-1)
# 0 ist ein valider Wert und diese Dimension wird in der Modifikation von Aufnahmen nicht berücksichtigt
freqSteps : 5

# noiseSteps ist die Anzahl der Elemente in dem Modifikationsarray
# 5 würde [0,0.2,0.4,0.6,0.8,1] entsprechen --> Schrittweite: 1/n
# 0 ist ein valider Wert und diese Dimension wird in der Modifikation von Aufnahmen nicht berücksichtigt
noiseSteps : 5
# Wie Stark das letztendlich überlagerte Geräusch am Ende sein soll
# entspricht dem finalen Element der Liste --> [0,0.2,...,2]
# 0 ist ein valider Wert und diese Dimension wird in der Modifikation von Aufnahmen nicht berücksichtigt
noiseAmplitude : 1

                """)

            raise FileNotFoundError("config.yaml fehlt. Default Version wurde erstellt.")
        # TODO Regex check
        with open("config.yaml",'r') as stream:
            confData = load(stream, Loader) # yaml module

        def safeCast (n, error):
            try:
                return n()
            except ValueError:
                raise ValueError(error)
        confData["freqSteps"] = safeCast(lambda: int(confData["freqSteps"]), "freqSteps muss eine ganze Zahl groesser gleich Null sein.")
        confData["noiseSteps"] = safeCast(lambda: int(confData["noiseSteps"]), "noiseSteps muss eine ganze Zahl groesser gleich Null sein.")
        confData["noiseAmplitude"] = safeCast(lambda: float(confData["noiseAmplitude"]), "noiseAmp muss eine Kommazahl groesser gleich Null sein.")


        # {'pitchshiftPercents': '[-1,0,1]', 'freqSteps': 5, 'noiseSteps': 5, 'noiseAmp': 1}
        # TODO abfangen von invaliden Werten
        # check if values fit criteria
        if confData["freqSteps"] < 0:
            raise ValueError("freqSteps muss eine ganze Zahl groesser gleich Null sein.")
        if confData["noiseSteps"] < 0:
            raise ValueError("noiseSteps muss eine ganze Zahl groesser gleich Null sein.")
        if confData["noiseAmplitude"] < 0:
            raise ValueError("noiseAmp muss eine ganze Zahl groesser gleich Null sein.")
        # any form of [number*, 0, number*] and whitespace characters fitted in
        # number = "[0-9]|-?[1-9][0-9]*"
        regex ="\s*\[\s*(\s*(0|-?[1-9][0-9]*)\s*,\s*)*\s*0\s*(\s*,\s*(0|-?[1-9][0-9]*)\s*)*\s*\]\s*"
        if confData["pitchshiftPercents"] is None or  re.compile(
            regex
        ).match(str(confData["pitchshiftPercents"])) is None:
            raise ValueError("pitchshiftPercents muss wie folgt aussehen [...,-2,-1,0,1,2,...], wobei \"... für Nummern steht. "
                             "Auch muss der Wert 0 enthalten sein\"")
        # remove string components and cast to integer
        confData["pitchshiftPercents"] = confData["pitchshiftPercents"].replace('[', '').replace(']', '')
        confData["pitchshiftPercents"] = list(map(int, confData["pitchshiftPercents"].split(',')))
        # remove duplicates and sort list from lowest to highest
        confData["pitchshiftPercents"] = sorted(list(set(confData["pitchshiftPercents"])))
        # cast to integer, to prevent passing of strings

        frequencyCutouts = arange(confData["freqSteps"]+1)/confData["freqSteps"]
        if confData["noiseAmplitude"]!=0 and confData["noiseSteps"] >0: # no division of zero
            noisePercents = arange(confData["noiseSteps"]+1) / confData["noiseSteps"]*confData["noiseAmplitude"]
        else:
            noisePercents = arange(1) # no injection of noise, arange results in = [0]


        pEl = [
            StartElementVO(baseElement=None, nextPipeElement=None), # standard dtype np.single=float
            FrequencyAugmentationVO(nextPipeElement=None, useCache=True,
                                    valueRange=frequencyCutouts),
            PitchShiftVO(nextPipeElement=None, useCache=True, valueRange=confData["pitchshiftPercents"]),
            NoiseInjectionVO(nextPipeElement=None, useCache=False,
                             valueRange=noisePercents,
                             noise=None, sr=None),
            AudioTyping(nextPipeElement=None, useCache=False)
        ]

        self.__pipelineContainer = Model.PipelineContainer.PipelineContainerVO(pEl, classOutQueue, classInQueue)

    def runCalculation(self):
        self.__server.start()
        app_future = self.__pool.submit(asyncio.run, self.__pipelineContainer.run())
        app_future.result() # wait for calc to finish
        # shutdown server
        self.__server.stop(grace=0)
        #shutdown pool
        self.__pool.shutdown(wait=False)
        self.__pipelineContainer.evalCollection.save()




        

