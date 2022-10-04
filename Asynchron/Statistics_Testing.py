
from Model.PredictionContainer import *
from Datalayer.Datalayer import DatalayerInterface
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    dims = [
                                      [-1,0,1],
                                      np.arange(5)/5,
                                      np.arange(6)/5
                                  ]
    data = np.arange(len(dims[0])*len(dims[1])*len(dims[2]))


    predSpace = EvaluationSpaceVO(DatalayerInterface() , name="test",
                                  dims=dims
                                  , mean=data)

    mean = predSpace.mean
    mean.getFigure()
    plt.show()
