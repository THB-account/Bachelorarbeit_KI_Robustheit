import matplotlib.pyplot as plt
from itertools import product

# TODO folgende statistische Maße implementieren
"""
- absoluter Fehler
- mean suqared Error
- sum squared error
- Wendepunkte
- Durchschnitt aus der pitch-Dimension, so dass ein Mesh dargestellt werden kann
- pitch-Dimensionen als Mesh

"""


class StatNumberVO:

    def __init__(self, value, evaluationSpace, title):
        self._value = value
        self._evaluationSpace = evaluationSpace
        self._title = title
        self._saveConfig = {"fname": "{0}\\{1}_{0}".format(self._evaluationSpace.name, self._title),
                            "dpi": "figure",
                            "bbox_inches": None,
                            "pad_inches": 0.1}

    # abstract
    def getFigure(self):
        pass

    def saveFig(self):
        # with Path can directories be created
        configCopy = self._saveConfig.copy()
        configCopy["fname"] += ".png"
        self._evaluationSpace.datalayerInterface.saveFigure(figure=self.getFigure(), config=configCopy)

    # abstract
    def saveData(self):
        pass

    # setter and getter
    @property
    def value(self):
        return self._value

    @property
    def evaluationSpace(self):
        return self._evaluationSpace

    @property
    def title(self):
        return self._title

    @property
    def saveConfig(self):
        return self._saveConfig


class BaseStatVO(StatNumberVO):
    def __init__(self, value, evaluationSpace, title):
        StatNumberVO.__init__(self, value=value, evaluationSpace=evaluationSpace, title=title)

    def getFigure(self):
        axis = [dimTuple for dimTuple in product(*self._evaluationSpace.dims)]
        axisNames = [name for name in self._evaluationSpace.dimNames]
        pltConfig = {"figsize":(10,8)}

        if len(axis[0]) == 1: # arbitrary element for check
            x = [x[0] for x in axis]

            fig = plt.figure(**pltConfig)
            plt.plot(x, self._value.ravel())
            plt.title(self._title)
            plt.xlabel(axisNames[0])
            plt.ylabel("Konfidenz")
        elif len(axis[0]) == 2:
            x = [x[0] for x in axis]
            y = [y[1] for y in axis]

            fig = plt.figure(**pltConfig)
            ax = fig.add_subplot(projection='3d')
            ax.scatter(x, y, self._value.ravel())
            ax.set_title(self._title)
            ax.set_xlabel(axisNames[0])
            ax.set_ylabel(axisNames[1])
            ax.set_zlabel("Konfidenz")
        else: # if len == 3
            x = [x[0] for x in axis]
            y = [y[1] for y in axis]
            z = [z[2] for z in axis]

            fig = plt.figure(**pltConfig)
            ax = fig.add_subplot(projection='3d')
            img = ax.scatter(x, y, z, c=self._value.ravel(), cmap=plt.hot())
            ax.set_title(self._title)
            ax.set_xlabel(axisNames[0])
            ax.set_ylabel(axisNames[1])
            ax.set_zlabel(axisNames[2])
            cbar = fig.colorbar(img)
            cbar.set_label("Konfidenz")
        return fig

    def saveData(self):
        # Übergebene soll eine Liste mit Einträgen sein, [x,y,z,data] + header ["x","y","z","data"]
        header = ["xyzabcdefgh"[i] for i in range(len(self._evaluationSpace.dims))]
        header.append("data")
        data = [x + (y,) for x, y in zip(product(*self._evaluationSpace.dims),
                                         self._value.ravel())]
        self._evaluationSpace.datalayerInterface.saveCSVData(path="{0}.csv".format(self._saveConfig["fname"])
                                                             , header=header, data=data)
