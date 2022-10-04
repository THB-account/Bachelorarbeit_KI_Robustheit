from Model.Statistics import BaseStatVO, ErrorStatVO, SurfaceStatVO
import numpy as np
import matplotlib.pyplot as plt


class EvaluationCollection:
    def __init__(self):
        self.__container = []
        self.__counter = 0

    # own methods
    # should consist of Methods to calculate values and manage self.__container
    def add(self, element):
        if (self.__container is not None):
            self.__container.append(element)
        else:
            raise ValueError("Im Objekt {0} wurde versucht ein Element zu einem Nonetype hinzuzufügen",
                             hex(id(self)))

    def save(self):
        for space in self.__container:
            space.save()
        # TODO Vergleich verschiedener Spaces implementieren
        """
        1. Hole DatalayerInterface von der ersten Klasse
        2. Hole Daten von den drei Klassen
        3. Erstelle mit diesen das Vergleichsdiagramm
        """
        datalayerInterface = self.__container[0].datalayerInterface # for later stirage
        saveConfig = self.__container[0].stats["MSE"].saveConfig.copy() # basic saveconfig for surface diagram
        tempContainer = [[],[],[]]
        titles=[
            self.__container[0].stats["MSE"].title, # just so that the title fits into the general name scheme
            self.__container[0].stats["SSE"].title,
            self.__container[0].stats["AE"].title
        ]


        names = [] # Names of noise class
        for i,evaluationSpace in enumerate(self.__container): # extract values from classes
            names.append(evaluationSpace.name)
            tempContainer[0].append( evaluationSpace.stats["MSE"].value)
            tempContainer[1].append(evaluationSpace.stats["SSE"].value)
            tempContainer[2].append(evaluationSpace.stats["AE"].value)

        # MSE
        for i in range(len(titles)):
            saveConfig["fname"] = ''.join([titles[i],".png"])
            fig = plt.figure(figsize=(10, 8))
            for i,noiseClass in enumerate(tempContainer[0]):
                plt.hist(noiseClass, bins='fd', density=True, alpha=0.75, label=names[i])

            plt.grid(True)
            plt.title(titles[0])
            plt.ylabel("Wahrscheinlichkeitsdichte")
            plt.xlabel("berechneter " + titles[0])
            plt.legend()
            # save to file and close figure
            datalayerInterface.saveFigure(fig, config=saveConfig)

    # getter and setter
    def getElement(self, index):
        if index < 0 and index < len(self.__container):
            return self.__container[index]
        else:
            raise IndexError("Trying to access out of bounds")

    @property
    def container(self):
        return self.__container.copy()

    @container.setter
    def container(self, container):
        self.__container = container


