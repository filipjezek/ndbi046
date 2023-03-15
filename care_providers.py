#!/usr/bin/env python3
import csv
from datetime import date

from rdflib import Graph, BNode, Literal, Namespace
# See https://rdflib.readthedocs.io/en/latest/_modules/rdflib/namespace.html
from rdflib.namespace import QB, RDF, XSD, SKOS
import itertools as it

NS = Namespace('https://filipjezek.github.io/ontology#')
NSR = Namespace('https://filipjezek.github.io/resources/')
# We use custom Namespace here as the generated is limited in content
# https://rdflib.readthedocs.io/en/stable/_modules/rdflib/namespace/_RDFS.html
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
SDMX_DIM = Namespace('http://purl.org/linked-data/sdmx/2009/dimension#')
SDMX_CON = Namespace('http://purl.org/linked-data/sdmx/2009/concept#')
SDMX_MEA = Namespace('http://purl.org/linked-data/sdmx/2009/measure#')

DCT = Namespace('http://purl.org/dc/terms/')


def main():
    data_as_csv = load_csv_file_as_object('care_providers.csv')
    data_cube = as_data_cube(data_as_csv)
    print(data_cube.serialize(format='ttl'))


def load_csv_file_as_object(file):
    result = []
    with open(file, 'r', encoding='UTF-8    ') as stream:
        reader = csv.reader(stream)
        header = next(reader)
        for line in reader:
            result.append({key: value for key, value in zip(header, line)})
    return result


def as_data_cube(data):
    result = Graph()
    create_resources(result, data)
    dimensions = create_dimensions(result)
    measures = create_measure(result)
    structure = create_structure(result, dimensions, measures)
    dataset = create_dataset(result, structure)
    create_observations(result, dataset, data)
    return result


def sanitize(value: str):
    return value.replace(',', '_').replace(' ', '_')


def create_resources(collector: Graph, data):
    County = NS.County
    collector.add((County, RDF.type, RDFS.Class))
    collector.add((County, SKOS.prefLabel, Literal('Okres', lang='cs')))
    collector.add((County, SKOS.prefLabel, Literal('County', lang='en')))
    collector.add((County, QB.concept, SDMX_CON.refArea))

    for code, label in set(map(lambda row: (row['OkresCode'], row['Okres']), data)):
        collector.add((NSR[code], RDF.type, County))
        collector.add((NSR[code], SKOS.prefLabel, Literal(label, lang='cs')))

    Region = NS.Region
    collector.add((Region, RDF.type, RDFS.Class))
    collector.add((Region, SKOS.prefLabel, Literal('Kraj', lang='cs')))
    collector.add((Region, SKOS.prefLabel, Literal('Region', lang='en')))
    collector.add((Region, QB.concept, SDMX_CON.refArea))

    for code, label in set(map(lambda row: (row['KrajCode'], row['Kraj']), data)):
        collector.add((NSR[code], RDF.type, Region))
        collector.add((NSR[code], SKOS.prefLabel, Literal(label, lang='cs')))

    FieldOfCare = NS.FieldOfCare
    collector.add((FieldOfCare, RDF.type, RDFS.Class))
    collector.add((FieldOfCare, SKOS.prefLabel,
                  Literal('Obor péče', lang='cs')))
    collector.add((FieldOfCare, SKOS.prefLabel,
                  Literal('Field of care', lang='en')))
    collector.add((FieldOfCare, QB.concept, SDMX_CON.coverageSector))

    for label in set(map(lambda row: row['OborPece'], data)):
        sanitized = sanitize(label)
        collector.add((NSR[sanitized], RDF.type, FieldOfCare))
        collector.add((NSR[sanitized], SKOS.prefLabel,
                      Literal(label, lang='cs')))


def create_dimensions(collector: Graph):
    county = NS.county
    collector.add((county, RDF.type, RDFS.Property))
    collector.add((county, RDF.type, QB.DimensionProperty))
    collector.add((county, RDFS.subPropertyOf, SDMX_DIM.refArea))
    collector.add((county, QB.concept, SDMX_CON.refArea))
    collector.add((county, RDFS.label, Literal('Okres', lang='cs')))
    collector.add((county, RDFS.label, Literal('County', lang='en')))
    collector.add((county, RDFS.range, NS.County))

    region = NS.region
    collector.add((region, RDF.type, RDFS.Property))
    collector.add((region, RDF.type, QB.DimensionProperty))
    collector.add((region, RDFS.subPropertyOf, SDMX_DIM.refArea))
    collector.add((region, QB.concept, SDMX_CON.refArea))
    collector.add((region, RDFS.label, Literal('Kraj', lang='cs')))
    collector.add((region, RDFS.label, Literal('Region', lang='en')))
    collector.add((region, RDFS.range, NS.Region))

    field_of_care = NS.fieldOfCare
    collector.add((field_of_care, RDF.type, RDFS.Property))
    collector.add((field_of_care, RDF.type, QB.DimensionProperty))
    collector.add((region, RDFS.subPropertyOf, SDMX_DIM.coverageSector))
    collector.add((region, QB.concept, SDMX_CON.coverageSector))
    collector.add((field_of_care, RDFS.label, Literal('Obor péče', lang='cs')))
    collector.add((field_of_care, RDFS.label,
                  Literal('Field of care', lang='en')))
    collector.add((field_of_care, RDFS.range, NS.FieldOfCare))

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


def create_structure(collector: Graph, dimensions, measures):

    structure = NS.structure
    collector.add((structure, RDF.type, QB.DataStructureDefinition))

    for dimension in dimensions:
        component = BNode()
        collector.add((structure, QB.component, component))
        collector.add((component, QB.dimension, dimension))

    for measure in measures:
        component = BNode()
        collector.add((structure, QB.component, component))
        collector.add((component, QB.measure, measure))

    return structure


def create_dataset(collector: Graph, structure):

    now = date.today().strftime('%Y-%m-%d')

    dataset = NSR.dataCubeInstance
    collector.add((dataset, RDF.type, QB.DataSet))
    collector.add((dataset, DCT.issued, Literal(now, datatype=XSD.date)))
    collector.add((dataset, DCT.modified, Literal(now, datatype=XSD.date)))
    collector.add((dataset, DCT.publisher, Literal(
        'https://github.com/filipjezek')))
    collector.add((dataset, DCT.license, Literal(
        'https://opensource.org/license/MIT/')))
    collector.add((dataset, RDFS.label, Literal(
        'Care providers', lang='en')))
    collector.add((dataset, RDFS.label, Literal(
        'Poskytovatelé zdravotní péče', lang='cs')))
    collector.add((dataset, QB.structure, structure))

    return dataset


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

    collector.add((resource, NS.county, NSR[data['county']]))
    collector.add((resource, NS.region, NSR[data['region']]))
    collector.add((resource, NS.fieldOfCare, NSR[sanitize(data['field'])]))
    collector.add((resource, NS.careProvidersCount, Literal(
        data['count'], datatype=XSD.integer)))


if __name__ == '__main__':
    main()
