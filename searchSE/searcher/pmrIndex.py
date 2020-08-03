from ..general import dumpJson, loadJson, regexTokeniser, getTokens
from ..general import RESOURCE_DIR, ALG_BOOL, ALG_BM25

import math

class PmrIndex:

    def __init__(self, fileIndex):
        jsonIndex = loadJson(RESOURCE_DIR, fileIndex)
        self.invIndex = jsonIndex['index']
        self.settings = jsonIndex['setting']
        self.meta = loadJson(RESOURCE_DIR, fileIndex+'_map')

    def getResults(self, query, top, algorithm=ALG_BM25):
        candidates = {}
        if algorithm == ALG_BM25:
            candidates = self.__getResultsBM25(query)
        candidates = {k: v for k, v in list(sorted(candidates.items(), key=lambda item: item[1], reverse=True))[:top]}
        return candidates

    def __getResultsBM25(self, query):
        tokens = getTokens(query,**self.settings)
        candidates = {}
        for token in tokens:
            if token in self.invIndex:
                # calculate IDF
                idf = self.__getIdf(self.meta['general']['totalData'], len(self.invIndex[token]))
                for candidate in self.invIndex[token]:
                    if candidate not in candidates:
                        candidates[candidate] = 0
                    freqTermDoc =  self.invIndex[token][candidate]
                    docLength = self.meta['data'][candidate]['len']
                    avgDataLength = self.meta['general']['totalTerms'] / self.meta['general']['totalData']
                    candidates[candidate] += idf * self.__getTf(freqTermDoc, docLength, avgDataLength)
        return candidates

    def __getIdf(self, totData, totTermData):
        idf = math.log((totData - totTermData + 0.5) / (totTermData + 0.5) + 1)
        return idf

    def __getTf(self, freqTermDoc, docLength, avgDataLength, k1=1.2, b=0.75):
        tf = (freqTermDoc * (k1 + 1)) / (freqTermDoc + k1 * (1 - b + b * docLength / avgDataLength))
        return tf
