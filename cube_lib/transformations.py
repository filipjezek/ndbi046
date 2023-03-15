#!/usr/bin/env python3
import csv


def load_csv_file_as_object(file):
    result = []
    reader = csv.reader(file)
    header = next(reader)
    for line in reader:
        result.append({key: value for key, value in zip(header, line)})
    return result
