#!/usr/bin/env python3
import argparse
import sys

from rdflib import Graph, Literal
from rdflib.namespace import SKOS, RDF
from cube_lib.transformations import create_county_conversion_map, load_csv_file_as_object
from cube_lib.namespaces import NS, NSR
from cube_lib.utils import region_labels


def main():
    args = init_args()
    collector = Graph()
    create_hierarchy(collector)
    collector.serialize(format='ttl', encoding='UTF-8', destination=args.out)


def init_args():
    parser = argparse.ArgumentParser(
        description='create counties SKOS hierarchy')
    parser.add_argument(
        '-o', '--out', dest='out', default=sys.stdout.buffer, type=argparse.FileType('wb'),
        help='the file where the hierarchy should be written')
    return parser.parse_args()


def create_hierarchy(collector: Graph):
    county_codes = create_county_conversion_map()
    with open('data/population.csv', 'r', encoding='UTF-8') as file:
        data = load_csv_file_as_object(file)
    data = [{
        'OkresCode': county_codes[row['vuzemi_kod']],
        'Okres': row['vuzemi_txt'],
        'KrajCode': county_codes[row['vuzemi_kod']][:-1],
    } for row in data if row['vuk'] == 'DEM0004' and row['vuzemi_cis'] == '101']

    scheme = NSR.Regions
    collector.add((scheme, RDF.type, SKOS.ConceptScheme))
    for code, label in region_labels.items():
        resource = NSR['region-' + code]
        collector.add((resource, RDF.type, NS.Region))
        collector.add((resource, RDF.type, SKOS.Concept))
        collector.add((resource, SKOS.prefLabel, Literal(label, lang='cs')))
        collector.add((resource, SKOS.notation, Literal(code)))
        collector.add((scheme, SKOS.hasTopConcept, resource))

    for row in data:
        resource = NSR['county-' + row['OkresCode']]
        collector.add((resource, RDF.type, NS.County))
        collector.add((resource, RDF.type, SKOS.Concept))
        collector.add((resource, SKOS.prefLabel,
                      Literal(row['Okres'], lang='cs')))
        collector.add((resource, SKOS.notation, Literal(row['OkresCode'])))
        collector.add((NSR['region-' + row['KrajCode']],
                      SKOS.narrower, resource))


if __name__ == '__main__':
    main()
