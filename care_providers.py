#!/usr/bin/env python3
import csv


from rdflib import Graph, BNode, Literal, Namespace
# See https://rdflib.readthedocs.io/en/latest/_modules/rdflib/namespace.html
from rdflib.namespace import QB, RDF, XSD

NS = Namespace("https://skodapetr.github.io/ontology#")
NSR = Namespace("https://skodapetr.github.io/resources/")
# We use custom Namespace here as the generated is limited in content
# https://rdflib.readthedocs.io/en/stable/_modules/rdflib/namespace/_RDFS.html
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")


def main():
    data_as_csv = load_csv_file_as_object("care_providers.csv")
    data_cube = as_data_cube(data_as_csv)
    print(data_cube.serialize(format="ttl"))


def load_csv_file_as_object(file):
    result = []
    with open(file, "r") as stream:
        reader = csv.reader(stream)
        header = next(reader)
        for line in reader:
            result.append({key: value for key, value in zip(header, line)})
    return result


def as_data_cube(data):
    result = Graph()
    dimensions = create_dimensions(result)
    measures = create_measure(result)
    structure = create_structure(result, dimensions, measures)
    dataset = create_dataset(result, structure)
    create_observations(result, dataset, data)
    return result


def create_dimensions(collector: Graph):
    county = NS.county
    collector.add((county, RDF.type, RDFS.Property))
    collector.add((county, RDF.type, QB.DimensionProperty))
    collector.add((county, RDFS.label, Literal("Okres", lang="cs")))
    collector.add((county, RDFS.label, Literal("County", lang="en")))
    collector.add((county, RDFS.range, XSD.string))

    region = NS.region
    collector.add((region, RDF.type, RDFS.Property))
    collector.add((region, RDF.type, QB.DimensionProperty))
    collector.add((region, RDFS.label, Literal("Kraj", lang="cs")))
    collector.add((region, RDFS.label, Literal("Region", lang="en")))
    collector.add((region, RDFS.range, XSD.string))

    field_of_care = NS.fieldOfCare
    collector.add((field_of_care, RDF.type, RDFS.Property))
    collector.add((field_of_care, RDF.type, QB.DimensionProperty))
    collector.add((field_of_care, RDFS.label, Literal("Obor péče", lang="cs")))
    collector.add((field_of_care, RDFS.label,
                  Literal("Field of care", lang="en")))
    collector.add((field_of_care, RDFS.range, XSD.string))

    return [county, region, field_of_care]


def create_measure(collector: Graph):

    care_providers_count = NS.careProvidersCount
    collector.add((care_providers_count, RDF.type, RDFS.Property))
    collector.add((care_providers_count, RDF.type, QB.MeasureProperty))
    collector.add((care_providers_count, RDFS.label,
                  Literal("Počet poskytovatelů péče", lang="cs")))
    collector.add((care_providers_count, RDFS.label,
                  Literal("Care providers count", lang="en")))
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

    dataset = NSR.dataCubeInstance
    collector.add((dataset, RDF.type, QB.DataSet))
    collector.add((dataset, RDFS.label, Literal(
        "Points per seminar", lang="en")))
    collector.add((dataset, QB.structure, structure))

    return dataset


def create_observations(collector: Graph, dataset, data):
    for index, row in enumerate(data):
        resource = NSR["observation-" + str(index).zfill(3)]
        create_observation(collector, dataset, resource, row)


def create_observation(collector: Graph, dataset, resource, data):
    collector.add((resource, RDF.type, QB.Observation))
    collector.add((resource, QB.dataSet, dataset))
    collector.add((resource, NS.date, Literal(
        convert_date(data["Date"]), datatype=XSD.date)))
    collector.add((resource, NS.room, Literal(data["Room"])))
    collector.add((resource, NS.subject, Literal(data["Subject"])))
    collector.add((resource, NS.points, Literal(
        data["Points"], datatype=XSD.integer)))


def convert_date(value):
    return value.replace(".", "-")


if __name__ == "__main__":
    main()
