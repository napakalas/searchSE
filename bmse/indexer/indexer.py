from ..general import RESOURCE_DIR, CURRENT_PATH, ONTOLOGY_DIR
from ..general import RS_VARIABLE, RS_CELLML, RS_CLUSTERER, RS_ONTOLOGY
from ..general import loadJson, dumpJson, saveToFlatFile, getAllFilesInDir
from ..general import loadFromFlatFile, saveBinaryInteger, loadBinaryInteger
from ..general import loadPickle, dumpPickle, regexTokeniser, getTokens
from ..colls.variable import Variables
from ..colls.cellml import Cellmls
from ..colls.equation import Maths

from .clusterer import CellmlClusterer

import os
import pandas as pd

class Indexer:
    FEATURE_DOCUMENT = 0
    FEATURE_RDF = 1
    FEATURE_ONTO = 2
    FEATURE_DOI = 3

    #LIST OF METHODS
    MTD_BAG_OF_WORDS = 0

    def __init__(self):
        """load ontologies"""
        self.__loadOntologies()

        """load all required data"""
        self.__loadData()

        """create clusterer file """
        self.__createClusterer()

        """(soon will be modified so Indexer will be an independent object,
           do not load ontologies other data and cluster)"""

    def createIndexVariable(self, destFile, lower=False, stem=None, lemma=False):
        self.invIdxVar = {}
        self.metaVar = {'general':{'totalTerms':0, 'totalData':len(self.vars['data'])}, 'data':{}}
        for varId, value in self.vars['data'].items():
            text = ''
            """index from RDF"""
            # try:
            if 'rdfLeaves' in value:
                for leaf in value['rdfLeaves']:
                    leaf = str(leaf).strip()
                    if leaf.startswith('http://'):
                        text += self.__getOntoClassText(leaf) + ' '
                    elif leaf.startswith('file://'):
                        pass
                    else:
                        text += leaf + ' '
            # modify text to multiple setting and get tokens
            tokens = getTokens(text, lower=lower, stem=stem, lemma=lemma)
            self.__generateTermsIndex(varId, tokens)
            self.settings = {'lower':lower, 'stem':stem, 'lemma':lemma}
            # save variable local and general metadata
            self.metaVar['data'][varId] = {'len':len(tokens)}
            self.metaVar['general']['totalTerms'] += len(tokens)

        dumpJson({'setting':self.settings, 'index':self.invIdxVar}, RESOURCE_DIR, destFile)
        dumpJson(self.metaVar, RESOURCE_DIR, destFile+'_map')
        print(len(self.ontologies.index))

    def __getOntoClassText(self, classId):
        classId = self.__parseOntoClassId(classId)
        df = self.ontologies
        if classId in df.index:
            # temporarily, extract all textual information
            text = classId + '. '
            dfClassId = df.loc[classId]
            # print(classId, dfClassId.index)
            for key in dfClassId.index:
                if type(dfClassId[key]) == str:
                    text += key + ' : ' + dfClassId[key] + '. '
            return text
        return ''

    def __parseOntoClassId(self, classId):
        idPart = classId[classId.rfind('/')+1:]
        idPart = idPart.replace('_',':')
        if len(idPart.split(':')) >= 2:
            return idPart

    def __generateTermsIndex(self, varId, tokens):
        for token in tokens:
            if token not in self.invIdxVar:
                self.invIdxVar[token] = {}
            if varId not in self.invIdxVar[token]:
                self.invIdxVar[token][varId] = 0
            self.invIdxVar[token][varId] += 1

    def getFeatures(self, *featureTypes):
        for featureType in featureTypes:
            if featureType in Indexer.FEATURE_DOCUMENT:
                self.__getFeatureDocument()
            elif featureType in Indexer.FEATURE_RDF:
                self.__getFeatureRdf()
            elif featureType in Indexer.FEATURE_ONTO:
                self.__getFeatureOnto()
            elif featureType in Indexer.FEATURE_DOI:
                self.__getFeatureDoi()

    def __getFeatureDocument(self):
        pass

    def __getFeatureRdf(self):
        pass

    def __getFeatureOnto(self):
        pass

    def __getFeatureDoi(self):
        pass

    def buildMap(self):
        pass

    def __loadOntologies(self):
        print('Loading ontologies ...')
        listData, dfCsv = [], pd.DataFrame()
        allFiles = getAllFilesInDir(ONTOLOGY_DIR)
        if any(RS_ONTOLOGY in file for file in allFiles):
            self.ontologies = loadPickle(ONTOLOGY_DIR,RS_ONTOLOGY)
            self.ontoName = {idx.split(':')[0] for idx in self.ontologies.index if idx[0].isupper() and ':' in idx}
            return
        for ontoFile in allFiles:
            if ontoFile.endswith('.obo'):
                with open(ontoFile) as fp:
                    while True:
                        line = fp.readline()
                        if not line:
                            break
                        line = line.strip()

                        if line == '[Term]':
                            data = {}
                            while True:
                                line = fp.readline().strip()
                                keyVals = line.split(': ',1)
                                if len(keyVals) == 2:
                                    if keyVals[0] not in data:
                                        data[keyVals[0]] = keyVals[1]
                                    else:
                                        data[keyVals[0]] += '|'+keyVals[1]
                                if not line:
                                    listData += [data]
                                    break
            elif '.csv' in ontoFile:
                df = pd.read_csv(ontoFile,sep=',',header=0,index_col='Class ID')
                dfCsv = dfCsv.append(df,sort=False)
        # tranform dfCsv
        dfCsv = dfCsv.dropna(axis='columns', how='all')
        dfCsv = dfCsv.rename(index=lambda s: s[s.rfind('/')+1:])
        dfCsv = dfCsv.rename(index=lambda s: s[s.rfind('#')+1:].replace('_',':'))
        dfCsv['synonym'] = dfCsv['synonyms'].fillna('')  + ('|'+dfCsv['synonym']).fillna('')
        dfCsv = dfCsv.drop(columns=['synonyms','definition','preferred label','alternative label',
                                   'http://www.w3.org/2000/01/rdf-schema#label',
                                   'http://data.bioontology.org/metadata/prefixIRI'])
        dfCsv = dfCsv.rename(columns={'http://www.w3.org/2000/01/rdf-schema#comment':'comment',
                                      'http://purl.org/dc/elements/1.1/creator':'created_by',
                                      'http://bhi.washington.edu/OPB#discussion':'discussion',
                                      'http://bhi.washington.edu/OPB#classTerm':'classTerm',
                                      'Definitions':'def', 'Preferred Label':'name'})
        # transform df
        df = df.dropna(axis='columns', how='all')
        df = pd.DataFrame(listData)
        df = df.set_index('id')
        df = df.append(dfCsv, sort=False)
        df = df.groupby(df.index).first() # delete duplicate
        dumpPickle(df, ONTOLOGY_DIR, RS_ONTOLOGY)
        self.ontologies = df
        self.ontoName = {idx.split(':')[0] for idx in df.index if idx[0].isupper() and ':' in idx}

    def __loadData(self):
        print('Loading required data, e.g. cellml, sedml, variable, workspaces, etc ... ')
        self.vars = loadJson(RESOURCE_DIR, RS_VARIABLE)
        self.cellmls = loadJson(RESOURCE_DIR, RS_CELLML)

    def __createClusterer(self):
        print('Create clusterer with XPath and structur features using HDBSCAN')
        if not os.path.exists(os.path.join(CURRENT_PATH, RESOURCE_DIR, RS_CLUSTERER)):
            clusterer = CellmlClusterer(cellmls=self.cellmls)
            dumpJson(clusterer.getDict(), RESOURCE_DIR, RS_CLUSTERER)

    def close(self):
        self.__closeOntologies()

    def __closeOntologies(self):
        del self.ontologies
        import gc
        gc.collect()
