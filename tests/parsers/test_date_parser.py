import pytest

from nlm_utils.parsers.value_parser import DateParser


@pytest.mark.parametrize(
    "date_str, expected",
    [
        (
            "01-01-2022",
            {
                "formatted_value": "01-01-2022",
                "raw_value": 1640995200.0,
            },
        ),
        (
            "2022",
            {
                "formatted_value": "2022",
                "raw_value": 1640995200.0,
            },
        ),
        (
            "15th December",
            {
                "formatted_value": "15th December",
                "raw_value": 1671062400.0,
            },
        ),
        (
            "July 16, 2020",
            {
                "formatted_value": "July 16, 2020",
                "raw_value": 1594857600.0,
            },
        ),
    ],
)
def test_date_parser(date_str, expected):
    date_parser = DateParser()
    assert date_parser.parse(date_str) == expected
