# Data transformation
import Model.PipelineContainer
from Model.Pipeline import StartElementVO, PitchShiftVO, FrequencyAugmentationVO, NoiseInjectionVO
from numpy import arange
# File handling
from os.path import exists
from yaml import load, Loader
# Threading and Data transmission
from concurrent import futures
import queue
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
pitchshiftPercents : "[-1,0,1]"

# Anzahl der Abschnitte für das Entfernen von Frequenzanteilen
# 5 würde in [0,0.2,0.4,0.6,0.8] resultieren, wobei ein Intervall und der
# nächsthöheren Nummer besteht e.g. (0-0.2),(0.2-0.4)...(0.8-1)
freqSteps : 5

# noiseSteps ist die Anzahl der Elemente in dem Modifikationsarray
# 5 würde [0,0.2,0.4,0.6,0.8,1] entsprechen --> Schrittweite: 1/n
noiseSteps : 5
# Wie Stark das letztendlich überlagerte Geräusch am Ende sein soll
# entspricht dem finalen Element der Liste --> [0,0.2,...,2]
noiseAmp : 1

                """)

            raise FileNotFoundError("config.yaml fehlt. Default Version wurde erstellt.")

        with open("config.yaml",'r') as stream:
            confData = load(stream, Loader) # yaml module
        # {'pitchshiftPercents': '[-1,0,1]', 'freqSteps': 5, 'noiseSteps': 5, 'noiseAmp': 1}
        confData["pitchshiftPercents"] = confData["pitchshiftPercents"].replace('[','').replace(']','')
        confData["pitchshiftPercents"] = list(map(int, confData["pitchshiftPercents"].split(',') ))

        pEl = [
            StartElementVO(baseElement=None, nextPipeElement=None), # standard dtype np.single=float
            FrequencyAugmentationVO(nextPipeElement=None, useCache=True,
                                    valueRange=arange(confData["freqSteps"])/confData["freqSteps"]),
            PitchShiftVO(nextPipeElement=None, useCache=True, valueRange=confData["pitchshiftPercents"]),
            NoiseInjectionVO(nextPipeElement=None, useCache=False,
                             valueRange=arange(confData["noiseSteps"]+1) / confData["noiseSteps"]*confData["noiseAmp"],
                             noise=None, sr=None)
        ]

        self.__pipelineContainer = Model.PipelineContainer.PipelineContainerVO(pEl, classOutQueue, classInQueue)

    def runCalculation(self):
        self.__server.start()
        app_future = self.__pool.submit(self.__pipelineContainer.run)
        app_future.result() # wait for calc to finish
        # shutdown server
        self.__server.stop(grace=0)
        #shutdown pool
        self.__pool.shutdown(wait=False)
        self.__pipelineContainer.evalCollection.save()




        

