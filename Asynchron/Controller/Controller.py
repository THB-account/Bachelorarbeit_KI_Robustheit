# Data transformation
import Model.PipelineContainer
from Model.Pipeline import StartElementVO, PitchShiftVO, FrequencyAugmentationVO, NoiseInjectionVO, AudioTyping
from numpy import arange
from math import ceil, floor, log
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
# for error control
import logging

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
# Wenn die Aufnahmen im Ordner "Basisgerausche" auf deren durchschnittliches Maximum normalisiert werden sollen, auf True
# setzen, ansonsten auf False.
basisaudioNormalisierung : False

# Wenn die Störgeräusche im Ordner "Stoergerausche" im Verhältnis zum Basisgerausch normalisiert werden sollen auf True
# setzen, ansonsten auf False.
# Berechnungsformel: verarbeitetes Signal = Max(Basisgerausch)/Max(Noise) * Noise * stellwert[i] + Basisgerausch 
noiseNormalisierung : False

                
# Shifted den Frequenzbereich um pitchshiftSchrittweite% in den hoch- oder niedrigfrequenten.
# Der Wert 0 würde dazu führen, dass die Modifikationsdimension nicht berücksichtig wird und
# die Stellwerteliste 0 erstellt wird.
pitchshiftSchrittweite: 0.1

# Der Wert 3 würde zur Erstellung der Liste von Verschiebungsstufen [-3,-2,-1,0,1,2,3] führen. Die Schrittweite ist 1.
# Der Wert 0 würde dazu führen, dass die Modifikationsdimension nicht berücksichtig wird und
# die Stellwerteliste 0 erstellt wird.
pitchshiftSchritte: 10


# Anzahl der Abschnitte für das Entfernen von Frequenzanteilen
# 5 würde in [0,0.2,0.4,0.6,0.8,1] resultieren, wobei ein Intervall und der
# nächsttieferen Nummer besteht e.g. (0,0) (0-0.2),(0.2-0.4)...(0.8-1). Die Schrittweite ist 1/n.
# 0 ist ein valider Wert und würde dazu führen, dass diese Dimension in der Modifikation von Aufnahmen 
# nicht berücksichtigt wird. Die entsprechende Liste wäre [0].
frequenzSchritte : 5

# noiseSchritte ist die Anzahl der Elemente in dem Modifikationsarray.
# 5 würde [0,0.2,0.4,0.6,0.8,1] entsprechen --> Schrittweite: 1/n
# 0 ist ein valider Wert, wodurch diese Dimension nicht in der Modifikation von Aufnahmen berücksichtigt wird.
noiseSchritte : 5
# noiseAmplitude bestimmt wie stark das letztendlich überlagerte Geräusch am Ende sein soll.
# noiseAmplitude entspricht dem finalen Element der Liste --> [0,0.2,...,2] und bestimmt die Schrittweite
# in Form von noiseAmplitude/noiseSchritte.
# 0 ist ein valider Wert, wodurch diese Dimension nicht in der Modifikation von Aufnahmen berücksichtigt wird.
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
        confData["noiseSchritte"] = safeCast(lambda: int(confData["noiseSchritte"]), "noiseSchritte muss eine ganze Zahl groesser gleich Null sein.")
        confData["noiseAmplitude"] = safeCast(lambda: float(confData["noiseAmplitude"]), "noiseAmplitude muss eine Kommazahl groesser gleich Null sein.")
        confData["pitchshiftSchritte"] = safeCast(lambda: int(confData["pitchshiftSchritte"]), "pitchshiftSchritte muss eine ganze Zahl groesser gleich Null sein.")
        confData["pitchshiftSchrittweite"] = safeCast(lambda: float(confData["pitchshiftSchrittweite"]), "pitchshiftSchrittweite muss eine Kommazahl (Bsp. 0.4) groesser gleich Null sein.")

        # check if values fit criteria
        if confData["frequenzSchritte"] < 0:
            raise ValueError("frequenzSchritte muss eine ganze Zahl groesser gleich Null sein.")
        if confData["noiseSchritte"] < 0:
            raise ValueError("noiseSchritte muss eine ganze Zahl groesser gleich Null sein.")
        if confData["noiseAmplitude"] < 0:
            raise ValueError("noiseAmp muss eine ganze Zahl groesser gleich Null sein.")
        if confData["pitchshiftSchritte"] < 0:
            raise ValueError("noiseAmp muss eine ganze Zahl groesser gleich Null sein.")
        if confData["pitchshiftSchrittweite"] < 0:
            raise ValueError("noiseAmp muss eine Kommazahl groesser gleich Null sein.")

        """
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
        """

        if confData["pitchshiftSchritte"]>0 and confData["pitchshiftSchrittweite"]>0:
            pitchshiftKeys = arange(-confData["pitchshiftSchritte"],confData["pitchshiftSchritte"]+1,1)
            # you could calculate the result and round on a logarithmic scale
            # but a comparison is easier to implement and the calculation only happens once
            if abs(confData["pitchshiftSchrittweite"]-ceil(log(2,confData["pitchshiftSchrittweite"]))) <  abs(confData["pitchshiftSchrittweite"]-floor(log(2,confData["pitchshiftSchrittweite"]))):
                bins = ceil(log(2,1+confData["pitchshiftSchrittweite"]/100))
            else:
                bins = floor(log(2,1+confData["pitchshiftSchrittweite"]/100))
        else:
            pitchshiftKeys = arange(1) # arange to create np.array without importing, functionality used later on
            # due to bins not needing to be set i use the standard value, which is equal to 0.1 % percent per octave
            bins = 70


        if confData["frequenzSchritte"] > 0:
            frequencyCutouts = arange(confData["frequenzSchritte"]+1)/confData["frequenzSchritte"]
        else:
            frequencyCutouts = arange(1)
        if confData["noiseAmplitude"]!=0 and confData["noiseSchritte"] >0: # no division of zero
            noisePercents = arange(confData["noiseSchritte"]+1) / confData["noiseSchritte"]*confData["noiseAmplitude"]
        else:
            noisePercents = arange(1) # no injection of noise, arange results in = [0]


        pEl = [
            StartElementVO(baseElement=None, nextPipeElement=None), # standard dtype np.single=float
            FrequencyAugmentationVO(nextPipeElement=None, useCache=True,
                                    valueRange=frequencyCutouts),
            PitchShiftVO(nextPipeElement=None, useCache=True, valueRange=pitchshiftKeys, bins=bins),
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




        

