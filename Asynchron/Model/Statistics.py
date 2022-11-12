import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from numpy import meshgrid, linspace, max, min, array
from Model.Pipeline import PitchShiftVO
from math import ceil, floor

from itertools import product

# Base class
class StatNumberVO:

    def __init__(self, value, evaluationSpace, title, fileName, subfolder=""):
        self._value = value
        self._evaluationSpace = evaluationSpace
        self._title = title
        self._fileName = fileName
        self._subfolder = subfolder
        self._saveConfig = {"fname": "{0}\\{2}\\{1}_{0}".format(self._evaluationSpace.name, self._fileName,self._subfolder),
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
    def subfolder(self):
        return self._subfolder

    @property
    def saveConfig(self):
        return self._saveConfig # do not remove .copy(), because all instances will operate on the same array

# for depicting all confidence values in one diagram
class BaseStatVO(StatNumberVO):
    def __init__(self, value, evaluationSpace, title, fileName, subfolder=""):
        StatNumberVO.__init__(self, value=value, evaluationSpace=evaluationSpace, title=title, fileName=fileName
                              , subfolder=subfolder)

    def getFigure(self):
        # create axis data
        axis = [dimTuple for dimTuple in product(*self._evaluationSpace.dims)]
        axisNames = [name for name in self._evaluationSpace.dimNames]

        cmap = self._evaluationSpace.color
        x = [x[0] for x in axis]
        y = [y[1] for y in axis]
        z = [z[2] for z in axis]

        fig = plt.figure(figsize=(10,8))
        ax = fig.add_subplot(projection='3d')
        img = ax.scatter(x, y, z, c=self._value.ravel(), cmap=cmap)
        ax.set_title(self._title, wrap=True, fontsize=14)
        ax.set_xlabel(axisNames[0], wrap=True, fontsize=12)
        ax.set_ylabel(axisNames[1], wrap=True, fontsize=12)
        ax.set_zlabel(axisNames[2], wrap=True, fontsize=12)
        ax.w_xaxis.set_pane_color((0, 0, 0, 0.2))
        ax.w_yaxis.set_pane_color((0, 0, 0, 0.2))
        ax.w_zaxis.set_pane_color((0, 0, 0, 0.2))

        cbar = fig.colorbar(img, pad=0.09, shrink=0.5, aspect=5)
        # set ticks again so all ticks will be displayed
        cbarTicks = cbar.get_ticks()
        cbar.set_ticks(cbarTicks)

        #cbar.set_ticks(append(cbar.get_ticks(), [self._value.max()]))
        cbar.set_label("Konfidenz einer ok-Bewertung der KI", fontsize=11)
        return fig

    def saveData(self):
        # Übergebene soll eine Liste mit Einträgen sein, [x,y,z,data] + header ["x","y","z","data"]
        header = [str(dim) for dim in self._evaluationSpace.dimNames]
        header.append("data")
        data = [x + (y,) for x, y in zip(product(*self._evaluationSpace.dims),
                                         self._value.ravel())]
        self._evaluationSpace.datalayerInterface.saveCSVData(path="{0}.csv".format(self._saveConfig["fname"])
                                                             , header=header, data=data)

# for depicting mean, range and std
# depicts PitchShift values as own diagramms
class BasePitchStatVO(StatNumberVO):
    def __init__(self, value, evaluationSpace, title, fileName, subfolder=""):
        StatNumberVO.__init__(self, value=value, evaluationSpace=evaluationSpace, title=title, fileName=fileName
                              ,subfolder=subfolder)

    def getFigure(self):
        # string comparison instead of type comparison due to the fact, that import paths are messing that up
        # index of PitchShiftVO in Pipeline
        pitchIndex = next((i for i, x in enumerate(self._evaluationSpace.dimTypes) if str(x) == str(PitchShiftVO)))

        dims = array([dimTuple for dimTuple in product(*self._evaluationSpace.dims)])
        data = self._value.ravel()
        figs = []
        for x in self.evaluationSpace.dims[pitchIndex]:
            cond = [True if dimTuple[pitchIndex]==x else False for dimTuple in dims]
            axis = dims[cond]
            cData = data[cond]

            axisNames = [name for name in self._evaluationSpace.dimNames]

            cmap = self._evaluationSpace.color
            x = [x[0] for x in axis]
            y = [y[1] for y in axis]
            z = [z[2] for z in axis]

            fig = plt.figure(figsize=(10,8))
            ax = fig.add_subplot(projection='3d')
            img = ax.scatter(x, y, z, c=cData, cmap=cmap)
            ax.set_title(self._title, fontsize=14)
            ax.set_xlabel(axisNames[0], wrap=True, fontsize=12)
            ax.set_ylabel(axisNames[1], wrap=True, fontsize=12)
            ax.set_zlabel(axisNames[2], wrap=True, fontsize=12)
            ax.w_xaxis.set_pane_color((0, 0, 0, 0.2))
            ax.w_yaxis.set_pane_color((0, 0, 0, 0.2))
            ax.w_zaxis.set_pane_color((0, 0, 0, 0.2))

            cbar = fig.colorbar(img, pad=0.09, shrink=0.5, aspect=5)
            # set ticks again so all ticks will be displayed
            cbarTicks = cbar.get_ticks()
            cbar.set_ticks(cbarTicks)

            #cbar.set_ticks(append(cbar.get_ticks(), [self._value.max()]))
            cbar.set_label("Konfidenz einer ok-Bewertung der KI", fontsize=11)
            figs.append(fig)
        return figs

    def saveFig(self):
        # with Path can directories be created
        configCopy = self._saveConfig.copy()
        copy = configCopy["fname"]
        for i,fig in enumerate(self.getFigure()):
            configCopy["fname"] = f"{copy}_{i}.png"
            self._evaluationSpace.datalayerInterface.saveFigure(figure=fig, config=configCopy)

    def saveData(self):
        # Übergebene soll eine Liste mit Einträgen sein, [x,y,z,data] + header ["x","y","z","data"]
        header = [str(dim) for dim in self._evaluationSpace.dimNames]
        header.append("data")
        data = [x + (y,) for x, y in zip(product(*self._evaluationSpace.dims),
                                         self._value.ravel())]
        self._evaluationSpace.datalayerInterface.saveCSVData(path="{0}.csv".format(self._saveConfig["fname"])
                                                             , header=header, data=data)

    # specifically for depicting pitch shift as separate diagrams
class ContourPitchStatVO(StatNumberVO):
    def __init__(self, value, evaluationSpace, title, fileName, subfolder=""):
        StatNumberVO.__init__(self, value=value, evaluationSpace=evaluationSpace, title=title, fileName=fileName
                              ,subfolder=subfolder)

    def getFigure(self):
        # string comparison instead of type comparison due to the fact, that import paths are messing that up
        # index of PitchShiftVO in Pipeline
        pitchIndex = next((i for i, x in enumerate(self._evaluationSpace.dimTypes) if str(x) == str(PitchShiftVO)))
        axisValues = self._evaluationSpace.dims[:pitchIndex] + self._evaluationSpace.dims[pitchIndex + 1:]
        dimNames = self._evaluationSpace.dimNames[:pitchIndex] + self._evaluationSpace.dimNames[pitchIndex + 1:]

        dims = array([dimTuple for dimTuple in product(*self._evaluationSpace.dims)])
        data = self._value.ravel()
        figs = []
        for x in self._evaluationSpace.dims[pitchIndex]:
            cond = [True if dimTuple[pitchIndex] == x else False for dimTuple in dims]
            cData = data[cond]


            x = axisValues[0] # FrequencyAugmentation
            y = axisValues[1] # NoiseInjection
            x, y = meshgrid(y, x)
            z = cData
            z = z.reshape(x.shape)

            levels = 8
            #vmin = round(min(z), 1)
            #vmax = round(max(z), 1)
            vmin = floor(min(z) * 10) / 10
            vmax = ceil(max(z) * 10) / 10
            level_boundaries = linspace(vmin, vmax, levels + 1)

            # Credit for code to :
            # https://matplotlib.org/stable/gallery/mplot3d/surface3d.html
            #create figure
            fig, ax = plt.subplots(figsize=(10, 8))
            # create colormap
            colors = ["black", "red", "yellow", "white"]
            cmap = self._evaluationSpace.color
            # Plot the surface.
            quadcontourset = ax.contourf(y, x, z, level_boundaries, vmin=vmin, vmax=vmax, cmap=cmap,antialiased=False)

            # Add a color bar which maps values to colors.
            cbar = fig.colorbar(quadcontourset, pad=0.09, shrink=0.5, aspect=5)
            cbar.set_label("Konfidenz einer ok-Bewertung der KI", rotation=270, labelpad=10.0, fontsize=11)

            fig.suptitle(self._title, fontsize=14)
            ax.set_xlabel(dimNames[0], wrap=True, fontsize=12) # due to gridmesh (x,y) being inverted 0 and 1 need to be swapped
            ax.set_ylabel(dimNames[1], wrap=True, fontsize=12)
            figs.append(fig)
        return figs

    def saveFig(self):
        # with Path can directories be created
        configCopy = self._saveConfig.copy()
        copy = configCopy["fname"]
        for i,fig in enumerate(self.getFigure()):
            configCopy["fname"] = f"{copy}_{i}.png"
            self._evaluationSpace.datalayerInterface.saveFigure(figure=fig, config=configCopy)

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


# for comparing different error classes as histogramm
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

        plt.title("Werteverteilung " + axisName, wrap=True, fontsize=12)
        plt.ylabel("Häufigkeit der Fehler #")
        plt.xlabel("berechneter " + axisName)
        return fig

    def saveData(self):
        data = [(x,) for i, x in enumerate(self._value)]
        self._evaluationSpace.datalayerInterface.saveCSVData(path="{0}.csv".format(self._saveConfig["fname"])
                                                             , header=["error"], data=data)

# For removing the pitchshift dimension by calculating the mean over it
class SurfaceStatVO(StatNumberVO):
    def __init__(self, value, evaluationSpace, title, fileName):
        StatNumberVO.__init__(self, value=value, evaluationSpace=evaluationSpace, title=title, fileName=fileName)

    def getFigure(self):
        # string comparison instead of type comparison due to the fact, that import paths are messing that up
        # index of PitchShiftVO in Pipeline
        pitchIndex = next((i for i, x in enumerate(self._evaluationSpace.dimTypes) if str(x) == str(PitchShiftVO)))
        dims = self._evaluationSpace.dims[:pitchIndex] + self._evaluationSpace.dims[pitchIndex+1:]
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
        cmap = self._evaluationSpace.color
        # Plot the surface.
        surf = ax.plot_surface(x, y, z, cmap=cmap,linewidth=0, antialiased=False)

        # Customize the z axis.
        ax.set_zlim(0, 1.1)

        # Add a color bar which maps values to colors.
        cbar = fig.colorbar(surf, pad=0.09, shrink=0.5, aspect=5)
        # set ticks again so that all values will be displayed
        cbarTicks = cbar.get_ticks()
        cbar.set_ticks(cbarTicks)



        fig.suptitle(self._title, fontsize=14)
        ax.set_xlabel(dimNames[1], wrap=True, fontsize=12) # due to gridmesh (x,y) being inverted 0 and 1 need to be swapped
        ax.set_ylabel(dimNames[0], wrap=True, fontsize=12)
        ax.set_zlabel("Konfidenz einer ok-Bewertung der KI", wrap=True, fontsize=12)

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
        dimNames = self._evaluationSpace.dimNames[:pitchIndex] + self._evaluationSpace.dimNames[pitchIndex + 1:]

        x = dims[0] # FrequencyAugmentation
        y = dims[1] # NoiseInjection
        x, y = meshgrid(y, x)
        z = self._value.ravel()
        z = z.reshape(x.shape)

        levels = 8
        #vmin = round(min(z), 1)
        #vmax = round(max(z), 1)
        vmin = floor(min(z)*10)/10
        vmax = ceil(max(z)*10)/10
        level_boundaries = linspace(vmin, vmax, levels + 1)

        # Credit for code to :
        # https://matplotlib.org/stable/gallery/mplot3d/surface3d.html
        #create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        # facecolor of background so contrast is higher
        ax.set_facecolor("grey")
        # create colormap
        colors = ["black", "red", "yellow", "white"]
        cmap = self._evaluationSpace.color
        # Plot the surface.
        quadcontourset = ax.contourf(y, x, z, level_boundaries, vmin=vmin, vmax=vmax, cmap=cmap,antialiased=False)

        # Add a color bar which maps values to colors.
        cbar = fig.colorbar(quadcontourset, pad=0.09, shrink=0.5, aspect=5)
        cbar.set_label("Konfidenz einer ok-Bewertung der KI", rotation=270, labelpad=10.0, fontsize=11)

        fig.suptitle(self._title, fontsize=14)
        ax.set_xlabel(dimNames[0], wrap=True, fontsize=12) # due to gridmesh (x,y) being inverted 0 and 1 need to be swapped
        ax.set_ylabel(dimNames[1], wrap=True, fontsize=12)

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



