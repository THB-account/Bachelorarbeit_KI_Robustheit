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
# Wenn die Aufnahmen im Ordner "Basisgerausche" auf deren durchschnittliches Maximum normalisiert werden sollen auf True
# setzen, ansonsten auf False setzen
basisaudioNormalisierung : False

# Wenn die Störgeräusche im Ordner "Stoergerauschen" im Verhältnis zum Basisgerausch normalisiert werden sollen auf True
# setzen, ansonsten auf False setzen
# Berechnungsformel: verarbeitetes Signal = RMS(Basisgerausch)/RMS(Noise) * Noise * stellwert[i] + Basisgerausch
# wobei Signal Noise Ratio = RMS(Basisgerausch)/RMS(Noise)
# durch RMS(Basisgerausch)/RMS(Noise) * Noise ist Noise auf die Energie des Signals normalisiert 
noiseNormalisierung : False

                
# Shifted den Frequenzbereich um n% nach Rechts
# muss 0 als Wert enthalten für Fehlerberechnung
pitchshiftProzente : "[-1,0,1]"

# Anzahl der Abschnitte für das Entfernen von Frequenzanteilen
# 5 würde in [0,0.2,0.4,0.6,0.8] resultieren, wobei ein Intervall und der
# nächsthöheren Nummer besteht e.g. (0-0.2),(0.2-0.4)...(0.8-1)
# 0 ist ein valider Wert und diese Dimension wird in der Modifikation von Aufnahmen nicht berücksichtigt
frequenzSchritte : 5

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

        def safeCast (n, error, check=lambda:True):
            if check():
                try:
                    return n()
                except ValueError:
                    raise ValueError(error)
            else:
                raise ValueError(error)

        confData["basisaudioNormalisierung"] = safeCast(lambda: bool(confData["basisaudioNormalisierung"])
                                                        , "basisaudioNormalisierung muss entweder der Wert True oder False sein."
                                                        , lambda: isinstance(confData["basisaudioNormalisierung"],bool))
        confData["noiseNormalisierung"] = safeCast(lambda: bool(confData["noiseNormalisierung"])
                                                   , "noiseNormalisierung muss entweder der Wert True oder False sein."
                                                   , lambda: isinstance(confData["noiseNormalisierung"],bool))
        confData["frequenzSchritte"] = safeCast(lambda: int(confData["frequenzSchritte"]), "frequenzSchritte muss eine ganze Zahl groesser gleich Null sein.")
        confData["noiseSteps"] = safeCast(lambda: int(confData["noiseSteps"]), "noiseSteps muss eine ganze Zahl groesser gleich Null sein.")
        confData["noiseAmplitude"] = safeCast(lambda: float(confData["noiseAmplitude"]), "noiseAmp muss eine Kommazahl groesser gleich Null sein.")


        # check if values fit criteria
        if confData["frequenzSchritte"] < 0:
            raise ValueError("frequenzSchritte muss eine ganze Zahl groesser gleich Null sein.")
        if confData["noiseSteps"] < 0:
            raise ValueError("noiseSteps muss eine ganze Zahl groesser gleich Null sein.")
        if confData["noiseAmplitude"] < 0:
            raise ValueError("noiseAmp muss eine ganze Zahl groesser gleich Null sein.")
        # any form of [number*, 0, number*] and whitespace characters fitted in
        # number = "[0-9]|-?[1-9][0-9]*"
        regex ="\s*\[\s*(\s*(0|-?[1-9][0-9]*)\s*,\s*)*\s*0\s*(\s*,\s*(0|-?[1-9][0-9]*)\s*)*\s*\]\s*"
        if confData["pitchshiftProzente"] is None or  re.compile(
            regex
        ).match(str(confData["pitchshiftProzente"])) is None:
            raise ValueError("pitchshiftProzente muss wie folgt aussehen [...,-2,-1,0,1,2,...], wobei \"... für Nummern steht. "
                             "Auch muss der Wert 0 enthalten sein\"")
        # remove string components and cast to integer
        confData["pitchshiftProzente"] = confData["pitchshiftProzente"].replace('[', '').replace(']', '')
        confData["pitchshiftProzente"] = list(map(int, confData["pitchshiftProzente"].split(',')))
        # remove duplicates and sort list from lowest to highest
        confData["pitchshiftProzente"] = sorted(list(set(confData["pitchshiftProzente"])))
        # cast to integer, to prevent passing of strings

        frequencyCutouts = arange(confData["frequenzSchritte"]+1)/confData["frequenzSchritte"]
        if confData["noiseAmplitude"]!=0 and confData["noiseSteps"] >0: # no division of zero
            noisePercents = arange(confData["noiseSteps"]+1) / confData["noiseSteps"]*confData["noiseAmplitude"]
        else:
            noisePercents = arange(1) # no injection of noise, arange results in = [0]


        pEl = [
            StartElementVO(baseElement=None, nextPipeElement=None), # standard dtype np.single=float
            FrequencyAugmentationVO(nextPipeElement=None, useCache=True,
                                    valueRange=frequencyCutouts),
            PitchShiftVO(nextPipeElement=None, useCache=True, valueRange=confData["pitchshiftProzente"]),
            NoiseInjectionVO(nextPipeElement=None, useCache=False,
                             valueRange=noisePercents,
                             noise=None, sr=None, normalization=confData["noiseNormalisierung"]),
            AudioTyping(nextPipeElement=None, useCache=False)
        ]

        self.__pipelineContainer = Model.PipelineContainer.PipelineContainerVO(pEl, classOutQueue, classInQueue
                                                                               ,normalization=
                                                                               confData["basisaudioNormalisierung"])

    def runCalculation(self):
        self.__server.start()
        app_future = self.__pool.submit(asyncio.run, self.__pipelineContainer.run())
        app_future.result() # wait for calc to finish
        # shutdown server
        self.__server.stop(grace=0)
        #shutdown pool
        self.__pool.shutdown(wait=False)
        self.__pipelineContainer.evalCollection.save()




        

