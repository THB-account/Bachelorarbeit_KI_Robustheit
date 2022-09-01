import numpy as np

class EvaluationCollection:
    def __init__(self):
        self.__container = []
        self.__counter = 0

    # own methods
    # should consist of Methods to calculate values and manage self.__container
    def add(self, element):
        if (self.__container != []):
            self.__container.append(element)
        else:
            raise ValueError("Im Objekt {0} wurde versucht ein Element zu einem Nonetype hinzuzufügen",
                             hex(id(self)))


    def getElement(self, index):
        if index < 0 and index < len(self.__container):
            return self.__container[index]
        else:
            rais IndexError("Trying to access out of bounds")

    # getter and setter
    @property
    def container(self):
        return self.__container.copy()

    @container.setter
    def container(self, container):
        self.__container = container

class PredictionSpaceContainer:
    def __init__(self, n,shape, dtype=np.dtype(np.single), name=""):
        self.__container = np.ndarray(shape= (n,) + shape, dtype=dtype)
        self.__counter = 0
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

    def createAnalysis(self):



        # analysis functions
    def mean(self):
        return np.mean(self.__container, axis=0)

    # getter and setter
    @property
    def container(self):
        return self.__container

    @property
    def counter(self):
        return self.__counter
    @property
    def name(self):
        return self.__name

    @container.setter
    def container(self, container):
        self.__container = container

    @name.setter
    def name(self, name):
        self.__name = name
