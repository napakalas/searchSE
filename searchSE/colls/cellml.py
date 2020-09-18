from ..general import loadPickle
from ..general import CURRENT_PATH,RESOURCE_DIR, WORKSPACE_DIR
from .pmrcollection import PmrCollection
import os
from lxml import etree
import rdflib
import urllib.parse as urilib

class Cellmls(PmrCollection):
    def __init__(self, *paths):
        super().__init__(*paths)
        self.statusC = {'deprecated': 0, 'current': 1, 'validating': 2, 'invalid': 3}
        self.id2Url = {v['id']:k for k, v in self.data.items()}
        self.local2Url = {v['workingDir']+'/'+v['cellml']:k for k, v in self.data.items()}

    def getUrl(self, localPath=None, id=None):
        if localPath != None:
            if localPath in self.local2Url:
                return self.local2Url[localPath]
        elif id != None:
            if id in self.id2Url:
                return self.id2Url[id]
        return None

    def getObjData(self, url=None, localPath=None, id=None, items=[], isCopy=False):
        if localPath != None:
            url = self.getUrl(localPath=localPath)
        elif id != None:
            url = self.getUrl(id=id)
        if url != None:
            if url in self.data:
                return PmrCollection.getObjData(self, id=url, items=items, isCopy=isCopy)
        return {}

    def getWorkspace(self, url=None, localPath=None, id=None):
        objData = self.getObjData(url=url, localPath=localPath, id=id)
        return objData['workspace']

    def getObjLeaves(self, url=None, localPath=None, id=None):
        objData = self.getObjData(url=url, localPath=localPath, id=id)
        leaves = []
        if 'rdfLeaves' in objData:
            for leaf in objData['rdfLeaves']:
                if not leaf.startswith('file:'):
                    leaves += [leaf]
        return leaves

    def getImages(self, url=None, localPath=None, id=None):
        objData = self.getObjData(url=url, localPath=localPath, id=id)
        return objData['images'] if 'images' in objData else []

    def getSedmls(self, url=None, localPath=None, id=None):
        objData = self.getObjData(url=url, localPath=localPath, id=id)
        return objData['sedml'] if 'sedml' in objData else []

    def getCaption(self, url=None, localPath=None, id=None):
        objData = self.getObjData(url=url, localPath=localPath, id=id)
        return objData['caption'] if 'caption' in objData else []

    def getId(self, url=None, localPath=None):
        if localPath != None:
            url = self.getUrl(localPath=localPath)
        if url != None:
            if url in self.data:
                return self.data[url]['id']
        return None

    def getPath(self, url=None, id=None):
        if id != None:
            url = self.getUrl(id=id)
        if url != None:
            if url in self.data:
                return os.path.join(self.data[url]['workingDir'], self.data[url]['cellml'])
        return None

    def showStatistic(self):
        indicator = ['ma','chebi','pr','go','opb','fma','cl','uberon']
        # check rdf files
        rdfFileData = {}
        self.rdfGraph = loadPickle(CURRENT_PATH,RESOURCE_DIR,'rdf.graph')

        # merge all RDF tag in a cellml to self.rdfGraph
        for k, v in self.data.items():
            rdfFileData[k] = {'runable':0,'isRdf':0,'isAnnotated':0,'isSemgen':0}
            rdfFileData[k]['runable'] = 0 if v['status'] == self.statusC['invalid'] else 1
            path = os.path.join(CURRENT_PATH, WORKSPACE_DIR, v['workingDir'],v['cellml'])
            rdfPath = 'file://'+ urilib.quote(path)
            parser = etree.XMLParser(recover=True, remove_comments=True)
            root = etree.parse(path, parser).getroot()
            if 'cmeta' in root.nsmap:
                nsmeta = root.nsmap['cmeta']
            else:
                continue
            rdfElements = root.xpath(".//*[local-name()='RDF']")
            for rdfElement in rdfElements:
                for desc in rdfElement.xpath(".//*[local-name()='Description'][@*[local-name()='about']]"):
                    if any(x in ['rdf','RDF'] for x in desc.nsmap):
                        if 'rdf' in desc.nsmap:
                            att = '{'+desc.nsmap['rdf']+'}about'
                        elif 'RDF' in desc.nsmap:
                            att = '{'+desc.nsmap['RDF']+'}about'
                        if desc.attrib[att].startswith('#'):
                            desc.attrib[att] = rdfPath+desc.attrib[att]
                try:
                    self.rdfGraph.parse(data = etree.tostring(rdfElement))
                except:
                    pass
            # now check the cellml:
            metas = root.xpath(".//@cmeta:id", namespaces={'cmeta':nsmeta})
            if len(metas) > 0:
                rdfFileData[k]['isRdf'] = 1
                rdfFileData[k]['isSemgen'] = 0 if 'semsim' not in root.nsmap else 1
            for meta in metas:
                sbj =rdfPath+'#'+meta
                triples, leaves = self.__getTriplesOfMeta(rdflib.URIRef(sbj))
                # print(meta, leaves)
                for leave in leaves:
                    leave = str(leave).lower()
                    if leave.startswith('http') and any(onto in leave for onto in indicator):
                        rdfFileData[k]['isAnnotated'] = 1
                        break
                    else:
                        rdfFileData[k]['isAnnotated'] = 0
                if rdfFileData[k]['isAnnotated'] == 1:
                    break
        # summarise the statistic:
        summary = {0:{'tot':0,'isRdf':0,'isAnnotated':0,'isSemgen':0},1:{'tot':0,'isRdf':0,'isAnnotated':0,'isSemgen':0}}
        for k, v in rdfFileData.items():
            summary[v['runable']]['tot'] += 1
            summary[v['runable']]['isRdf'] += v['isRdf']
            summary[v['runable']]['isAnnotated'] += v['isAnnotated']
            summary[v['runable']]['isSemgen'] += v['isSemgen']
        print(summary)
