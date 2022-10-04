"""
Dies ist ein manueller Test. Es werden manuell Eingaben in die conf-Datei eingegeben und getestet wie das Programm
reagiert.
Es gibt insgesamt vier Variablen, die getestet werden sollen.
- pitchshiftPercents : "[0]"
- freqSteps : 8
- noiseSteps : 8
- noiseAmplitude : 0.5
Diese sind als "[Name der Variable] : [Wert]" zu interpretieren.

Folgendes Verhalten ist zu erwarten:
- pitchshiftPercents : soll ein Array wie in Python syntax sein, ansonsten Abbruch
- freqSteps : soll eine Zahl in Reichweite [0,inf) sein, ansonsten Abbruch
- noiseSteps : soll eine Zahl in Reichweite [0,inf) sein, ansonsten Abbruch
- noiseAmplitude : soll eine Zahl in Reichweite [0,inf) sein, ansonsten Abbruch
Für alle Variablen führt eine 0 dazu, dass dieser Dimension nicht bearbeitet wird. Hierbei sind diese
wie folgt gruppiert:
- pitchshiftPercents : PitchShift-Dimension
- freqSteps : FrequenzAugmentation-Dimension
- noiseSteps : NoiseInjection-Dimension
- noiseAmplitude : NoiseInjection-Dimension
Folgende Daten wurden getestet:
- pitchshiftPercents : Y=app started, X=app aborted, (Y/X) = erwartetes Ergebnis
keine Eingabe X (X)
[]          X (X)
[0,]        X (X)
[,0]        X (X)
0           X (X)
[0]         Y (Y)
[0,0]       Y (Y)
[0          X (X)
0]          X (X)
[-1,0,1]    Y (Y)
[0,-1,1]    Y (Y)
[a,0]       X (X)
[0,b]       X (X)
[0,1.1]     X (X)
[0.,1]      X (X)
- freqSteps : FrequenzAugmentation-Dimension
keine Eingabe X (X)
-1          X (X)
0           Y (Y)
1           Y (Y)
a           X (X
01          Y (Y)
-01         X (X)
- noiseSteps : NoiseInjection-Dimension
keine Eingabe X (X)
-1          X (X)
0           Y (Y)
1           Y (Y)
a           X (X
01          Y (Y)
-01         X (X)
- noiseAmplitude : NoiseInjection-Dimension
keine Eingabe X (X)
-1          X (X)
0           Y (Y)
1.1           Y (Y)
a           X (X
01.1          Y (Y)
-01.1         X (X)
"""

