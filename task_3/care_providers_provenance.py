#!/usr/bin/env python3
import argparse
import sys
from datetime import datetime
from io import TextIOWrapper

from rdflib import Graph, Literal, URIRef, BNode
from rdflib.namespace import RDF, XSD, PROV, RDFS, FOAF

from cube_lib.namespaces import NS, NSR


def main():
    args = init_args()
    prov = CareProvidersProv()
    prov.start_transformation()
    prov.end_transformation()
    prov.save_to(args.out)


def init_args():
    parser = argparse.ArgumentParser(
        description='create care providers data cube provenance')
    parser.add_argument(
        '-o', '--out', dest='out', default=sys.stdout.buffer, type=argparse.FileType('wb'),
        help='the file where the provenance should be written')
    return parser.parse_args()


class CareProvidersProv:
    def __init__(self):
        self.__collector = Graph()
        self.__me = URIRef('https://github.com/filipjezek')
        self.__cube = NSR.CareProvidersDataCube
        self.__script = NSR.CareProvidersScript
        self.__datasrc = URIRef(
            'https://opendata.mzcr.cz/data/nrpzs/narodni-registr-poskytovatelu-zdravotnich-sluzeb.csv')
        self.__org = URIRef('https://mff.cuni.cz')
        self.__mhcz = URIRef('https://www.mzcr.cz')
        self.__transformation = NSR.CareProvidersTransformation
        self.__role_raw_data = NSR.roleRawData

        self.__add_activities()
        self.__add_agents()
        self.__add_entities()
        self.__add_roles()

    def __add_entities(self):
        self.__collector.add((self.__cube, RDF.type, PROV.Entity))
        self.__collector.add((self.__cube, RDFS.label, Literal(
            'Care providers data cube', lang='en')))
        self.__collector.add((self.__cube, PROV.wasGeneratedBy, self.__script))
        self.__collector.add((self.__cube, PROV.wasAttributedTo, self.__me))
        self.__collector.add(
            (self.__cube, PROV.wasDerivedFrom, self.__datasrc))

        self.__collector.add((self.__datasrc, RDF.type, PROV.Entity))
        self.__collector.add((
            self.__datasrc, PROV.wasAttributedTo, self.__mhcz))
        self.__collector.add((self.__datasrc, RDFS.label, Literal(
            'Care providers data source', lang='en')))

    def __add_agents(self):
        self.__collector.add((self.__me, RDF.type, PROV.Agent))
        self.__collector.add((self.__me, RDF.type, PROV.Person))
        self.__collector.add((self.__me, FOAF.name, Literal('Filip Ježek')))
        self.__collector.add((self.__me, PROV.actedOnBehalfOf, self.__org))

        self.__collector.add((self.__org, RDF.type, PROV.Agent))
        self.__collector.add((self.__org, RDF.type, PROV.Organization))
        self.__collector.add((self.__org, FOAF.name, Literal(
            'Univerzita Karlova, Matematicko-fyzikální fakulta', lang='cs')))
        self.__collector.add((self.__mhcz, RDF.type, PROV.Agent))
        self.__collector.add((self.__mhcz, RDF.type, PROV.Organization))
        self.__collector.add((self.__mhcz, FOAF.name, Literal(
            'Ministerstvo zdravotnictví České republiky', lang='cs')))

    def __add_activities(self):
        self.__collector.add((self.__transformation, RDF.type, PROV.Activity))

        bnode = BNode()
        self.__collector.add((bnode, RDF.type, PROV.Usage))
        self.__collector.add((bnode, PROV.entity, self.__datasrc))
        self.__collector.add((bnode, PROV.hadRole, self.__role_raw_data))
        self.__collector.add(
            (self.__transformation, PROV.qualifiedUsage, bnode))

    def __add_roles(self):
        self.__collector.add((self.__role_raw_data, RDF.type, PROV.Role))

    def start_transformation(self):
        self.__collector.add(
            (self.__transformation, PROV.startedAtTime, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))

    def end_transformation(self):
        self.__collector.add(
            (self.__transformation, PROV.endedAtTime, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))

    def save_to(self, dest: TextIOWrapper):
        self.__collector.serialize(
            format='ttl', encoding='UTF-8', destination=dest)


if __name__ == '__main__':
    main()
