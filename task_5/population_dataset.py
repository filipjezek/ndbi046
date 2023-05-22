#!/usr/bin/env python3
import argparse
import sys
from io import TextIOWrapper
from hashlib import sha1

from rdflib import Graph, Literal, URIRef, BNode
from rdflib.namespace import DCAT, RDF, DCTERMS, RDFS, XSD
from cube_lib.namespaces import NSR, SPDX


def main():
    args = init_args()
    collector = Graph()
    create_dataset_entry(collector, args.src)
    collector.serialize(format='ttl', encoding='UTF-8', destination=args.out)


def init_args():
    parser = argparse.ArgumentParser(
        description='create population DCAT dataset entry')
    parser.add_argument(
        'src', type=argparse.FileType('rb'),
        help='data cube file')
    parser.add_argument(
        '-o', '--out', dest='out', default=sys.stdout.buffer, type=argparse.FileType('wb'),
        help='the file where the dataset entry should be written')
    return parser.parse_args()


def create_dataset_entry(collector: Graph, cube_file: TextIOWrapper):
    collector.add((NSR.PopulationDataCube, RDF.type, DCAT.Dataset))
    collector.add((NSR.PopulationDataCube, DCTERMS.title,
                  Literal('Population data cube', lang='en')))
    collector.add((NSR.PopulationDataCube, RDFS.label,
                  Literal('Population data cube', lang='en')))
    collector.add((NSR.PopulationDataCube, DCTERMS.description, Literal(
        'A data cube containing mean population of Czech counties and regions in 2021', lang='en')))
    collector.add((NSR.PopulationDataCube, DCTERMS.spatial, URIRef(
        'http://publications.europa.eu/resource/authority/country/CZE')))
    collector.add((NSR.PopulationDataCube, DCTERMS.accrualPeriodicity, URIRef(
        'http://publications.europa.eu/resource/authority/frequency/NEVER')))
    me = URIRef('https://github.com/filipjezek')
    collector.add((NSR.PopulationDataCube, DCTERMS.publisher, me))
    collector.add((NSR.PopulationDataCube, DCTERMS.creator, me))
    collector.add((NSR.PopulationDataCube, DCAT.keyword,
                  Literal('population', lang='en')))
    collector.add((NSR.PopulationDataCube, DCAT.keyword,
                  Literal('region', lang='en')))
    collector.add((NSR.PopulationDataCube, DCAT.keyword,
                  Literal('district', lang='en')))
    collector.add((NSR.PopulationDataCube, DCAT.theme,
                  URIRef('http://eurovoc.europa.eu/2908')))

    distribution = NSR['data-catalog.ttl']
    collector.add((NSR.PopulationDataCube, DCAT.distribution, distribution))
    collector.add((distribution, RDF.type, DCAT.Distribution))
    collector.add((distribution, DCAT.accessURL, distribution))
    collector.add((distribution, DCTERMS.format, URIRef(
        'http://publications.europa.eu/resource/authority/file-type/RDF_TURTLE')))
    collector.add((distribution, DCAT.mediaType, URIRef(
        'http://www.iana.org/assignments/media-types/text/turtle')))

    checksum_node = BNode()
    checksum = sha1(cube_file.read()).hexdigest()
    collector.add((distribution, SPDX.checksum, checksum_node))
    collector.add((checksum_node, RDF.type, SPDX.Checksum))
    collector.add((checksum_node, SPDX.algorithm, SPDX.checksumAlgorithm_sha1))
    collector.add((checksum_node, SPDX.checksumValue,
                  Literal(checksum, datatype=XSD.hexBinary)))


if __name__ == '__main__':
    main()
