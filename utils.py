# signal processing
from numpy.fft import fft
from numpy import linspace, mean, sqrt, square
from numpy import savetxt
import matplotlib.pyplot as plt
# grpc communication
import GrpcKommunikation.classifications_manager_pb2 as pb2
import GrpcKommunikation.data_pb2 as data_pb2


def fft_display(n, sr, plot=False, name=None):
    nF = fft(n)
    nF = 2*abs(nF)/len(nF)

    xF = linspace(0,sr,len(nF) + 1)
    nF = nF[:int(len(nF)/2)]
    xF = xF[:len(nF)]

    if plot:
        plt.figure()
        if name is not None:
            plt.title(name)
        plt.plot(xF,nF)

        plt.show()
        plt.close()
    return (xF, nF)

def rms(n):
    return sqrt(mean(square(n)))

def job_envelope(sr, audio_data, acc_data):
    """
    :param sr:sampling rate as an integer
    :param audio_data: numpy array with extracted audio data ; dtype=any numeric
    :param acc_data: numpy array with etracted accelerometer data ; dtype= mixed ;
     consists of [time in ns, x-axis, y-axis, z-axis]
    :return: grpc.classifications_manager_pb2.JobDownStream.PushJob
    """
    pushJob = pb2.JobDownstream()
    """
    - metadata:  result.pushJob.job.metadata
    - audiodata:  result.pushJob.job.audiodata
    - accelerometerData:  result.pushJob.job.accelerometerData
    """
    # metadata
    pushJob.pushJob.job.metadata.id.uuid.lsb = 66666  # uint64         #ingorable
    pushJob.pushJob.job.metadata.id.uuid.lsb = 66666  # int64          #ingorable
    pushJob.pushJob.job.metadata.recording.uuid.lsb = 1  # int64   #ingorable
    pushJob.pushJob.job.metadata.recording.uuid.msb = 2  # int64   #ingorable
    pushJob.pushJob.job.metadata.scenario.uuid.lsb = 3  # int64    #ingorable
    pushJob.pushJob.job.metadata.scenario.uuid.msb = 4  # int64    #ingorable
    pushJob.pushJob.job.metadata.step = 2  # uint32   #ignorable
    pushJob.pushJob.job.metadata.sensor.uuid.lsb = 8  # int64      #ingorable
    pushJob.pushJob.job.metadata.sensor.uuid.msb = 8  # int64    #ingorable
    pushJob.pushJob.job.metadata.chunkStartOffsetNano = 2000000000  # uint64   #probably ingorable
    pushJob.pushJob.job.metadata.chunkEndOffsetNano = 4000000000  # uint64    #probably ingorable
    # repeated
    pushJob.pushJob.job.metadata.properties.add().name = "JobEnvelope"  # string #ingorable
    pushJob.pushJob.job.metadata.properties[0].text.value = "Dies ist ein JobEnvelope"  # string  #ingorable
    # audiodata
    pushJob.pushJob.job.audioData.referenceNano = 2000000000  # uint64 in ns
    pushJob.pushJob.job.audioData.sampleRate = sr  # uint32
    pushJob.pushJob.job.audioData.samples = audio_data.tobytes()
    pushJob.pushJob.job.accelerometerData.samples.extend(
        (data_pb2.AccelerometerSample(
            referenceNano=int(line[0]),
            x=float(line[1]),
            y=float(line[2]),
            z=float(line[3])
        ) for line in acc_data if int(line[0]) >= 0)
    )
    return pushJob
