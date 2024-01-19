import pytest

from nlm_utils.parsers.value_parser import PercentParser


@pytest.mark.parametrize(
    "percent_str, expected",
    [
        (
            "90.2%",
            {
                "formatted_value": "90.2%",
                "raw_value": 90.2,
                "percent_label": "%",
            },
        ),
        (
            "90.2 percent",
            {
                "formatted_value": "90.2 percent",
                "raw_value": 90.2,
                "percent_label": "%",
            },
        ),
        (
            "90.2 bps",
            {
                "formatted_value": "90.2 bps",
                "raw_value": 90.2,
                "percent_label": "bps",
            },
        ),
        (
            "90.2 basis points",
            {
                "formatted_value": "90.2 basis points",
                "raw_value": 90.2,
                "percent_label": "bps",
            },
        ),
    ],
)
def test_money_parser(percent_str, expected):
    count_parser = PercentParser()
    assert count_parser.parse(percent_str) == expected
