#!/usr/bin/env python3
import argparse
import sys
from io import TextIOWrapper

from rdflib import Graph, Literal
# See https://rdflib.readthedocs.io/en/latest/_modules/rdflib/namespace.html
from rdflib.namespace import QB, RDF, XSD

from .cube_lib.namespaces import NS, NSR, RDFS, SDMX_MEA
from .cube_lib import resources, utils, dimensions
from .cube_lib.transformations import load_csv_file_as_object, create_county_conversion_map
from .cube_lib.dataset import create_dataset, create_structure


def main():
    args = init_args()
    data_cube = create_cube(args.src, args.counties)
    data_cube.serialize(format='ttl', encoding='UTF-8', destination=args.out)


def create_cube(src: TextIOWrapper, counties_path: str) -> Graph:
    data_as_csv = load_csv_file_as_object(src)
    data_as_csv = preprocess_data(data_as_csv, counties_path)
    return as_data_cube(data_as_csv)


def init_args():
    parser = argparse.ArgumentParser(
        description='create population data cube')
    parser.add_argument(
        'src', type=argparse.FileType('r', encoding='UTF-8'),
        help='data source file')
    parser.add_argument(
        'counties', type=str,
        help='county codes file')
    parser.add_argument(
        '-o', '--out', dest='out', default=sys.stdout, type=argparse.FileType('wb'),
        help='the file where the data cube should be written')
    return parser.parse_args()


def preprocess_data(data, counties_path: str):
    county_codes = create_county_conversion_map(counties_path)
    mapped = (
        {
            'OkresCode': county_codes[row['vuzemi_kod']],
            'Okres': row['vuzemi_txt'],
            'KrajCode': county_codes[row['vuzemi_kod']][:-1],
            'Kraj': utils.region_labels[county_codes[row['vuzemi_kod']][:-1]],
            'Mean': int(row['hodnota'])
        } for row in data if row['vuk'] == 'DEM0004' and row['vuzemi_cis'] == '101'
    )
    return list(mapped)


def as_data_cube(data):
    result = Graph()
    create_resources(result, data)
    dimensions = create_dimensions(result)
    measures = create_measure(result)
    structure = create_structure(result, dimensions, measures)
    dataset = create_dataset(result, structure, {
                             'cs': 'Obyvatelé okresy', 'en': 'Population'})
    create_observations(result, dataset, data)
    return result


def create_resources(collector: Graph, data):
    resources.create_county(collector, data)
    resources.create_region(collector, data)


def create_dimensions(collector: Graph):
    county = dimensions.create_county(collector)
    region = dimensions.create_region(collector)

    return [county, region]


def create_measure(collector: Graph):

    mean_population = NS.meanPopulation
    collector.add((mean_population, RDF.type, RDFS.Property))
    collector.add((mean_population, RDF.type, QB.MeasureProperty))
    collector.add(
        (mean_population, RDFS.subPropertyOf, SDMX_MEA.obsValue))
    collector.add((mean_population, RDFS.label,
                  Literal('Střední stav obyvatel', lang='cs')))
    collector.add((mean_population, RDFS.label,
                  Literal('Mean population', lang='en')))
    collector.add((mean_population, RDFS.range, XSD.integer))

    return [mean_population]


def sort_by_dimensions(row):
    return row['OkresCode'], row['KrajCode']


def create_observations(collector: Graph, dataset, data):
    for index, row in enumerate(data):
        resource = NSR['observation-' + str(index).zfill(5)]
        create_observation(collector, dataset, resource, row)


def create_observation(collector: Graph, dataset, resource, data):
    collector.add((resource, RDF.type, QB.Observation))
    collector.add((resource, QB.dataSet, dataset))

    collector.add((resource, NS.county, NSR['county-' + data['OkresCode']]))
    collector.add((resource, NS.region, NSR['region-' + data['KrajCode']]))
    collector.add((resource, NS.meanPopulation, Literal(
        data['Mean'], datatype=XSD.integer)))


if __name__ == '__main__':
    main()
