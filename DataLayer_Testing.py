# Press the green button in the gutter to run the script.
from Datalayer.Datalayer import *
import os

if __name__ == '__main__':
    print("Momentanes Arbeitsverzeichnis:  ", os.getcwd())

    # Unterste Elemente der Klasse
    audioTO = AudioTransferObject("Test/Test", "meinName", "meineUUID")
    print(audioTO.path, "  ", audioTO.name, "   ", audioTO.uuid)

    # Erstellen des Interfaces und Laden der Dateien
    dl = DatalayerInterface()
    temp = dl.loadBaseAudio()


    print("\nAusgabe der einzelnen Label und Audioobjekte\n")
    # durchgehen der geladenen Dateien und Ausgabe
    for direct in temp:
        for uuid in temp[direct]:
            print("\n{0}\n{1}".format( str(temp[direct][uuid]["audio"] ) , str( temp[direct][uuid]["label"] ) ) )

    print("\nAusgabe des Kollektionsobjekts:\n")
    print(str(temp))
    print("\nAudio der erst beliebigen Datei\n{0}".format( next(iter( next(iter(   temp.items() ))[1].items() ))[1]["audio"].audio[1][:5]  )  )


    temp = dl.loadNoiseAudio()

    print("\nAusgabe der einzelnen Label und Audioobjekte für Noise\n")
    # durchgehen der geladenen Dateien und Ausgabe
    for direct in temp:
        for uuid in temp[direct]:
            print("\n{0}\n{1}".format(str(temp[direct][uuid]["audio"]), str(temp[direct][uuid]["label"])))

    print("\nAusgabe des Kollektionsobjekts:\n")
    print(str(temp))

