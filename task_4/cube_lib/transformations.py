#!/usr/bin/env python3
import csv


def load_csv_file_as_object(file):
    result = []
    reader = csv.reader(file)
    header = next(reader)
    for line in reader:
        result.append({key: value for key, value in zip(header, line)})
    return result


def create_county_conversion_map():
    result = {}
    with open('data/counties.csv', 'r', encoding='UTF-8') as stream:
        reader = csv.reader(stream)
        header = next(reader)
        for line in reader:
            obj = ({key: value for key, value in zip(header, line)})
            result[obj['CHODNOTA2']] = obj['CHODNOTA1']
        return result
