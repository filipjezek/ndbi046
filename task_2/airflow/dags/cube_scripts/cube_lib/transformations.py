#!/usr/bin/env python3
import csv
from io import TextIOWrapper


def load_csv_file_as_object(file: TextIOWrapper):
    result = []
    reader = csv.reader(file)
    header = next(reader)
    for line in reader:
        result.append({key: value for key, value in zip(header, line)})
    return result


def create_county_conversion_map(path: str):
    result = {}
    with open(path, 'r', encoding='UTF-8') as stream:
        reader = csv.reader(stream)
        header = next(reader)
        for line in reader:
            obj = ({key: value for key, value in zip(header, line)})
            result[obj['CHODNOTA2']] = obj['CHODNOTA1']
        return result
