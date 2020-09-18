from .indexVariable import IndexVariable
from ..general import *
from ..colls.unit import  Units
from ..colls.equation import Maths
from ..colls.variable import Variables
from ..colls.cellml import Cellmls
from ..colls.sedml import Sedmls
from ..colls.workspace import Workspaces
from ..colls.component import Components
from ..colls.image import Images
import os

class Searcher:
    def __init__(self, algorithm=ALG_BM25, idxVarFile='invIdxVar-obo-lemma-low'):
        """Initialise ...

        Parameters
        ----------
        idxVarFile : str
            The name of the variavle file index.
        idxCellmlFile : str
            The name of the cellml file index.
        idxSedmlFile : str
            The name of the sedml file index.
        idxWorkspaceFile : str
            The name of the workspace file index.
        idxWorkspaceFile : str
            The name of the workspace file index.
        ....

        Returns
        -------
        list
            a list of strings used that are the header columns
        """
        self.algorithm = algorithm

        self.idxVar = IndexVariable(idxVarFile)

        self.clusterer = loadPickle(RESOURCE_DIR, RS_CLUSTERER)

        self.sysUnits = Units(RESOURCE_DIR, RS_UNIT)
        self.sysMaths = Maths(RESOURCE_DIR, RS_MATH)
        self.sysSedmls = Sedmls(RESOURCE_DIR, RS_SEDML)
        self.sysVars = Variables(self.sysMaths, RESOURCE_DIR, RS_VARIABLE)
        self.sysComps = Components(RESOURCE_DIR, RS_COMPONENT)
        self.sysWks = Workspaces(RESOURCE_DIR, RS_WORKSPACE)
        self.sysCellmls = Cellmls(RESOURCE_DIR, RS_CELLML)
        self.sysImages = Images(RESOURCE_DIR, RS_IMAGE)

    def search(self, query, top=20):
        # classify the query vertically
        # queryTypes = self.__classify(query)

        # get result based on the classification results
        # temporarily just variable search :)
        # the sedml search temporarily is modified variable search

        return self.__searchSedmls(query, top)

        # return self.__getVariables(query, top)

    def __getVariables(self, query, top):
        resultVars = self.idxVar.getResults(query, top, algorithm=self.algorithm)

        for varId in resultVars:
            varData = {}
            # get main information
            varData['name'] = self.sysVars.getName(varId)
            varData['init'] = self.sysVars.getInit(varId)
            varData['type'] = self.sysVars.getType(varId)
            if varData['type'] == 'state':
                varData['rate'] = self.sysVars.getRate(varId)
            # get units
            varUnit = self.sysVars.getUnit(varId)
            varData['unit'] = {'name': self.sysUnits.getNames(varUnit)[0], 'text':self.sysUnits.getText(varUnit)}
            # get math
            varData['math'] = self.sysVars.getMaths(varId)
            # get maths' dependents
            varData['dependent'] = {}
            self.sysVars.getDependents(varId, varDep=varData['dependent'])
            # get leaves
            varData['rdfLeaves'] = self.sysVars.getObjLeaves(varId)
            # get sedmls and plot
            varData['plot'] = [os.path.join(CURRENT_PATH, RESOURCE_DIR, SEDML_IMG_DIR, plot+IMG_EXT) for plot in self.sysVars.getPlots(varId)]
            varData['sedml'] = [os.path.join(PMR_SERVER, self.sysSedmls.getUrl(plot.split('.')[0])) for plot in self.sysVars.getPlots(varId)]
            #get components
            varData['component'] = self.sysComps.getName(self.sysVars.getCompId(varId))
            varData['compLeaves'] = self.sysComps.getObjLeaves(self.sysVars.getCompId(varId))
            # get cellml, workspace, images
            cellmlId = self.sysComps.getCellml(self.sysVars.getCompId(varId))
            varData['cellmlUrl'] = PMR_SERVER + self.sysCellmls.getUrl(id=cellmlId)
            varData['cellmlCaption'] = self.sysCellmls.getCaption(id=cellmlId)
            # varData['cellmlImages'] = [varData['cellmlUrl'][:varData['cellmlUrl'].rfind('/')+1]+self.sysImages.getPath(id) for id in self.sysCellmls.getImages(id=cellmlId)]
            varData['workspaceUrl'] = PMR_SERVER + self.sysCellmls.getWorkspace(id=cellmlId)

            # get exposures
            exposures = self.sysWks.getExposures(url=self.sysCellmls.getWorkspace(id=cellmlId))
            varData['exposures'] = [PMR_SERVER + exposure for exposure in exposures.keys()]
            # get similar cellml using cluster
            similarCellmls = self.clusterer.getSimCellmlsByCluster(self.sysCellmls.getUrl(id=cellmlId)).keys()
            varData['similarCellmls'] = [PMR_SERVER + url for url in similarCellmls]

            # get cellml images
            cellmlImages = []
            for imageId in self.sysCellmls.getImages(id=cellmlId):
                imagePath = os.path.join(CURRENT_PATH, WORKSPACE_DIR, os.path.dirname(self.sysCellmls.getPath(id=cellmlId)),self.sysImages.getPath(imageId))
                if os.path.exists(imagePath):
                    cellmlImages += [os.path.join(os.path.dirname(varData['cellmlUrl']),self.sysImages.getPath(imageId))]
            # get cellml images from other cellml / workspaces if not found
            if len(cellmlImages) == 0:
                for similarCellml in similarCellmls:
                    for imageId in self.sysCellmls.getImages(url=similarCellml):
                        imagePath = os.path.join(CURRENT_PATH, WORKSPACE_DIR, os.path.dirname(self.sysCellmls.getPath(url=similarCellml)),self.sysImages.getPath(imageId))
                        if os.path.exists(imagePath):
                            cellmlImages += [os.path.join(os.path.dirname(PMR_SERVER + similarCellml),self.sysImages.getPath(imageId))]
            varData['cellmlImages'] = cellmlImages

            resultVars[varId] = varData

        return resultVars

    def __searchSedmls(self, query, top):
        def getVarDataForPlot(varId):
            varData = {}
            varData['name'] = self.sysVars.getName(varId)
            varData['init'] = self.sysVars.getInit(varId)
            varData['type'] = self.sysVars.getType(varId)
            if varData['type'] == 'state':
                varData['rate'] = self.sysVars.getRate(varId)
            varUnit = self.sysVars.getUnit(varId)
            varData['unit'] = {'name': self.sysUnits.getNames(varUnit)[0], 'text':self.sysUnits.getText(varUnit)}
            varData['math'] = self.sysVars.getMaths(varId)
            varData['dependent'] = {}
            self.sysVars.getDependents(varId, varDep=varData['dependent'])
            varData['rdfLeaves'] = self.sysVars.getObjLeaves(varId)
            return varData

        resultVars = self.idxVar.getResults(query, top, algorithm=self.algorithm)
        resultPlots = {}
        # for each variable, identify the plot and store in a resultPlots
        for varId in resultVars:
            varData = {}
            plots = self.sysVars.getPlots(varId)
            if len(plots) > 0:
                for plot in plots:
                    if plot not in resultPlots:
                        plotData = {}
                        plotData['variable'] = {}
                        sedmlId,plotId = plot.split('.')
                        varIdsPlot = self.sysSedmls.getVariables(sedmlId, plot=plotId)
                        for varIdPlot in varIdsPlot:
                            if varIdPlot not in plotData['variable']:
                                plotData['variable'][varIdPlot] = getVarDataForPlot(varIdPlot)
                        resultPlots[plot]=plotData
                        resultPlots[plot]['path'] = os.path.join(CURRENT_PATH, RESOURCE_DIR, SEDML_IMG_DIR, plot+IMG_EXT)
                        resultPlots[plot]['url'] = PMR_SERVER+self.sysSedmls.getUrl(sedmlId)
                        resultPlots[plot]['workspaceUrl'] = PMR_SERVER+self.sysSedmls.getWorkspace(sedmlId)
                        cellmlId = self.sysSedmls.getCellmlId(sedmlId)
                        resultPlots[plot]['cellmlUrl'] = PMR_SERVER + self.sysCellmls.getUrl(id=cellmlId)
                        # get exposures
                        exposures = self.sysWks.getExposures(url=self.sysCellmls.getWorkspace(id=cellmlId))
                        resultPlots[plot]['exposures'] = [PMR_SERVER + exposure for exposure in exposures.keys()]
                        # get similar cellml using cluster
                        similarCellmls = self.clusterer.getSimCellmlsByCluster(self.sysCellmls.getUrl(id=cellmlId)).keys()
                        resultPlots[plot]['similarCellmls'] = [PMR_SERVER + url for url in similarCellmls]

                        # get cellml images
                        cellmlImages = []
                        for imageId in self.sysCellmls.getImages(id=cellmlId):
                            imagePath = os.path.join(CURRENT_PATH, WORKSPACE_DIR, os.path.dirname(self.sysCellmls.getPath(id=cellmlId)),self.sysImages.getPath(imageId))
                            if os.path.exists(imagePath):
                                cellmlImages += [os.path.join(os.path.dirname(resultPlots[plot]['cellmlUrl']),self.sysImages.getPath(imageId))]
                        # get cellml images from other cellml / workspaces if not found
                        if len(cellmlImages) == 0:
                            for similarCellml in similarCellmls:
                                for imageId in self.sysCellmls.getImages(url=similarCellml):
                                    imagePath = os.path.join(CURRENT_PATH, WORKSPACE_DIR, os.path.dirname(self.sysCellmls.getPath(url=similarCellml)),self.sysImages.getPath(imageId))
                                    if os.path.exists(imagePath):
                                        cellmlImages += [os.path.join(os.path.dirname(PMR_SERVER + similarCellml),self.sysImages.getPath(imageId))]
                        resultPlots[plot]['cellmlImages'] = cellmlImages

        return resultPlots

    def __getOtherCellms(cellmlId):
        url = self.sysCellmls.getUrl(id=cellmlId)
        similarCellmls = self.clusterer.getSimCellmlsByCluster(url).keys()
