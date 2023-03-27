#!/usr/bin/env python3
from rdflib import Graph, Literal
from .namespaces import NSR, RDFS
from rdflib.namespace import RDF, SKOS, OWL
from .utils import sanitize


def create_resource(collector: Graph, data, dataKey: str, labelsScheme, labelsClass, name: str, coded: bool):
    scheme = NSR[name]

    collector.add((scheme, RDF.type, SKOS.ConceptScheme))

    for lang in labelsScheme:
        collector.add(
            (scheme, SKOS.prefLabel, Literal(labelsScheme[lang], lang=lang)))
        collector.add((scheme, RDFS.label, Literal(
            labelsScheme[lang], lang=lang)))

    _class = NSR[name.capitalize()]
    collector.add((_class, RDF.type, RDFS.Class))
    collector.add((_class, RDF.type, OWL.Class))
    collector.add((_class, RDFS.subClassOf, SKOS.Concept))

    for lang in labelsClass:
        collector.add(
            (_class, SKOS.prefLabel, Literal(labelsClass[lang], lang=lang)))
        collector.add((_class, RDFS.label, Literal(
            labelsClass[lang], lang=lang)))

    if coded:
        for code, label in set(map(lambda row: (row[f'{dataKey}Code'], row[dataKey]), data)):
            normalized = f'{name}-{code}'
            collector.add((NSR[normalized], RDF.type, _class))
            collector.add((NSR[normalized], RDF.type, SKOS.Concept))
            collector.add((NSR[normalized], SKOS.notation, Literal(code)))
            collector.add((NSR[normalized], SKOS.prefLabel,
                           Literal(label, lang='cs')))
            collector.add((NSR[normalized], RDFS.label,
                          Literal(label, lang='cs')))
            collector.add((NSR[normalized], SKOS.inScheme, scheme))
            collector.add((NSR[normalized], SKOS.topConceptOf, scheme))
            collector.add((scheme, SKOS.hasTopConcept, NSR[normalized]))
    else:
        for label in set(map(lambda row: row[dataKey], data)):
            normalized = f'{name}-{sanitize(label)}'
            collector.add((NSR[normalized], RDF.type, _class))
            collector.add((NSR[normalized], RDF.type, SKOS.Concept))
            collector.add((NSR[normalized], SKOS.prefLabel,
                           Literal(label, lang='cs')))
            collector.add((NSR[normalized], RDFS.label,
                          Literal(label, lang='cs')))
            collector.add((NSR[normalized], SKOS.inScheme, scheme))
            collector.add((NSR[normalized], SKOS.topConceptOf, scheme))
            collector.add((scheme, SKOS.hasTopConcept, NSR[normalized]))


def create_county(collector: Graph, data):
    return create_resource(collector, data, 'Okres', {
        'cs': 'Číselník okresů - schéma',
        'en': 'Code list for counties - scheme',
    }, {
        'cs': 'Číselník okresů - třída',
        'en': 'Code list for counties - class',
    }, 'county', True)


def create_region(collector: Graph, data):
    return create_resource(collector, data, 'Kraj', {
        'cs': 'Číselník krajů - schéma',
        'en': 'Code list for regions - scheme',
    }, {
        'cs': 'Číselník krajů - třída',
        'en': 'Code list for regions - class',
    }, 'region', True)


def create_field_of_care(collector: Graph, data):
    return create_resource(collector, data, 'OborPece', {
        'cs': 'Seznam oborů péče - schéma',
        'en': 'Code list for fields of care - scheme',
    }, {
        'cs': 'Seznam oborů péče - třída',
        'en': 'Code list for fields of care - class',
    }, 'fieldOfCare', False)
