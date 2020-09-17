from ..general import *
from .workspace import Workspaces
from .cellml import Cellmls
from .variable import Variables
from .equation import Maths
from .sedml import Sedmls
from .exposure import Exposures
from .category import Categories
from .view import Views
from .unit import Units
from .component import Components
from .image import Images


class Crawler():
    def __init__(self):
        self.workspaces = Workspaces(RESOURCE_DIR, RS_WORKSPACE)
        self.exposures = Exposures(self.workspaces, RESOURCE_DIR, RS_EXPOSURE)
        self.categories = Categories(RESOURCE_DIR, RS_CATEGORY)
        self.sedmls = Sedmls(RESOURCE_DIR, RS_SEDML)
        self.sysMaths = Maths(RESOURCE_DIR, RS_MATH)
        self.sysVars = Variables(self.sysMaths,RESOURCE_DIR, RS_VARIABLE)
        self.sysUnits = Units(RESOURCE_DIR, RS_UNIT)
        self.sysComps = Components(RESOURCE_DIR, RS_COMPONENT)
        self.sysImages = Images(RESOURCE_DIR, RS_IMAGE)
        self.cellmls = Cellmls(self.workspaces, self.sedmls, self.sysImages, self.sysComps, self.sysVars, self.sysUnits, self.sysMaths, RESOURCE_DIR, RS_CELLML)

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

    def load(self):
        pass

    def showStatistic(self):
        self.cellmls.showStatistic()
