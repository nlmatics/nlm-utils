import pytest

from nlm_utils.parsers.value_parser import CountParser


@pytest.mark.parametrize(
    "count_str, expected",
    [
        (
            "90,000 shares",
            {
                "formatted_value": "90,000 shares",
                "raw_value": 90000,
            },
        ),
    ],
)
def test_money_parser(count_str, expected):
    count_parser = CountParser()
    assert count_parser.parse(count_str) == expected
