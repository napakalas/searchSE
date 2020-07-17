from .general import *
from .pmrcollection import IrCollection
from .workspace import Workspaces
from .cellml import Cellmls
from .variable import Variables
from .equation import Maths
from .sedml import Sedmls
from .exposure import Exposures
from .category import Categories
from .view import Views


class Crawler():
    def __init__(self):
        self.workspaces = Workspaces('workspaces', 'resources', 'listOfWorkspace.json',)
        self.exposures = Exposures(self.workspaces, 'resources', 'listOfExposure.json',)
        self.categories = Categories('resources', 'listOfCategory.json')
        self.sedmls = Sedmls(self.workspaces.allWksDir,'resources', 'listOfSedml.json')
        self.sysMaths = Maths('resources', 'listOfMath.json')
        self.sysVars = Variables(self.sysMaths,'resources', 'listOfVariable.json')
        self.cellmls = Cellmls(self.workspaces, self.sedmls, self.sysVars, self.sysMaths, 'resources', 'listOfCellml.json')

    def update(self):
        self.workspaces.update()
        self.exposures.update()
        self.categories.update()
        self.cellmls.update()

    def validate(self):
        """
        This function is to check the validity of all cellml and sedml.
        However, you can only run it from OpenCor iPython because some sedml and
        cellml cause Kernel restart before the function finish.
        """
        self.cellmls.validate()
        self.sedmls.validate()

    def extract(self):
        self.cellmls.extract()
        self.sedmls.extract(self.cellmls, self.sysVars)
        self.workspaces.extract(self.cellmls)
        self.exposures.extract()
        pass

    def load(self):
        pass

    def showStatistic(self):
        self.cellmls.showStatistic()
