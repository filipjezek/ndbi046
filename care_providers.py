#!/usr/bin/env python3
import itertools as it
import argparse
import sys

from rdflib import Graph, Literal
# See https://rdflib.readthedocs.io/en/latest/_modules/rdflib/namespace.html
from rdflib.namespace import QB, RDF, XSD

from cube_lib.namespaces import NS, NSR, RDFS, SDMX_MEA
from cube_lib import resources, utils, dimensions
from cube_lib.transformations import load_csv_file_as_object
from cube_lib.dataset import create_dataset, create_structure


def main():
    args = init_args()
    data_as_csv = load_csv_file_as_object(args.src)
    data_cube = as_data_cube(data_as_csv)
    data_cube.serialize(format='ttl', encoding='UTF-8', destination=args.out)


def init_args():
    parser = argparse.ArgumentParser(
        description='create care providers data cube')
    parser.add_argument(
        'src', type=argparse.FileType('r', encoding='UTF-8'),
        help='data source file')
    parser.add_argument(
        '-o', '--out', dest='out', default=sys.stdout, type=argparse.FileType('wb'),
        help='the file where the data cube should be written')
    return parser.parse_args()


def as_data_cube(data):
    result = Graph()
    create_resources(result, data)
    dimensions = create_dimensions(result)
    measures = create_measure(result)
    structure = create_structure(result, dimensions, measures)
    dataset = create_dataset(result, structure, {
                             'cs': 'Poskytovatelé zdravotní péče', 'en': 'Care providers'})
    create_observations(result, dataset, data)
    return result


def create_resources(collector: Graph, data):
    resources.create_county(collector, data)
    resources.create_region(collector, data)
    resources.create_field_of_care(collector, data)


def create_dimensions(collector: Graph):
    county = dimensions.create_county(collector)
    region = dimensions.create_region(collector)
    field_of_care = dimensions.create_field_of_care(collector, region)

    return [county, region, field_of_care]


def create_measure(collector: Graph):

    care_providers_count = NS.careProvidersCount
    collector.add((care_providers_count, RDF.type, RDFS.Property))
    collector.add((care_providers_count, RDF.type, QB.MeasureProperty))
    collector.add(
        (care_providers_count, RDFS.subPropertyOf, SDMX_MEA.obsValue))
    collector.add((care_providers_count, RDFS.label,
                  Literal('Počet poskytovatelů péče', lang='cs')))
    collector.add((care_providers_count, RDFS.label,
                  Literal('Care providers count', lang='en')))
    collector.add((care_providers_count, RDFS.range, XSD.integer))

    return [care_providers_count]


def sort_by_dimensions(row):
    return row['OkresCode'], row['KrajCode'], row['OborPece']


def create_observations(collector: Graph, dataset, data):
    groups = sorted(data, key=sort_by_dimensions)
    groups = it.groupby(groups)
    for index, grouped in enumerate(groups):
        resource = NSR['observation-' + str(index).zfill(5)]
        create_observation(collector, dataset, resource, {
            'county': grouped[0]['OkresCode'],
            'region': grouped[0]['KrajCode'],
            'field': grouped[0]['OborPece'],
            'count': len(tuple(grouped[1])),
        })


def create_observation(collector: Graph, dataset, resource, data):
    collector.add((resource, RDF.type, QB.Observation))
    collector.add((resource, QB.dataSet, dataset))

    collector.add((resource, NS.county, NSR['county-' + data['county']]))
    collector.add((resource, NS.region, NSR['region-' + data['region']]))
    collector.add((resource, NS.fieldOfCare,
                  NSR['fieldOfCare-' + utils.sanitize(data['field'])]))
    collector.add((resource, NS.careProvidersCount, Literal(
        data['count'], datatype=XSD.integer)))


if __name__ == '__main__':
    main()
