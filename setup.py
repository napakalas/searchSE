import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name='BMSE',
    version='0.0.1',
    author="Yuda Munarko",
    author_email="yuda.munarko@gmail.com",
    description="A tool for cellml, variables, and sedml search in PMR",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/napakalas/searchSE",
    packages=setuptools.find_packages(),
    # packages=setuptools.find_namespace_packages(include=['searchSE.*']),
    # namespace_packages=['searchSE'],
    # package_dir={'': 'searchSE'},
    install_requires=[
        'matplotlib',
        'lxml',
        'requests',
        'GitPython',
        'tellurium',
        'pandas',
        'numpy',
        'rdflib',
        'xmltodict',
        'urllib3',
        'beautifulsoup4',
        'sklearn',
        'hdbscan',
        'nltk',
        ],
    classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: GNU General Public License (GPL)",
         "Operating System :: OS Independent",
        ],
    package_data={'': ['*resources/*','sedmlImages/*']},
    )
