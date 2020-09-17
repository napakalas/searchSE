from ..general import getJsonFromPmr, getAllFilesInDir
from ..general import PMR_SERVER, CURRENT_PATH, WORKSPACE_DIR, RESOURCE_DIR
from ..colls.workspace import Workspaces
import git
import os

class Workspaces(Workspaces):
    def __init__(self, *paths):
        super().__init__(*paths)

    def update(self):
        # get or update workspaces
        listWorkspace = self.getListWorkspaces(fromServer=True)
        counter,divider = 0, round(len(listWorkspace)/100)
        print('Updating %d workspaces ...' % len(listWorkspace))
        for url in listWorkspace:
            if counter % divider == 0:
                print(round(counter/divider),end='% ')
            counter += 1
            if url in self.data:
                # update to the latest commit
                self.__synchroWorkspace(url)
            else:
                # get the workspace repository
                self.__cloneWorkspace(url)
        # update status of deprecated workspace to 0
        for workspace in self.data:
            self.data[workspace]['status'] = self.statusC['deprecated'] if workspace not in listWorkspace else self.data[workspace]['status']
        # save Workspaces
        self.dumpJson()
        self.__updateRdf()

    # synchronising workspace in local
    def __synchroWorkspace(self, url):
        workingDir = self.data[url]['workingDir']
        path = os.path.join(CURRENT_PATH, 'workspaces', workingDir)
        repo = git.Repo(path)
        repoCommit = repo.heads[0].commit.hexsha
        try:
            fullUrl = PMR_SERVER + url
            remoteCommit = self.__getRemoteCommit(fullUrl)
            if remoteCommit != repoCommit:
                # pull or update local workspace
                g = git.cmd.Git(path)
                g.pull()
                self.data[url]['commit'] = remoteCommit
                self.data[url]['subModels'] = self.__trackImportedWorkspaces(path)
                self.data[url]['status'] = self.statusC['validating']
        except Exception as e:
            self.data[url]['status'] = self.statusC['deprecated']
            print('\n',e, '\n\t', url, ', repo commit: %s'%(repoCommit), ', workingDir: ',workingDir,'\n')

    # clone workspaces based on provided URL
    def __cloneWorkspace(self, url):
        workingDir = str(len(self.data))
        path = os.path.join(CURRENT_PATH, 'workspaces', workingDir)
        fullUrl = PMR_SERVER + url
        collection = getJsonFromPmr(fullUrl)
        if len(collection) > 0:
            Id = collection['items'][0]['data'][0]['value']
            title = collection['items'][0]['data'][1]['value']
            owner = collection['items'][0]['data'][2]['value']
            description = collection['items'][0]['data'][3]['value']
            storage = collection['items'][0]['data'][4]['value']
            version = collection['version']
        else:
            Id, title, owner, description, storage, version = '', '', '', '', '', ''
        try:
            repo = git.Repo.clone_from(fullUrl, path, branch='master')
            repoCommit = repo.heads[0].commit.hexsha
            subModels = self.__trackImportedWorkspaces(path)
            self.data[url] = {'id': Id, 'workingDir': workingDir, 'title': title, 'owner': owner,
                                    'description': description, 'storage': storage, 'version': version,
                                    'commit': repoCommit, 'status': self.statusC['validating'], 'subModels':subModels}
        except git.exc.GitError as e:
            print('\n', e, '\n')

    def __getRemoteCommit(self,url):
        remote_refs = {}
        g = git.cmd.Git()
        ref = g.ls_remote(url).split('\n')
        hashRef = ref[0].split('\t')
        return hashRef[0]

    # track imported workspaces:
    def __trackImportedWorkspaces(self,path):
        repo = git.Repo(path)
        sms = {}
        for sm in repo.submodules:
            importedWks = sm.url[sm.url.find('.org/')+5:]
            importedWks = importedWks[:-1] if importedWks.endswith('/') else importedWks
            sms[sm.path]={'name':sm.name, 'workspace':importedWks, 'commit':sm.hexsha}
            sourcePath = os.path.join(CURRENT_PATH, 'workspaces', self.data[importedWks]['workingDir'])
            destPath = os.path.join(path,sm.path)
            self.__getImportedWorkspaces(sourcePath, destPath, sm.hexsha)
        return sms

    def __getImportedWorkspaces(self, sourcePath, destPath, importedHexsha):
        if os.path.exists(destPath):
            shutil.rmtree(destPath)
        shutil.copytree(sourcePath, destPath)
        repo = git.Repo(destPath)
        repo.head.reset(importedHexsha, index=True, working_tree=True)
        for sm in repo.submodules:
            importedWks = sm.url[sm.url.find('.org/')+5:]
            importedWks = importedWks[:-1] if importedWks.endswith('/') else importedWks
            sourcePath = os.path.join(CURRENT_PATH, 'workspaces', self.data[importedWks]['workingDir'])
            destPath = os.path.join(destPath,sm.path)
            self.__getImportedWorkspaces(sourcePath, destPath, sm.hexsha)

    def __updateRdf(self):
        graph = rdflib.Graph()
        rdfPaths = getAllFilesInDir(WORKSPACE_DIR)
        for rdfPath in rdfPaths:
            if rdfPath.endswith('.rdf'):
                try:
                    graph.parse(rdfPath, format='application/rdf+xml')
                except:
                    pass
        dumpPickle(graph,CURRENT_PATH,RESOURCE_DIR,'rdf.graph')

    def addCellml(self, id=None, url=None, cellmlId=None):
        if id != None:
            url = self.getUrl(id)
        if url in self.data:
            if 'cellml' in self.data[url]:
                if cellmlId not in self.data[url]['cellml']:
                    self.data[url]['cellml'] += [cellmlId]
            else:
                self.data[url]['cellml'] = [cellmlId]

    def extract(self, sysCellmls):
        for cellmlId, data in sysCellmls.getData().items():
            self.addCellml(url=data['workspace'],cellmlId=data['id'])
        self.dumpJson()
