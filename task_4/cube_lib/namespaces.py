#!/usr/bin/env python3
from rdflib import Namespace

NS = Namespace('https://filipjezek.github.io/ontology#')
NSR = Namespace('https://filipjezek.github.io/resources/')
# We use custom Namespace here as the generated is limited in content
# https://rdflib.readthedocs.io/en/stable/_modules/rdflib/namespace/_RDFS.html
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
SDMX_DIM = Namespace('http://purl.org/linked-data/sdmx/2009/dimension#')
SDMX_CON = Namespace('http://purl.org/linked-data/sdmx/2009/concept#')
SDMX_MEA = Namespace('http://purl.org/linked-data/sdmx/2009/measure#')

DCT = Namespace('http://purl.org/dc/terms/')
