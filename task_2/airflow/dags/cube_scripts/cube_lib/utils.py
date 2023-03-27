def sanitize(value: str):
    return value.replace(',', '_').replace(' ', '_')


region_labels = {
    'CZ064': 'Jihomoravský kraj',
    'CZ010': 'Hlavní město Praha',
    'CZ020': 'Středočeský kraj',
    'CZ080': 'Moravskoslezský kraj',
    'CZ053': 'Pardubický kraj',
    'CZ032': 'Plzeňský kraj',
    'CZ042': 'Ústecký kraj',
    'CZ051': 'Liberecký kraj',
    'CZ052': 'Královéhradecký kraj',
    'CZ031': 'Jihočeský kraj',
    'CZ041': 'Karlovarský kraj',
    'CZ063': 'Kraj Vysočina',
    'CZ072': 'Zlínský kraj',
    'CZ071': 'Olomoucký kraj',
}
