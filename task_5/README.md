# SKOS & DCAT-AP assignment

## System requirements

- python 3.10

## Installation instructions

1. `pip install -r requirements.txt`

## Scripts

### population_dataset.py

Creates a DCAT dataset entry for the population data cube.

`usage: population_dataset.py [-o OUT] src`

- OUT is output file (default stdout)
- src is input file (the ttl data cube for which we want to create the DCAT entry)
