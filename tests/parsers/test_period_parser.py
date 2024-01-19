import pytest

from nlm_utils.parsers.value_parser import PeriodParser


@pytest.mark.parametrize(
    "period_str, expected",
    [
        (
            "90 days",
            {
                "formatted_value": "90 days",
                "raw_value": 90 * 24 * 60 * 60 * 1000,
                "time_value": 90,
                "time_unit": "day",
            },
        ),
        (
            "one (1) year",
            {
                "formatted_value": "one (1) year",
                "raw_value": 365 * 24 * 60 * 60 * 1000,
                "time_value": 1,
                "time_unit": "year",
            },
        ),
        (
            "one year",
            {
                "formatted_value": "one year",
                "raw_value": 365 * 24 * 60 * 60 * 1000,
                "time_value": 1,
                "time_unit": "year",
            },
        ),
        (
            "ten years",
            {
                "formatted_value": "ten years",
                "raw_value": 10 * 365 * 24 * 60 * 60 * 1000,
                "time_value": 10,
                "time_unit": "year",
            },
        ),
        (
            "four (4) -year period",
            {
                "formatted_value": "four (4) -year period",
                "raw_value": 4 * 365 * 24 * 60 * 60 * 1000,
                "time_value": 4,
                "time_unit": "year",
            },
        ),
        (
            "three (3) years",
            {
                "formatted_value": "three (3) years",
                "raw_value": 3 * 365 * 24 * 60 * 60 * 1000,
                "time_value": 3,
                "time_unit": "year",
            },
        ),
        (
            "36 months",
            {
                "formatted_value": "36 months",
                "raw_value": 3 * 365 * 24 * 60 * 60 * 1000,
                "time_value": 36.0,
                "time_unit": "month",
            },
        ),
    ],
)
def test_money_parser(period_str, expected):
    period_parser = PeriodParser()
    assert period_parser.parse(period_str) == expected
