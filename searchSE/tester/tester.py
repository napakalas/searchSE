from ..searcher.searcher import Searcher
from ..general import ALG_BM25, m_c2p, TO_JUPYTER
from py_asciimath.translator.translator import MathML2Tex
from IPython.display import HTML, Markdown, display
import logging
import string
import os
from shutil import copyfile

class Tester:
    def __init__(self):
        self.searcher = Searcher(algorithm=ALG_BM25, idxVarFile='invIdxVar-obo-lemma-low')
        self.viewTemplate = string.Template("""
            <hr style="height:2px;border:none;color:#333;background-color:#333;" />
            <details>
            <summary>${header}</summary>
            <p>
            ${content}
            </p>
            </details>
            """)
        self.cacheDir = os.path.join(os.path.abspath(''),'cache')
        if not os.path.exists(self.cacheDir):
            os.makedirs(self.cacheDir)

    def searchSedmls(self, query):
        result = self.searcher.search(query, top=1000)
        for rs, val in result.items():
            header = 'SEDML: <a href="%s">%s</a> <br>'%(val['url'],val['url'])
            content = ''

            for imageLink in [val['path']]:
                if not os.path.isfile(os.path.join(self.cacheDir, imageLink.rsplit('/',1)[1])):
                    copyfile(imageLink, os.path.join(self.cacheDir, imageLink.rsplit('/',1)[1]))
                content += '<img src="cache/'+imageLink.rsplit('/',1)[1]+'" alt="drawing" style="width:400px;"/><br>'

            if 'cellmlImages' in val:
                for imgUrl in val['cellmlImages']:
                    content += '<img src="'+imgUrl+'" alt="drawing" style="width:400px;"/><br>'

            content += 'CellML: <a href="%s">%s</a> <br>'%(val['cellmlUrl'],val['cellmlUrl'])
            content += 'Workspace: <a href="%s">%s</a> <br>'%(val['workspaceUrl'],val['workspaceUrl'])
            # print exposures
            if len(val['exposures']) > 0:
                content += 'Exposures: <ul>'
                for cellmlUrl in val['exposures']:
                    content += '<li><a href="%s">%s</a> </li>'%(cellmlUrl,cellmlUrl)
                content += '</ul>'

            # print similar cellmls
            if len(val['similarCellmls']) > 0:
                content += 'Similar CellMLs: <ul>'
                for cellmlUrl in val['similarCellmls']:
                    content += '<li><a href="%s">%s</a> </li>'%(cellmlUrl,cellmlUrl)
                content += '</ul>'

            # print maths and dependencies
            content += '<ul>'
            for varId, varData in val['variable'].items():
                content += self.__printMath(varData)
                content += '<hr style="height:1px;border:none;color:#333;background-color:#333;" />'
            content += '</ul>'

            # replace value in html template
            replacer = {'header':header, 'content':content}
            display(HTML(self.viewTemplate.substitute(replacer)))

    def __printMath(self, varData):
        def getVarMd(varData):
            logger = logging.getLogger()
            mathml2tex = MathML2Tex()
            varMd = '<li>' + '; '.join(['<b>name:</b> %s'%varData['name'], '<b>type:</b> %s'%varData['type'], '<b>init:</b> %s'%varData['init']])
            if 'rate' in varData:
                varMd += '; <b>rate:</b> %s'%str(varData['rate'])
            varMd += '; <b>unit:</b> ' + varData['unit']['text'] + '<br>' if 'unit' in varData else '<br>'
            for k, mth in varData['math'].items():
                logger.disabled = True
                lttex = m_c2p(mth, destination=TO_JUPYTER)
                varMd += lttex + "<br>"

                if 'dependent' in varData:
                    if len(varData['dependent']) > 0:
                        varMd += '<ul><li><ul> dependents: '
                        for varIdDept, varDataDept in varData['dependent'].items():
                            varMd += getVarMd(varDataDept)
                        varMd += '</ul></li></ul>'
                logger.disabled = False

            return varMd + '</li>'

        varMd = getVarMd(varData)
        return varMd

    def searchVariables(self, query, top=20):
        result = self.searcher._Searcher__getVariables(query, top=top)

        for rs, val in result.items():
            header = '; '.join(['<b>name:</b> %s'%val['name'], '<b>type:</b> %s'%val['type'], '<b>init:</b> %s'%val['init']])
            if 'rate' in val:
                header += '; <b>rate:</b> %s'%str(val['rate'])
            header += '; <b>unit:</b> ' + val['unit']['text'] if 'unit' in val else ''
            content = 'CellML: <a href="%s">%s</a> <br>'%(val['cellmlUrl'],val['cellmlUrl'])
            content += 'Workspace: <a href="%s">%s</a> <br>'%(val['workspaceUrl'],val['workspaceUrl'])
            # print exposures
            if len(val['exposures']) > 0:
                content += 'Exposures: <ul>'
                for cellmlUrl in val['exposures']:
                    content += '<li><a href="%s">%s</a> </li>'%(cellmlUrl,cellmlUrl)
                content += '</ul>'

            # print similar cellmls
            if len(val['similarCellmls']) > 0:
                content += 'Similar CellMLs: <ul>'
                for cellmlUrl in val['similarCellmls']:
                    content += '<li><a href="%s">%s</a> </li>'%(cellmlUrl,cellmlUrl)
                content += '</ul>'

            # print images
            if 'cellmlImages' in val:
                for imgUrl in val['cellmlImages']:
                    content += '<img src="'+imgUrl+'" alt="drawing" style="width:400px;"/><br>'


            content += self.__printMath(val)
            content += '<hr style="height:1px;border:none;color:#333;background-color:#333;" />'

            replacer = {'header':header, 'content':content}
            display(HTML(self.viewTemplate.substitute(replacer)))
