from .general import *

class IrCollection:
    def __init__(self, *paths):
        self.dataDict = loadJson(*paths)
        self.paths = os.path.join(currentPath,*paths)
        if len(self.dataDict)==0:
            self.dataDict['data'] = {}
        self.statusC = {}
        self.data = self.dataDict['data']

    def getJson(self):
        return self.dataDict

    def dumpJson(self):
        self.dataDict['status'] = self.statusC
        for k, v in self.dataDict['data'].items():
            if isinstance(v,dict):
                self.dataDict['vars'] = list(v.keys())
            break
        dumpJson(self.dataDict, self.paths)

    def getStatus(self):
        return self.dataDict['status']

    def getData(self):
        return self.data

    def getNewId(self):
        return self.__class__.__name__[:3]+'Id-'+str(len(self.data))

    def addRdf(self, id, rdf, rdfLeaves, cmeta):
        if 'rdf' not in self.data[id]:
            self.data[id]['rdf'] = []
        if 'rdfLeaves' not in self.data[id]:
            self.data[id]['rdfLeaves'] = []
        self.data[id]['rdf'] += rdf
        self.data[id]['rdfLeaves'] += rdfLeaves
        self.data[id]['cmeta'] = cmeta

    def getCMeta(self, id):
        if 'cmeta' in self.data[id]:
            return self.data[id]['cmeta']
        return None
