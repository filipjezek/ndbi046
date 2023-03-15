def sanitize(value: str):
    return value.replace(',', '_').replace(' ', '_')