class PredictionSpaceContainerVO:
    def __init__(self, n,shape, dtype=np.dtype(np.single), dims=None, dimNames=None, dimTypes=None, name=""):
        self.__container = np.ndarray(shape=(n,) + shape, dtype=dtype)
        self.__counter = 0
        self.__dims = dims
        self.__dimNames = dimNames
        self.__dimTypes = dimTypes
        self.__name = name


    # own methods
    # should consist of Methods to calculate values and manage self.__container
    def add(self, arr):
        if (self.__counter < self.__container.shape[0]):
            self.__container[self.__counter] = arr
            self.__counter += 1
        else:
            raise IndexError("Es wurde versucht das Objekt {0} in den vollen PredictionContrainer {1} einzugüfen",
                             hex(id(arr)), hex(id(self)))

    def createAnalysis(self, datalayerInterface):
        initValues = {
            "datalayerInterface" : datalayerInterface,
            "name" : self.__name,
            "dims" : self.__dims,
            "dimNames" : self.__dimNames,
            "dimTypes" : self.__dimTypes
        }
        initValues["mean"] = self.mean()
        initValues["std"] = self.std()
        initValues["statRange"] = self.range()
        initValues.update(self.error())
        initValues.update(self.surface(initValues["mean"],initValues["std"],initValues["statRange"]))

        evaluation = EvaluationSpaceVO(**initValues)
        return evaluation

        # analysis functions
    def mean(self):
        # if container has form            (65,4,3,2) # 65 three dimensional objects
        # the order of dimensions would be (0 ,1,2,3) and nth dimension would be cut
        # in case of
        return np.mean(self.__container, axis=0)

    def std(self):
        return np.std(self.__container, axis=0)

    def max(self):
        return self.__container.max(axis=0)

    def min(self):
        return self.__container.min(axis=0)

    def range(self):
        return self.__container.max(axis=0) - self.__container.min(axis=0)

    def error(self):
        result = {"SSE" : np.ndarray(len(self.__container), dtype=np.int32),
                  "MSE" : np.ndarray(len(self.__container), dtype=np.int32),
                  "AE"  : np.ndarray(len(self.__container), dtype=np.int32)}
        size = self.__container[0].size
        ogCoord = tuple()
        for dim in self.__dims:
            for x in dim:
                if x==0:
                    ogCoord+= (int(x),)
                    break

        for i in range(len(self.__container)):
            original = self.__container[(i,)+ogCoord]
            # for entry in container add together
            errors = [0, 0, 0]  # absolute, sum square, mean square
            for x in np.nditer(self.__container[i]):
                errors[0]+=abs(x - original)*100 # absolute error
                errors[1]+= ((x-original)*(x-original))*100 # sum squared error

            # calculate mean
            errors[2] = errors[1]/size # mean square error
            result["AE"][i] = int(errors[0])
            result["SSE"][i] = int(errors[1])
            result["MSE"][i] = int(errors[2])
            errors[0] = errors[1] = errors[2] = 0 # reset values

        return result

    def surface(self, mean, std, statRange):
        result = { "mean_surf" : mean,
                   "std_surf"  : std,
                   "statRange_surf": range,
        }
        if len(self.__dims) == 2:
            pass
        elif len(self.__dims) == 3:
            temp = -1
            # check whether object is instance of pitch shift or if that is false if there are less than 3 dimensions
            # TODO Figure out Error, why isinstance not working and replace hard coding
            # Following doesnt work, most likely due to import paths
            """
            for i in range(3):
                if isinstance(self.__dimTypes[i], PitchShiftVO):
                    temp = i
                    break    
            if i < 0: # if no pitch shift and more than 2 dimensions cant create a surface
                raise ValueError("In der Surfaceberechnung im PredictionContainer wurde keine PitchShift-Dimension mitgegeben.")
            """
            # find dimension which is pitch_shift
            result["mean_surf"] =  np.mean(mean, axis=1)
            result["std_surf"] =   np.mean(std, axis=1)
            result["statRange_surf"] = np.mean(statRange, axis=1)
        else:
            raise ValueError("In der Surfaceberechnung im wurden nicht genug Dimensionen mitgegeben.")
        return result


    # getter and setter
    @property
    def container(self):
        return self.__container

    @property
    def counter(self):
        return self.__counter

    @property
    def dims(self):
        return self.__dims

    @property
    def name(self):
        return self.__name

    @property
    def dimNames(self):
        return self.__dimNames

    @property
    def dimTypes(self):
        return self.__dimTypes

    @container.setter
    def container(self, container):
        self.__container = container

    @name.setter
    def name(self, name):
        self.__name = name


class EvaluationSpaceVO:

    def __init__(self, datalayerInterface, name, dims, dimNames, dimTypes, mean, std, statRange, SSE, MSE, AE,
                 mean_surf, std_surf, statRange_surf):
        self.__datalayerInterface = datalayerInterface
        self.__name = name
        self.__dims = dims
        self.__dimNames = dimNames
        self.__dimTypes = dimTypes
        # statistics
        self.__stats = {}
        self.__stats["mean"] =  BaseStatVO(value=mean, evaluationSpace=self, title="mean")
        self.__stats["std"] =   BaseStatVO(value=std, evaluationSpace=self, title="std")
        self.__stats["range"] = BaseStatVO(value=statRange, evaluationSpace=self, title="range")
        self.__stats["SSE"] =   ErrorStatVO(value=SSE, evaluationSpace=self, title="Sum Squared Error")
        self.__stats["MSE"] =   ErrorStatVO(value=MSE, evaluationSpace=self, title="Mean Squared Error")
        self.__stats["AE"] =    ErrorStatVO(value=AE, evaluationSpace=self, title="Absolute Error")
        self.__stats["mean_surf"]=  SurfaceStatVO(value=mean_surf, evaluationSpace=self, title="mean_surface")
        self.__stats["std_surf"]=  SurfaceStatVO(value=std_surf, evaluationSpace=self, title="std_surface")
        self.__stats["statRange_surf"]=  SurfaceStatVO(value=statRange_surf, evaluationSpace=self, title="range_surface")


    # own methods
    def save(self):
        for stat in self.__stats.values():
            stat.saveFig()
            stat.saveData()

    # getter and setter methods
    @property
    def datalayerInterface(self):
        return self.__datalayerInterface

    @property
    def name(self):
        return self.__name

    @property
    def dims(self):
        return self.__dims

    @property
    def dimNames(self):
        return self.__dimNames

    @property
    def dimTypes(self):
        return self.__dimTypes

    # statistics
    @property
    def stats(self):
        return self.__stats

