from .indexVariable import IndexVariable
from ..general import *
from ..crawler.unit import  Units
from ..crawler.equation import Maths
from ..crawler.variable import Variables
from ..crawler.cellml import Cellmls
from ..crawler.sedml import Sedmls
from ..crawler.workspace import Workspaces
from ..crawler.component import Components
from ..crawler.image import Images


class Searcher:
    def __init__(self, algorithm = ALG_BM25, idxVarFile='invIdxVar-obo-low'):
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

        self.sysUnits = Units(RESOURCE_DIR, RS_UNIT)
        self.sysMaths = Maths(RESOURCE_DIR, RS_MATH)
        self.sysSedmls = Sedmls(RESOURCE_DIR, RS_SEDML)
        self.sysVars = Variables(self.sysMaths, RESOURCE_DIR, RS_VARIABLE)
        self.sysComps = Components(RESOURCE_DIR, RS_COMPONENT)
        self.sysWks = Workspaces(RESOURCE_DIR, RS_WORKSPACE)
        self.sysCellmls = Cellmls(self.sysWks, self.sysSedmls, self.sysVars, self.sysMaths, RESOURCE_DIR, RS_CELLML)
        self.sysImages = Images(RESOURCE_DIR, RS_IMAGE)

    def search(self, query, top=20):
        # classify the query vertically
        # queryTypes = self.__classify(query)

        # get result based on the classification results
        # temporarily just variable search :)
        # the sedml search temporarily is modified variable search

        return self.__sedmlSearch(query, top)

        # return self.__getVariables(query, top)

    def __getVariables(self, query, top):
        resultVars = self.idxVar.getResults(query, top, algorithm=self.algorithm)

        for varId in resultVars:
            varData = {}
            varData['name'] = self.sysVars.getName(varId)
            varData['init'] = self.sysVars.getInit(varId)
            varData['type'] = self.sysVars.getType(varId)
            varUnit = self.sysVars.getUnit(varId)
            varData['unit'] = {'name': self.sysUnits.getNames(varUnit)[0], 'text':self.sysUnits.getText(varUnit)}
            varData['math'] = self.sysVars.getMaths(varId)
            varData['dependent'] = {}
            self.sysVars.getDependents(varId, varDep=varData['dependent'])
            varData['rdfLeaves'] = self.sysVars.getObjLeaves(varId)
            varData['plot'] = [os.path.join(CURRENT_PATH, RESOURCE_DIR, SEDML_IMG_DIR, plot+IMG_EXT) for plot in self.sysVars.getPlots(varId)]
            varData['sedml'] = [os.path.join(PMR_SERVER, self.sysSedmls.getUrl(plot.split('.')[0])) for plot in self.sysVars.getPlots(varId)]
            varData['component'] = self.sysComps.getName(self.sysVars.getCompId(varId))
            varData['compLeaves'] = self.sysComps.getObjLeaves(self.sysVars.getCompId(varId))

            cellmlId = self.sysComps.getCellml(self.sysVars.getCompId(varId))
            varData['cellmlUrl'] = PMR_SERVER + self.sysCellmls.getUrl(id=cellmlId)
            varData['cellmlCaption'] = self.sysCellmls.getCaption(id=cellmlId)
            varData['cellmlImages'] = {varData['cellmlUrl'][:varData['cellmlUrl'].rfind('/')+1]+self.sysImages.getPath(id):self.sysImages.getTitle(id) for id in self.sysCellmls.getImages(id=cellmlId)}
            varData['workspaceUrl'] = PMR_SERVER + self.sysCellmls.getWorkspace(id=cellmlId)
            resultVars[varId] = varData

        return resultVars

    def __sedmlSearch(self, query, top):
        def getVarDataForPlot(varId):
            varData = {}
            varData['name'] = self.sysVars.getName(varId)
            varData['init'] = self.sysVars.getInit(varId)
            varData['type'] = self.sysVars.getType(varId)
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
                        # get cellml images
                        cellmlImages = []
                        for imageId in self.sysCellmls.getImages(id=cellmlId):
                            cellmlImages += [os.path.join(os.path.dirname(resultPlots[plot]['cellmlUrl']),self.sysImages.getPath(imageId))]
                        resultPlots[plot]['cellmlImages'] = cellmlImages
        return resultPlots
