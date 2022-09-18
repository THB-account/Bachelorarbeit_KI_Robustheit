import grpc
import classifications_manager_pb2 as pb2
import classifications_manager_pb2_grpc
import logging_collector_pb2 as pb2_log
import logging_collector_pb2_grpc
import data_pb2

if __name__=="__main__":
    print("branch outcomes identity - initcompleting\n")
    initComplete = pb2.OutcomeUpstream()
    pull =         pb2.OutcomeUpstream()
    identify =     pb2.OutcomeUpstream()
    print("initComplete og: ", type(initComplete))
    print("pullOutcome  og: ", type(pull))
    print("identify  og: ", type(identify))

    print("\n")
    t = pb2.PullOutcome()
    test = pb2.OutcomeUpstream(pullOutcome=pb2.PullOutcome())

    print("test:",test)

    temp = dir(t)
    for x in temp:
        print(x)
    print("\n",t)

    print("\n")

    identify.identify.SetInParent()

    initComplete.initComplete.session.lsb = 1
    initComplete.initComplete.session.msb = 1

    pull= pull.pullOutcome.SetInParent()
    print("initComplete: " + str(initComplete))
    print("pullOutcome: " + str(pull))
    print("identify: " + str(identify))
