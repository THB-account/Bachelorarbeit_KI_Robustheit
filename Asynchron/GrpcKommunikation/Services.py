# service definition files, for implementing the service
import GrpcKommunikation.classifications_manager_pb2 as pb2
import GrpcKommunikation.classifications_manager_pb2_grpc as classifications_manager_pb2_grpc
import GrpcKommunikation.logging_collector_pb2 as pb2_log
import GrpcKommunikation.logging_collector_pb2_grpc as logging_collector_pb2_grpc
# logging, so that error messages dont mess with application
import logging
# utils used for creating message envelope
from utils import interpretResult



class ClassificationManager(classifications_manager_pb2_grpc.ClassificationsManager):

    def __init__(self, outqueue, inqueue):
        self.__classOutQueue = outqueue # gets job from this (sr, audio(n), acc(n,4))
        self.__classInQueue = inqueue   # puts result into this

    def jobs(self, request_iterator, context):
        for request in request_iterator:
            if request.HasField("init"):
                identify = pb2.JobDownstream()
                identify.identify.SetInParent()
                yield identify
            elif request.HasField("identity"):
                identity = pb2.JobDownstream()
                identity.initComplete.session.lsb = 1
                identity.initComplete.session.msb = 1
                yield identity
            elif request.HasField("pullJob"):
                # get job
                job = self.__classOutQueue.get()
                # process job and send to application
                yield job
            else:

                logging.error(f"unexpected value in ClassificationManager.jobs: {request}")


    def outcomes(self, request_iterator, context):
        for request in request_iterator:
            if request.HasField("init"):
                identify = pb2.OutcomeUpstream()
                identify.identify.SetInParent()
                yield identify
            elif request.HasField("identity"):
                initComplete = pb2.OutcomeUpstream()
                initComplete.initComplete.session.lsb = 1
                initComplete.initComplete.session.msb = 1
                yield initComplete
                pull = pb2.OutcomeUpstream(pullOutcome=pb2.PullOutcome())
                yield pull
            elif request.HasField("pushOutcome"):

                #with open("classResult.txt", 'a') as stream:
                #    stream.write("\n" + str([[x.number.value for x in request.pushOutcome.outcome.jobMetadata.properties]
                #                            , interpretResult(request.pushOutcome.outcome.predictions)]))
                # push result of request into queue for application
                index = [x.number.value-1 for x in request.pushOutcome.outcome.jobMetadata.properties]
                confidence = interpretResult([(prediction.confidence, prediction.result, prediction.pointOfInterestOffsetNano)
                for prediction in request.pushOutcome.outcome.predictions])


                self.__classInQueue.put([index, confidence])
                # request next Job pull
                pull = pb2.OutcomeUpstream(pullOutcome=pb2.PullOutcome())
                yield pull
            else:
                logging.error(f"unexpected value in ClassificationManager.outcomes: {request}")

    def list(self, request_iterator, context):
        return pb2.ListReplyMessage(empty=pb2.ListEmptyMessage())

    @property
    def classOutQueue(self):
        return self.__classOutQueue

    @property
    def classInQueue(self):
        return self.__classInQueue


class LoggingCollector(logging_collector_pb2_grpc.LoggingCollector):
    def logs(self,request_iterator, context):
        for request in request_iterator:
            if request.HasField("init"):
                identify = pb2_log.LoggingUpstream()
                identify.identify.SetInParent()
                yield identify
            elif request.HasField("identity"):
                initComplete = pb2_log.LoggingUpstream()
                initComplete.initComplete.session.lsb = 123
                initComplete.initComplete.session.msb = 456
                yield initComplete
            elif request.HasField("pushLogEvent"):
                pullLogEvent = pb2_log.LoggingUpstream()
                pullLogEvent.pullLogEvent.SetInParent()
                yield pullLogEvent
            else:
                logging.error(f"unexpected value in LoggingCollector.logs: {request}")
