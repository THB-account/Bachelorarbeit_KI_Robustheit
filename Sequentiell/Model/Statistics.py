import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from numpy import meshgrid, append

from itertools import product


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
        return self._saveConfig # do not remove .copy(), because all instances will operate on the same array


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
            colors = ["black", "red", "yellow"]
            cmap = LinearSegmentedColormap.from_list('test', colors, N=256)
            x = [x[0] for x in axis]
            y = [y[1] for y in axis]
            z = [z[2] for z in axis]

            fig = plt.figure(**pltConfig)
            ax = fig.add_subplot(projection='3d')
            img = ax.scatter(x, y, z, c=self._value.ravel(), cmap=cmap)
            ax.set_title(self._title)
            ax.set_xlabel(axisNames[0] + "[{0}-{1}]".format(min(self._evaluationSpace.dims[0])
                                                       , max(self._evaluationSpace.dims[0])))
            ax.set_ylabel(axisNames[1] + "[{0}-{1}]".format(min(self._evaluationSpace.dims[1])
                                                       , max(self._evaluationSpace.dims[1])))
            ax.set_zlabel(axisNames[2] + "[{0}-{1}]".format(min(self._evaluationSpace.dims[2])
                                                       , max(self._evaluationSpace.dims[2])))
            cbar = fig.colorbar(img, pad=0.09, extend='max', shrink=0.5, aspect=5)
            cbar.set_ticks(append(cbar.get_ticks(), [self._value.max()]))
            cbar.set_label("Konfidenz")
        return fig

    def saveData(self):
        # Übergebene soll eine Liste mit Einträgen sein, [x,y,z,data] + header ["x","y","z","data"]
        header = [str(dim) for dim in self._evaluationSpace.dimNames]
        header.append("data")
        data = [x + (y,) for x, y in zip(product(*self._evaluationSpace.dims),
                                         self._value.ravel())]
        self._evaluationSpace.datalayerInterface.saveCSVData(path="{0}.csv".format(self._saveConfig["fname"])
                                                             , header=header, data=data)


class ErrorStatVO(StatNumberVO):
    def __init__(self, value, evaluationSpace, title):
        StatNumberVO.__init__(self, value=value, evaluationSpace=evaluationSpace, title=title)

    def getFigure(self):
        axisName = self._title

        # https://stats.stackexchange.com/questions/798/calculating-optimal-number-of-bins-in-a-histogram
        # q75, q25 = np.percentile(x, [75 ,25])
        # iqr = q75 - q25
        # bin setting fd
        fig = plt.figure(figsize=(10, 8))
        plt.hist(self._value, bins='fd', density=True, facecolor='g', alpha=0.75)
        plt.grid(True)

        plt.title(axisName)
        plt.ylabel("Wahrscheinlichkeitsdichte")
        plt.xlabel("berechneter " + axisName)
        return fig

    def saveData(self):
        data = [(i,x) for i, x in enumerate(self._value)]
        self._evaluationSpace.datalayerInterface.saveCSVData(path="{0}.csv".format(self._saveConfig["fname"])
                                                             , header=["error"], data=data)


class SurfaceStatVO(StatNumberVO):
    def __init__(self, value, evaluationSpace, title):
        StatNumberVO.__init__(self, value=value, evaluationSpace=evaluationSpace, title=title)

    def getFigure(self):
        axis = [dimTuple for dimTuple in product(*self._evaluationSpace.dims)]
        dimNames = [self._evaluationSpace.dimNames[i] for i,dim in enumerate(self._evaluationSpace.dimTypes)
                    if i!=1]

        x = self._evaluationSpace.dims[0] # FrequencyAugmentation
        y = self._evaluationSpace.dims[2] # NoiseInjection
        x, y = meshgrid(y, x)
        z = self._value.ravel()
        z = z.reshape(x.shape)

        # Credit for code to :
        # https://matplotlib.org/stable/gallery/mplot3d/surface3d.html
        #create figure
        fig, ax = plt.subplots(subplot_kw={"projection": "3d"}, figsize=(10, 8))
        # create colormap
        colors = ["black", "red", "yellow", "white"]
        cmap = LinearSegmentedColormap.from_list('test', colors, N=256)
        # Plot the surface.
        surf = ax.plot_surface(x, y, z, cmap=cmap,linewidth=0, antialiased=False)

        # Customize the z axis.
        ax.set_zlim(0, 1.1)

        # Add a color bar which maps values to colors.
        cbar = fig.colorbar(surf, pad=0.09, extend='max', shrink=0.5, aspect=5)
        cbar.set_ticks(append(cbar.get_ticks(), [z.max()]))

        fig.suptitle(self._title)
        ax.set_xlabel(dimNames[1] + "[{0}-{1}]".format(min(self._evaluationSpace.dims[2])
                                                       , max(self._evaluationSpace.dims[2]))) # due to gridmesh (x,y) being inverted 0 and 1 need to be swapped
        ax.set_ylabel(dimNames[0] + "[{0}-{1}]".format(min(self._evaluationSpace.dims[0])
                                                       , max(self._evaluationSpace.dims[0])))
        ax.set_zlabel("Konfidenz")
        return fig

    def saveData(self):
        # Übergebene soll eine Liste mit Einträgen sein, [x,y,z,data] + header ["x","y","z","data"]
        # TODO durch Typüberprüfung ersetzen
        header = [self.evaluationSpace.dimNames[i] for i,dim in enumerate(self._evaluationSpace.dimTypes) if i!=1]
        header.append("data")
        data = [x + (y,) for x, y in zip(product(self._evaluationSpace.dims[0], self._evaluationSpace.dims[2]),
                                         self._value.ravel())]
        self._evaluationSpace.datalayerInterface.saveCSVData(path="{0}.csv".format(self._saveConfig["fname"])
                                                             , header=header, data=data)



