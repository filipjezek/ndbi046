# PROV assignment

## System requirements

- python 3.10

## Installation instructions

1. `pip install -r requirements.txt`

## Scripts

### population_provenance.py

Creates a provenance record for the population data cube. The script assumes that the original data came from mhcz.
The activity dates will be set to now.

`usage: population_provenance.py [-o OUT]`

- OUT is output file (default stdout)
- Also exposes `PopulationProv` class with methods `start_county_conversion`, `end_county_conversion`, `start_transformation`, `end_transformation`
  to set correct dates. The finished prov RDF can be exported using `save_to` method.

#### Example

```python
prov = PopulationProv()
prov.start_county_conversion()
# do conversion stuff
prov.end_county_conversion()
prov.start_transformation()
# do transformation stuff
prov.end_transformation()
prov.save_to(...)
```

### care_providers_provenance.py

Creates a provenance record for the care providers data cube. The script assumes that the original data came from czso.
The activity dates will be set to now.

`usage: care_providers_provenance.py [-o OUT]`

- OUT is output file (default stdout)
- Also exposes `CareProvidersProv` class with methods `start_transformation`, `end_transformation`
  to set correct dates. The finished prov RDF can be exported using `save_to` method.

#### Example

```python
prov = CareProvidersProv()
prov.start_transformation()
# do transformation stuff
prov.end_transformation()
prov.save_to(...)
```
