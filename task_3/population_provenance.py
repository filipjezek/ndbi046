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
    prov = PopulationProv()
    prov.start_county_conversion()
    prov.end_county_conversion()
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


class PopulationProv:
    def __init__(self):
        self.__collector = Graph()
        self.__me = URIRef('https://github.com/filipjezek')
        self.__cube = NSR.PopulationDataCube
        self.__preprocessed = NSR.PreprocessedPopulationData
        self.__script = NSR.PopulationScript
        self.__county_script = NSR.CountyTransformationScript
        self.__datasrc = URIRef(
            'https://www.czso.cz/documents/10180/184344914/130141-22data2021.csv')
        self.__countysrc = URIRef(
            'https://skoda.projekty.ms.mff.cuni.cz/ndbi046/seminars/02/číselník-okresů-vazba-101-nadřízený.csv')
        self.__org = URIRef('https://mff.cuni.cz')
        self.__czso = URIRef('https://www.czso.cz')
        self.__skoda = URIRef('https://skodapetr.github.io')
        self.__county_conversion = NSR.CountyConversion
        self.__transformation = NSR.PopulationTransformation
        self.__role_raw_data = NSR.roleRawData

        self.__add_activities()
        self.__add_agents()
        self.__add_entities()
        self.__add_roles()

    def __add_entities(self):
        self.__collector.add((self.__cube, RDF.type, PROV.Entity))
        self.__collector.add((self.__cube, RDFS.label, Literal(
            'Population data cube', lang='en')))
        self.__collector.add((self.__cube, PROV.wasGeneratedBy, self.__script))
        self.__collector.add((self.__cube, PROV.wasAttributedTo, self.__me))
        self.__collector.add(
            (self.__cube, PROV.wasDerivedFrom, self.__preprocessed))

        self.__collector.add((self.__preprocessed, RDF.type, PROV.Entity))
        self.__collector.add((self.__preprocessed, RDFS.label, Literal(
            'Preprocessed population data', lang='en')))
        self.__collector.add(
            (self.__preprocessed, PROV.wasGeneratedBy, self.__county_conversion))
        self.__collector.add(
            (self.__preprocessed, PROV.wasAttributedTo, self.__me))
        self.__collector.add(
            (self.__preprocessed, PROV.wasDerivedFrom, self.__countysrc))
        self.__collector.add(
            (self.__preprocessed, PROV.wasDerivedFrom, self.__datasrc))

        self.__collector.add((self.__datasrc, RDF.type, PROV.Entity))
        self.__collector.add((
            self.__datasrc, PROV.wasAttributedTo, self.__czso))
        self.__collector.add((self.__datasrc, RDFS.label, Literal(
            'Population data source', lang='en')))

        self.__collector.add((self.__countysrc, RDF.type, PROV.Entity))
        self.__collector.add((
            self.__datasrc, PROV.wasAttributedTo, self.__skoda))
        self.__collector.add((self.__countysrc, RDFS.label, Literal(
            'County codes data source', lang='en')))

    def __add_agents(self):
        self.__collector.add((self.__me, RDF.type, PROV.Agent))
        self.__collector.add((self.__me, RDF.type, PROV.Person))
        self.__collector.add((self.__me, FOAF.name, Literal('Filip Ježek')))
        self.__collector.add((self.__me, PROV.actedOnBehalfOf, self.__org))

        self.__collector.add((self.__skoda, RDF.type, PROV.Agent))
        self.__collector.add((self.__skoda, RDF.type, PROV.Person))
        self.__collector.add((self.__skoda, FOAF.name, Literal('Petr Škoda')))
        self.__collector.add((self.__skoda, PROV.actedOnBehalfOf, self.__org))

        self.__collector.add((self.__org, RDF.type, PROV.Agent))
        self.__collector.add((self.__org, RDF.type, PROV.Organization))
        self.__collector.add((self.__org, FOAF.name, Literal(
            'Univerzita Karlova, Matematicko-fyzikální fakulta', lang='cs')))
        self.__collector.add((self.__czso, RDF.type, PROV.Agent))
        self.__collector.add((self.__czso, RDF.type, PROV.Organization))
        self.__collector.add((self.__czso, FOAF.name, Literal(
            'Český statistický úřad', lang='cs')))

    def __add_activities(self):
        self.__collector.add(
            (self.__county_conversion, RDF.type, PROV.Activity))

        conv_usage = BNode()
        self.__collector.add((conv_usage, RDF.type, PROV.Usage))
        self.__collector.add((conv_usage, PROV.entity, self.__datasrc))
        self.__collector.add((conv_usage, PROV.entity, self.__countysrc))
        self.__collector.add((conv_usage, PROV.hadRole, self.__role_raw_data))
        self.__collector.add(
            (self.__transformation, PROV.qualifiedUsage, conv_usage))

        self.__collector.add((self.__transformation, RDF.type, PROV.Activity))

        trans_usage = BNode()
        self.__collector.add((trans_usage, RDF.type, PROV.Usage))
        self.__collector.add((trans_usage, PROV.entity, self.__preprocessed))
        self.__collector.add((trans_usage, PROV.hadRole, self.__role_raw_data))
        self.__collector.add(
            (self.__transformation, PROV.qualifiedUsage, trans_usage))

    def __add_roles(self):
        self.__collector.add((self.__role_raw_data, RDF.type, PROV.Role))

    def start_county_conversion(self):
        self.__collector.add(
            (self.__county_conversion, PROV.startedAtTime, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))

    def end_county_conversion(self):
        self.__collector.add(
            (self.__county_conversion, PROV.endedAtTime, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))

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
