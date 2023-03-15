#!/usr/bin/env python3
from datetime import date
from rdflib import Graph, Literal, BNode
from rdflib.namespace import QB, RDF, XSD
from .namespaces import NSR, DCT, RDFS, NS


def create_dataset(collector: Graph, structure, labels):
    now = date.today().strftime('%Y-%m-%d')

    dataset = NSR.dataCubeInstance
    collector.add((dataset, RDF.type, QB.DataSet))
    collector.add((dataset, DCT.issued, Literal(now, datatype=XSD.date)))
    collector.add((dataset, DCT.modified, Literal(now, datatype=XSD.date)))
    collector.add((dataset, DCT.publisher, Literal(
        'https://github.com/filipjezek')))
    collector.add((dataset, DCT.license, Literal(
        'https://opensource.org/license/MIT/')))

    for lang in labels:
        collector.add((dataset, RDFS.label, Literal(labels[lang], lang=lang)))

    collector.add((dataset, QB.structure, structure))

    return dataset


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
