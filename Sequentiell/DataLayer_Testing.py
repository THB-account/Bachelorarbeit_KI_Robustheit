# Press the green button in the gutter to run the script.
import Datalayer.Datalayer
from Datalayer.Datalayer import *
import os
from utils import job_envelope
from numpy import savetxt

service_test=True

if __name__ == '__main__':
    print("Momentanes Arbeitsverzeichnis:  ", os.getcwd())

    # Unterste Elemente der Klasse
    audioTO = Datalayer.Datalayer.ReadObject.AudioTransferObject("Test/Test", "meinName", "meineUUID")
    print(audioTO.path, "  ", audioTO.name, "   ", audioTO.uuid)

    # Erstellen des Interfaces und Laden der Dateien
    dl = DatalayerInterface()
    temp = dl.loadBaseAudio()


    print("\nAusgabe der einzelnen Label und Audioobjekte\n")
    # durchgehen der geladenen Dateien und Ausgabe
    for direct in temp:
        for uuid in temp[direct]:
            print("\n{0}\n{1}\n{2}".format( str(temp[direct][uuid]["audio"] ) , str( temp[direct][uuid]["label"] ),
                                            str(temp[direct][uuid]["accelerometer"])) )

    print("\nAusgabe des Kollektionsobjekts:\n")
    print(str(temp))
    temp_audio = next(iter( next(iter(   temp.items() ))[1].items() ))[1]["audio"]
    temp_label = next(iter( next(iter(   temp.items() ))[1].items() ))[1]["label"]
    print("\nAudio der erst beliebigen Datei\n{0}".format( temp_audio.audio[1][40000:40005]  )  )
    print("Audiorange: ", temp_audio.extractAudiorange(3*10**9, 2)[:10])
    temp_acc = next(iter(next(iter(temp.items()))[1].items()))[1]["accelerometer"]
    print("\nAccelerometer der erst beliebigen Datei\n{0}".format(temp_acc.acc[:10]))
    print("Accrange: ", temp_acc.extractAccrange(3 * 10 ** 9, 2)[:10])

    savetxt("extractedSample.txt", temp_audio.extractAudiorange(temp_label.labelOffsets[0],2))

    temp = dl.loadNoiseAudio()


    print("\nAusgabe der einzelnen Label und Audioobjekte für Noise\n")
    # durchgehen der geladenen Dateien und Ausgabe
    for direct in temp:
        for uuid in temp[direct]:
            print("\n{0}\n{1}".format(str(temp[direct][uuid]["audio"]), str(temp[direct][uuid]["label"])))

    print("\nAusgabe des Kollektionsobjekts:\n")
    print(str(temp))

