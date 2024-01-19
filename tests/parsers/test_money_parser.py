import pytest

from nlm_utils.parsers.value_parser import MoneyParser


@pytest.mark.parametrize(
    "money_str, expected",
    [
        (
            ".3",
            {
                "formatted_value": "0.30",
                "raw_value": 0.3,
                "currency_symbol": None,
                "unit": None,
            },
        ),
        (
            "1",
            {
                "formatted_value": "1.00",
                "raw_value": 1.0,
                "currency_symbol": None,
                "unit": None,
            },
        ),
        (
            "1.3",
            {
                "formatted_value": "1.30",
                "raw_value": 1.3,
                "currency_symbol": None,
                "unit": None,
            },
        ),
        (
            "43,324",
            {
                "formatted_value": "43,324.00",
                "raw_value": 43324.0,
                "currency_symbol": None,
                "unit": None,
            },
        ),
        (
            "3,424",
            {
                "formatted_value": "3,424.00",
                "raw_value": 3424.0,
                "currency_symbol": None,
                "unit": None,
            },
        ),
        (
            "-0.00",
            {
                "formatted_value": "-0.00",
                "raw_value": 0.0,
                "currency_symbol": None,
                "unit": None,
            },
        ),
        (
            "3 1/4",
            {
                "formatted_value": "3.25",
                "raw_value": 3.25,
                "currency_symbol": None,
                "unit": None,
            },
        ),
        (
            "EUR433,432.53",
            {
                "formatted_value": "€433,432.53",
                "raw_value": 433432.53,
                "currency_symbol": "EUR",
                "unit": "EUR",
            },
        ),
        (
            "25.675,26 EUR",
            {
                "formatted_value": "€25.68",
                "raw_value": 25.67526,
                "currency_symbol": "EUR",
                "unit": "EUR",
            },
        ),
        (
            "2.447,93 EUR",
            {
                "formatted_value": "€2.45",
                "raw_value": 2.44793,
                "currency_symbol": "EUR",
                "unit": "EUR",
            },
        ),
        (
            "-540,89EUR",
            {
                "formatted_value": "-€54,089.00",
                "raw_value": -54089.0,
                "currency_symbol": "EUR",
                "unit": "EUR",
            },
        ),
        (
            "67.60 EUR",
            {
                "formatted_value": "€67.60",
                "raw_value": 67.6,
                "currency_symbol": "EUR",
                "unit": "EUR",
            },
        ),
        (
            "30.998,63 CHF",
            {
                "formatted_value": "CHF31.00",
                "raw_value": 30.99863,
                "currency_symbol": "CHF",
                "unit": "CHF",
            },
        ),
        (
            "0,00 CHF",
            {
                "formatted_value": "CHF0.00",
                "raw_value": 0.0,
                "currency_symbol": "CHF",
                "unit": "CHF",
            },
        ),
        (
            "159.750,00 DKK",
            {
                "formatted_value": "DKK159.75",
                "raw_value": 159.75,
                "currency_symbol": "DKK",
                "unit": "DKK",
            },
        ),
        (
            "£ 2.237,85",
            {
                "formatted_value": "£2.24",
                "raw_value": 2.23785,
                "currency_symbol": "£",
                "unit": "GBP",
            },
        ),
        (
            "£ 2,237.85",
            {
                "formatted_value": "£2,237.85",
                "raw_value": 2237.85,
                "currency_symbol": "£",
                "unit": "GBP",
            },
        ),
        (
            "-1.876,85 SEK",
            {
                "formatted_value": "-SEK1.88",
                "raw_value": -1.87685,
                "currency_symbol": "SEK",
                "unit": "SEK",
            },
        ),
        (
            "59294325.3",
            {
                "formatted_value": "59,294,325.30",
                "raw_value": 59294325.3,
                "currency_symbol": None,
                "unit": None,
            },
        ),
        (
            "8,53 NOK",
            {
                "formatted_value": "NOK853.00",
                "raw_value": 853.0,
                "currency_symbol": "NOK",
                "unit": "NOK",
            },
        ),
        (
            "0,09 NOK",
            {
                "formatted_value": "NOK9.00",
                "raw_value": 9.0,
                "currency_symbol": "NOK",
                "unit": "NOK",
            },
        ),
        (
            "-.9 CZK",
            {
                "formatted_value": "-CZK0.90",
                "raw_value": -0.9,
                "currency_symbol": "CZK",
                "unit": "CZK",
            },
        ),
        (
            "35.255,40 PLN",
            {
                "formatted_value": "PLN35.26",
                "raw_value": 35.2554,
                "currency_symbol": "PLN",
                "unit": "PLN",
            },
        ),
        (
            "-PLN123.456,78",
            {
                "formatted_value": "-PLN123.46",
                "raw_value": -123.45678,
                "currency_symbol": "PLN",
                "unit": "PLN",
            },
        ),
        (
            "US$123.456,79",
            {
                "formatted_value": "$123.46",
                "raw_value": 123.45679,
                "currency_symbol": "US$",
                "unit": "USD",
            },
        ),
        (
            "-PLN123.456,78",
            {
                "formatted_value": "-PLN123.46",
                "raw_value": -123.45678,
                "currency_symbol": "PLN",
                "unit": "PLN",
            },
        ),
        (
            "PLN123.456,79",
            {
                "formatted_value": "PLN123.46",
                "raw_value": 123.45679,
                "currency_symbol": "PLN",
                "unit": "PLN",
            },
        ),
        (
            "IDR123.457",
            {
                "formatted_value": "IDR123.46",
                "raw_value": 123.457,
                "currency_symbol": "IDR",
                "unit": "IDR",
            },
        ),
        (
            "JP¥123.457",
            {
                "formatted_value": "¥123",
                "raw_value": 123.457,
                "currency_symbol": "JP¥",
                "unit": "JPY",
            },
        ),
        (
            "-JP¥123.457",
            {
                "formatted_value": "-¥123",
                "raw_value": -123.457,
                "currency_symbol": "JP¥",
                "unit": "JPY",
            },
        ),
        (
            "CN¥123.456,79",
            {
                "formatted_value": "CN¥123.46",
                "raw_value": 123.45679,
                "currency_symbol": "CN¥",
                "unit": "CNY",
            },
        ),
        (
            "U.S.$1,000,000,000",
            {
                "formatted_value": "$1,000,000,000.00",
                "raw_value": 1000000000.0,
                "currency_symbol": "U.S.$",
                "unit": "USD",
            },
        ),
        (
            "1,000,000,000 United states dollars",
            {
                "formatted_value": "$1,000,000,000.00",
                "raw_value": 1000000000.0,
                "currency_symbol": "dollar",
                "unit": "USD",
            },
        ),
        (
            "€1,000",
            {
                "formatted_value": "€1,000.00",
                "raw_value": 1000.0,
                "currency_symbol": "€",
                "unit": "EUR",
            },
        ),
        (
            "¥81,492,866,000",
            {
                "formatted_value": "¥81,492,866,000",
                "raw_value": 81492866000.0,
                "currency_symbol": "¥",
                "unit": "JPY",
            },
        ),
        (
            "one thousand dollars",
            {
                "formatted_value": "$1,000.00",
                "raw_value": 1000.0,
                "currency_symbol": "dollar",
                "unit": "USD",
            },
        ),
        (
            "twenty two million",
            {
                "formatted_value": "22,000,000.00",
                "raw_value": 22000000.0,
                "currency_symbol": None,
                "unit": None,
            },
        ),
        (
            "US$1.75 billion",
            {
                "formatted_value": "$1,750,000,000.00",
                "raw_value": 1750000000.0,
                "currency_symbol": "US$",
                "unit": "USD",
            },
        ),
        (
            "U.S.$1.75 billion",
            {
                "formatted_value": "$1,750,000,000.00",
                "raw_value": 1750000000.0,
                "currency_symbol": "U.S.$",
                "unit": "USD",
            },
        ),
        (
            "¥1.283 billion yen",
            {
                "formatted_value": "¥1,283,000,000",
                "raw_value": 1283000000.0,
                "currency_symbol": "¥",
                "unit": "JPY",
            },
        ),
        (
            "The price is $5mm for the property",
            {
                "formatted_value": "$5,000,000.00",
                "raw_value": 5000000.0,
                "currency_symbol": "$",
                "unit": "USD",
            },
        ),
        (
            "24 thousand dollars",
            {
                "formatted_value": "$24,000.00",
                "raw_value": 24000.0,
                "currency_symbol": "dollar",
                "unit": "USD",
            },
        ),
        (
            "USD 28K",
            {
                "formatted_value": "$28,000.00",
                "raw_value": 28000.0,
                "currency_symbol": "USD",
                "unit": "USD",
            },
        ),
    ],
)
def test_money_parser(money_str, expected):
    money_parser = MoneyParser()
    assert money_parser.parse(money_str) == expected
