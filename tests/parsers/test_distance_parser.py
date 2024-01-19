from nlm_utils.parsers.value_parser import DistanceParser


def test_money_parser(money_str, expected):
    distance_parser = DistanceParser()
    assert distance_parser.parse(money_str) == expected
