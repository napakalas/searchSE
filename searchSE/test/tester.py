from ..searcher.searcher import Searcher
from ..general import ALG_BM25, m_c2p, TO_JUPYTER
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib as mpl
from py_asciimath.translator.translator import MathML2Tex
from IPython.display import HTML, Markdown, display
import logging

class Tester:
    def __init__(self):
        self.searcher = Searcher(algorithm=ALG_BM25, idxVarFile='invIdxVar-obo-lemma-low')

    def searchTest(self, query):
        result = self.searcher.search(query, top=1000)
        for rs, val in result.items():
            images = [val['path']]
            if 'cellmlImages' in val:
                for i in range(len(val['cellmlImages'])-1, -1, -1):
                    try:
                        urllib.request.urlopen(val['cellmlImages'][i])
                    except:
                        val['cellmlImages'].pop(i)
                images += val['cellmlImages']

            fig=plt.figure(figsize=(10,10))
            for i in range(len(images)):
                img = mpimg.imread(images[i])
                fig.add_subplot(1, len(images), i+1)
                plt.imshow(img)
            plt.show()

            # mpl.rcParams['figure.dpi']= 150
            # img=mpimg.imread(val['path'])
            # imgplot = plt.imshow(img, interpolation='nearest')
            # plt.show()
            display(Markdown('SEDML: [%s](%s)'%(val['url'],val['url'])))
            display(Markdown('CellML: [%s](%s)'%(val['cellmlUrl'],val['cellmlUrl'])))
            display(Markdown('Workspace: [%s](%s)'%(val['workspaceUrl'],val['workspaceUrl'])))
            for varId, varData in val['variable'].items():
                self.__printMath(varData)
        # print(result)

    def __printMath(self, varData):
        def printmd(string):
            display(Markdown(string))

        def getVarMd(varData, indent):
            logger = logging.getLogger()
            mathml2tex = MathML2Tex()
            space =''
            for i in range(indent):
                space += '\n   '
            indent+=1
            varMd = space + '; '.join(['* name: %s'%varData['name'], 'type: %s'%varData['type'], 'init: %s'%varData['init']])
            varMd += '; ' + varData['unit']['text'] + '<br>' if 'unit' in varData else '<br>'
            for k, mth in varData['math'].items():
                logger.disabled = True
                lttex = m_c2p(mth, destination=TO_JUPYTER)
                varMd += lttex + "<br>"

                if 'dependent' in varData:
                    varMd += 'dependents: <br>'
                    for varIdDept, varDataDept in varData['dependent'].items():
                        varMd += getVarMd(varDataDept, indent=indent)
                logger.disabled = False
            return varMd

        indent = 0
        varMd = getVarMd(varData, indent)

        printmd(varMd)
