# SKOS & DCAT-AP assignment

## System requirements

- python 3.10

## Installation instructions

1. `pip install -r requirements.txt`

## Scripts

### population_dataset.py

Creates a DCAT dataset entry for the population data cube.

`usage: population_dataset.py [-o OUT]`

- OUT is output file (default stdout)

### regions_hierarchy.py

Creates a SKOS hierarchy for Czech regions and counties.

`usage: regions_hierarchy.py [-o OUT]`

- OUT is output file (default stdout)
