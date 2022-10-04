import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from numpy import meshgrid, append, linspace, max, min
from Model.Pipeline import FrequencyAugmentationVO, PitchShiftVO

from itertools import product


class StatNumberVO:

    def __init__(self, value, evaluationSpace, title, fileName):
        self._value = value
        self._evaluationSpace = evaluationSpace
        self._title = title
        self._fileName = fileName
        self._saveConfig = {"fname": "{0}\\{1}_{0}".format(self._evaluationSpace.name, self._fileName),
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
    def fileName(self):
        return self._fileName

    @property
    def saveConfig(self):
        return self._saveConfig # do not remove .copy(), because all instances will operate on the same array


class BaseStatVO(StatNumberVO):
    def __init__(self, value, evaluationSpace, title, fileName):
        StatNumberVO.__init__(self, value=value, evaluationSpace=evaluationSpace, title=title, fileName=fileName)

    def getFigure(self):
        # string comparison instead of type comparison due to the fact, that import paths are messing that up
        # index of noiseinjection in Pipeline
        i = next((i for i, x in enumerate(self._evaluationSpace.dimTypes) if str(x) == str(FrequencyAugmentationVO)))
        # create axis data
        axis = [dimTuple[:i] + (int(dimTuple[i]*self._evaluationSpace.samplingRate/2),)
                + dimTuple[i+1:] for dimTuple in product(*self._evaluationSpace.dims)]
        axisNames = [name for name in self._evaluationSpace.dimNames]



        colors = ["black", "red", "yellow"]
        cmap = LinearSegmentedColormap.from_list('test', colors, N=256)
        x = [x[0] for x in axis]
        y = [y[1] for y in axis]
        z = [z[2] for z in axis]

        fig = plt.figure(figsize=(10,8))
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
        # set ticks again so all ticks will be displayed
        cbarTicks = cbar.get_ticks()
        cbar.set_ticks(cbarTicks)

        #cbar.set_ticks(append(cbar.get_ticks(), [self._value.max()]))
        cbar.set_label("Konfidenz einer ok-Bewertung der KI")
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
    def __init__(self, value, evaluationSpace, title, fileName):
        StatNumberVO.__init__(self, value=value, evaluationSpace=evaluationSpace, title=title, fileName=fileName)

    def getFigure(self):
        axisName = self._title

        # https://stats.stackexchange.com/questions/798/calculating-optimal-number-of-bins-in-a-histogram
        # q75, q25 = np.percentile(x, [75 ,25])
        # iqr = q75 - q25
        # bin setting fd
        fig = plt.figure(figsize=(10, 8))
        plt.hist(self._value, bins='fd', facecolor='g', alpha=0.75)
        plt.grid(True)

        plt.title(axisName)
        plt.ylabel("Häufigkeit #")
        plt.xlabel("berechneter " + axisName)
        return fig

    def saveData(self):
        data = [(x,) for i, x in enumerate(self._value)]
        self._evaluationSpace.datalayerInterface.saveCSVData(path="{0}.csv".format(self._saveConfig["fname"])
                                                             , header=["error"], data=data)


class SurfaceStatVO(StatNumberVO):
    def __init__(self, value, evaluationSpace, title, fileName):
        StatNumberVO.__init__(self, value=value, evaluationSpace=evaluationSpace, title=title, fileName=fileName)

    def getFigure(self):
        # string comparison instead of type comparison due to the fact, that import paths are messing that up
        # index of PitchShiftVO in Pipeline
        pitchIndex = next((i for i, x in enumerate(self._evaluationSpace.dimTypes) if str(x) == str(PitchShiftVO)))
        dims = self._evaluationSpace.dims[:pitchIndex] + self._evaluationSpace.dims[pitchIndex+1:]
        # get index of FrequencyAugmentationVO so that its values can be multiplied by SamplingRate/2
        freqIndex = next((i for i, x in enumerate(self._evaluationSpace.dimTypes[:pitchIndex]+
                                                  self._evaluationSpace.dimTypes[pitchIndex+1:]) if str(x) == str(FrequencyAugmentationVO)))
        dims[freqIndex] = [int(x*self._evaluationSpace.samplingRate/2) for x in dims[freqIndex]]

        dimNames = self._evaluationSpace.dimNames[:pitchIndex] + self._evaluationSpace.dimNames[pitchIndex+1:]

        x = dims[0] # FrequencyAugmentation
        y = dims[1] # NoiseInjection
        x, y = meshgrid(y, x)
        z = self._value.ravel()
        z = z.reshape(x.shape)

        # Credit for code to :
        # https://matplotlib.org/stable/gallery/mplot3d/surface3d.html
        #create figure
        fig, ax = plt.subplots(subplot_kw={"projection": "3d"}, figsize=(10, 8))
        # create colormap
        colors = ["black", "red", "yellow", "white"]
        cmap = LinearSegmentedColormap.from_list('Hot', colors, N=256)
        # Plot the surface.
        surf = ax.plot_surface(x, y, z, cmap=cmap,linewidth=0, antialiased=False)

        # Customize the z axis.
        ax.set_zlim(0, 1.1)

        # Add a color bar which maps values to colors.
        cbar = fig.colorbar(surf, pad=0.09, extend='max', shrink=0.5, aspect=5)
        # set ticks again so that all values will be displayed
        cbarTicks = cbar.get_ticks()
        cbar.set_ticks(cbarTicks)



        fig.suptitle(self._title)
        ax.set_xlabel(dimNames[1] + "[{0}-{1}]".format(min(self._evaluationSpace.dims[2])
                                                       , max(self._evaluationSpace.dims[2]))) # due to gridmesh (x,y) being inverted 0 and 1 need to be swapped
        ax.set_ylabel(dimNames[0] + "[{0}-{1}]".format(min(self._evaluationSpace.dims[0])
                                                       , max(self._evaluationSpace.dims[0])))
        ax.set_zlabel("Konfidenz einer ok-Bewertung der KI")

        return fig

    def saveData(self):
        # using string instead of type due to import path messing type check up somewhere
        pitchIndex = next((i for i, x in enumerate(self._evaluationSpace.dimTypes) if str(x) == str(PitchShiftVO)))
        # Übergebene soll eine Liste mit Einträgen sein, [x,y,z,data] + header ["x","y","z","data"]
        header = [self.evaluationSpace.dimNames[i] for i, dim in enumerate(self._evaluationSpace.dimTypes) if
                  i != pitchIndex]
        header.append("data")
        data = [x + (y,) for x, y in zip(product(*(self._evaluationSpace.dims[:pitchIndex] +
                                                   self._evaluationSpace.dims[pitchIndex + 1:])),
                                         self._value.ravel())]
        self._evaluationSpace.datalayerInterface.saveCSVData(path="{0}.csv".format(self._saveConfig["fname"])
                                                             , header=header, data=data)


class ContourStatVO(StatNumberVO):
    def __init__(self, value, evaluationSpace, title, fileName):
        StatNumberVO.__init__(self, value=value, evaluationSpace=evaluationSpace, title=title, fileName=fileName)

    def getFigure(self):
        # string comparison instead of type comparison due to the fact, that import paths are messing that up
        # index of PitchShiftVO in Pipeline
        pitchIndex = next((i for i, x in enumerate(self._evaluationSpace.dimTypes) if str(x) == str(PitchShiftVO)))
        dims = self._evaluationSpace.dims[:pitchIndex] + self._evaluationSpace.dims[pitchIndex + 1:]
        # get index of FrequencyAugmentationVO so that its values can be multiplied by SamplingRate/2
        freqIndex = next((i for i, x in enumerate(self._evaluationSpace.dimTypes[:pitchIndex] +
                                                  self._evaluationSpace.dimTypes[pitchIndex + 1:]) if
                          str(x) == str(FrequencyAugmentationVO)))
        dims[freqIndex] = [int(x * self._evaluationSpace.samplingRate / 2) for x in dims[freqIndex]]

        dimNames = self._evaluationSpace.dimNames[:pitchIndex] + self._evaluationSpace.dimNames[pitchIndex + 1:]

        x = dims[0] # FrequencyAugmentation
        y = dims[1] # NoiseInjection
        x, y = meshgrid(y, x)
        z = self._value.ravel()
        z = z.reshape(x.shape)

        levels = 8
        vmin = round(min(z), 1)
        vmax = round(max(z), 1)
        level_boundaries = linspace(vmin, vmax, levels + 1)

        # Credit for code to :
        # https://matplotlib.org/stable/gallery/mplot3d/surface3d.html
        #create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        # create colormap
        colors = ["black", "red", "yellow", "white"]
        cmap = LinearSegmentedColormap.from_list('Hot', colors, N=256)
        # Plot the surface.
        quadcontourset = ax.contourf(x, y, z, level_boundaries, vmin=vmin, vmax=vmax, cmap=cmap,antialiased=False)

        # Add a color bar which maps values to colors.
        cbar = fig.colorbar(quadcontourset, pad=0.09, extend='max', shrink=0.5, aspect=5)
        cbar.set_label("Konfidenz einer ok-Bewertung der KI", rotation=270, labelpad=10.0)

        fig.suptitle(self._title)
        ax.set_xlabel(dimNames[1] + "[{0}-{1}]".format(min(self._evaluationSpace.dims[2])
                                                       , max(self._evaluationSpace.dims[2]))) # due to gridmesh (x,y) being inverted 0 and 1 need to be swapped
        ax.set_ylabel(dimNames[0] + "[{0}-{1}]".format(min(self._evaluationSpace.dims[0])
                                                       , max(self._evaluationSpace.dims[0])))

        return fig

    def saveData(self):
        # using string instead of type due to import path messing type check up somewhere
        pitchIndex = next((i for i, x in enumerate(self._evaluationSpace.dimTypes) if str(x) == str(PitchShiftVO)))
        # Übergebene soll eine Liste mit Einträgen sein, [x,y,z,data] + header ["x","y","z","data"]
        header = [self.evaluationSpace.dimNames[i] for i,dim in enumerate(self._evaluationSpace.dimTypes) if i!=pitchIndex]
        header.append("data")
        data = [x + (y,) for x, y in zip(product(*(self._evaluationSpace.dims[:pitchIndex] +
                                                  self._evaluationSpace.dims[pitchIndex + 1:])),
                                         self._value.ravel())]
        self._evaluationSpace.datalayerInterface.saveCSVData(path="{0}.csv".format(self._saveConfig["fname"])
                                                             , header=header, data=data)



