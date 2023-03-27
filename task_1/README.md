# Data cube assignment

## System requirements

- python 3.10

## Installation instructions

1. `pip install -r requirements.txt`

## Scripts

### population.py

Creates the population data cube. Example data (as well as schema) is in the `data` folder.

`usage: population.py [-o OUT] src`

- OUT is output file (default stdout)
- src is input file (must conform to the schema in `data/population.csv.schema.json`)
- the script also provides `create_cube(src: TextIOWrapper) -> Graph` function to get access to the data cube programmatically

### care_providers.py

Creates the care providers data cube. Example data (as well as schema) is in the `data` folder.

`usage: care_providers.py [-o OUT] src`

- OUT is output file (default stdout)
- src is input file (must conform to the schema in `data/care_providers.csv.schema.json`)
- the script also provides `create_cube(src: TextIOWrapper) -> Graph` function to get access to the data cube programmatically

### integrity.py

Runs integrity checks on both generated data cubes and reports results into stdout
