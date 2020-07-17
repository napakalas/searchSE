import json
import os, os.path
import requests
from lxml import etree
import pickle
import gzip
import io
import git
from git import Repo
from pydriller import RepositoryMining
import opencor as oc
import gc
from tellurium.utils import omex
import pandas as pd
import re
import rdflib
import xmltodict
import sys
import shutil
import urllib.parse as urilib

"""init global variable"""
currentPath = os.path.dirname(os.path.realpath(__file__))  # use this on real python
# currentPath = os.path.abspath('')#use this on jupyter
pmr_server = 'https://models.physiomeproject.org/'

def loadJson(*paths):
    file = os.path.join(currentPath, *paths)
    isExist = os.path.exists(file)
    if isExist:
        with open(file, 'r') as fp:
            data = json.load(fp)
        fp.close()
        return data
    else:
        return {}

def dumpJson(data, file):
    print(file)
    with open(file, 'w') as fp:
        json.dump(data, fp)
    fp.close()


def saveToFlatFile(data, *paths):
    file = os.path.join(currentPath, *paths)
    f = open(file, 'w+')
    for datum in data:
        f.write(str(datum).replace('\n', ' ').replace('\r', ' ') + '\n')
    f.close()

def loadFromFlatFile(*paths):
    file = os.path.join(currentPath, *paths)
    try:
        f = open(file, 'r')
        lines = f.readlines()
        f.close()
        return lines
    except:
        return []

def saveBinaryInteger(data, *paths):
    import struct
    file = os.path.join(currentPath, *paths)
    with open(file, "wb") as f:
        for x in data:
            f.write(struct.pack('i', x))  # 4bytes
    f.close()

def loadBinaryInteger(*paths):
    import struct
    file = os.path.join(currentPath, *paths)
    with open(file, 'rb') as f:
        bdata = []
        while True:
            bytes = f.read(4)
            if bytes == b'':
                break
            else:
                bdata.append(struct.unpack('i', bytes)[0])  # 4bytes
    f.close()
    return bdata

def dumpPickle(data, *paths):
    filename = os.path.join(currentPath, *paths)
    file = gzip.GzipFile(filename, 'wb')
    pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
    file.close()

def loadPickle(*paths):
    filename = os.path.join(currentPath, *paths)
    file = gzip.GzipFile(filename, 'rb')
    data = pickle.load(file)
    file.close()
    return data

def getAllFilesInDir(drc):
    lst = []
    for path, subdirs, files in os.walk(drc):
        for name in files:
            lst += [os.path.join(path, name)]
    return lst

# get list of URLs inside a particulat URL in the PMR
def getUrlFromPmr(url):
    r = requests.get(
        url, headers={"Accept": "application/vnd.physiome.pmr2.json.1"})
    urls = [link['href'] for link in r.json()['collection']['links']]
    return urls

# get json from PMR based on URL address
def getJsonFromPmr(url):
    r = requests.get(
        url, headers={"Accept": "application/vnd.physiome.pmr2.json.1"})
    try:
        return r.json()['collection']
    except:
        return {}

greek_code2name = {
    u'\u0391': 'Alpha',
    u'\u0392': 'Beta',
    u'\u0393': 'Gamma',
    u'\u0394': 'Delta',
    u'\u0395': 'Epsilon',
    u'\u0396': 'Zeta',
    u'\u0397': 'Eta',
    u'\u0398': 'Theta',
    u'\u0399': 'Iota',
    u'\u039A': 'Kappa',
    u'\u039B': 'Lamda',
    u'\u039C': 'Mu',
    u'\u039D': 'Nu',
    u'\u039E': 'Xi',
    u'\u039F': 'Omicron',
    u'\u03A0': 'Pi',
    u'\u03A1': 'Rho',
    u'\u03A3': 'Sigma',
    u'\u03A4': 'Tau',
    u'\u03A5': 'Upsilon',
    u'\u03A6': 'Phi',
    u'\u03A7': 'Chi',
    u'\u03A8': 'Psi',
    u'\u03A9': 'Omega',
    u'\u03B1': 'alpha',
    u'\u03B2': 'beta',
    u'\u03B3': 'gamma',
    u'\u03B4': 'delta',
    u'\u03B5': 'epsilon',
    u'\u03B6': 'zeta',
    u'\u03B7': 'eta',
    u'\u03B8': 'theta',
    u'\u03B9': 'iota',
    u'\u03BA': 'kappa',
    u'\u03BB': 'lamda',
    u'\u03BC': 'mu',
    u'\u03BD': 'nu',
    u'\u03BE': 'xi',
    u'\u03BF': 'omicron',
    u'\u03C0': 'pi',
    u'\u03C1': 'rho',
    u'\u03C3': 'sigma',
    u'\u03C4': 'tau',
    u'\u03C5': 'upsilon',
    u'\u03C6': 'phi',
    u'\u03C7': 'chi',
    u'\u03C8': 'psi',
    u'\u03C9': 'omega',
}

greek_name2code = { v:k for k, v in greek_code2name.items()}

def m_c2p(math_c):
    preff = '{http://www.w3.org/1998/Math/MathML}'
    if '<math ' not in math_c:
        math_c = '<math xmlns="http://www.w3.org/1998/Math/MathML">' + math_c + '</math>'
    mml_dom = etree.fromstring(math_c)
    xslt = etree.parse('ctopff.xsl')
    transform = etree.XSLT(xslt)
    mmldom = transform(mml_dom)
    root = mmldom.getroot()
    for name in root.iter(preff + 'mi'):
        comps = name.text.split('_')
        if len(comps) > 1:
            comps = ['&' + x + ';' if x in greek_name2code else x for x in comps]
            # comps = [greek_name2code[x] if x in greek_name2code else x for x in comps]
            name.tag = preff + 'msub'
            name.text = ''
            name.attrib.pop('mathvariant')
            rightEl = etree.Element(
                preff + 'mn' if comps[len(comps) - 1].isnumeric() else 'mi', mathvariant='italic')
            rightEl.text = comps[len(comps) - 1]
            leftEl = etree.Element(
                preff + 'mn' if comps[len(comps) - 2].isnumeric() else 'mi', mathvariant='italic')
            leftEl.text = comps[len(comps) - 2]
            if len(comps) > 2:
                subEl = etree.Element(preff + 'msub')
                subEl.append(leftEl)
                subEl.append(rightEl)
                for i in range(len(comps) - 3, -1, -1):
                    rightEl = subEl
                    leftEl = etree.Element(
                        preff + 'mn' if comps[i].isnumeric() else 'mi', mathvariant='italic')
                    leftEl.text = comps[i]
                    subEl = etree.Element(preff + 'msub')
                    subEl.append(leftEl)
                    subEl.append(rightEl)
            name.append(leftEl)
            name.append(rightEl)
    for elem in root.iter('*'):
        if elem.text != None:
            elem.text = elem.text.strip()
    return str(mmldom).replace('·', '&#xB7;').replace('−', '-')
