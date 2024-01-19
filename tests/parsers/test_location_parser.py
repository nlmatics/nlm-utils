from nlm_utils.parsers.location_parser import LocationParser


def test_location_parser(location_str, expected):
    location_parser = LocationParser()
    assert location_parser.parse(location_str) == expected
