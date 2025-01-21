COUNTRY_UNITS_MAP = {
    "US": "imperial",
    "UK": "imperial",
    "CA": "imperial",
    "AU": "metric",
    "IN": "metric",
    "FR": "metric",
    "DE": "metric",
    # Add more countries as needed
}

def get_units_for_country(country: str) -> str:
    return COUNTRY_UNITS_MAP.get(country.upper(), "metric")  # Default to metric
