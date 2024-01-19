import re

import dateparser
from money import Money
from word2number import w2n

import nlm_utils.parsers.constants as constants


class PeriodParser:
    def __init__(
        self,
        locale="en_US",
    ):
        self.locale = locale
        self.numeric_value_parser = NumericValueParser(
            units=constants.PERIOD_WORDS,
            include_plurals=True,
            locale=locale,
        )

    def parse(self, period_str):
        count, period = self.numeric_value_parser.parse(period_str)
        raw_value = count
        if period:
            period_singular = period.replace("s", "")
            period_singular = period_singular.replace("()", "")
            if period_singular in constants.PERIOD_MULTIPLIERS:
                raw_value = count * constants.PERIOD_MULTIPLIERS[period_singular]
            if period_singular == "month":
                raw_value += (
                    (count // 12) * 5 * constants.PERIOD_MULTIPLIERS["day"]
                )  # Add 5 more days per year
            if period_singular in constants.PERIOD_STANDARDIZED_WORDS:
                period_singular = constants.PERIOD_STANDARDIZED_WORDS[period_singular]
        parsed_value = {
            "formatted_value": period_str,
            "raw_value": raw_value,
            "time_value": count,
            "time_unit": period_singular,
        }

        return parsed_value


class PercentParser:
    def __init__(
        self,
        locale="en_US",
    ):
        self.locale = locale
        self.numeric_value_parser = NumericValueParser(
            units=["%", "percent", "basis points", "bps"],
            locale=locale,
        )

    def parse(self, percent_str):
        percent, percent_label = self.numeric_value_parser.parse(percent_str)
        raw_value = percent
        if percent_label in ["basis points", "bps"]:
            percent_label = "bps"
        if percent_label in ["%", "percent"]:
            percent_label = "%"
        parsed_value = {
            "formatted_value": percent_str,
            "raw_value": raw_value,
            "percent_label": percent_label,
        }

        return parsed_value


class CountParser:
    def __init__(
        self,
        locale="en_US",
    ):
        self.locale = locale
        self.numeric_value_parser = NumericValueParser(
            locale=locale,
        )

    def parse(self, count_str):
        count, _ = self.numeric_value_parser.parse(count_str)
        raw_value = count
        parsed_value = {
            "formatted_value": count_str,
            "raw_value": raw_value,
        }

        return parsed_value


class DateParser:
    def __init__(
        self,
        locale="en_US",
    ):
        self.locale = locale
        self.parser = dateparser.DateDataParser(
            languages=["en"],
            settings={
                "PREFER_DAY_OF_MONTH": "first",
                "TIMEZONE": "UTC",
                "RETURN_AS_TIMEZONE_AWARE": True,
            },
        )

    def _parse(self, date_str: str):
        date_data = self.parser.get_date_data(date_str)
        if date_data:
            if date_data["period"] in ["day", "month"]:
                return date_data["date_obj"]
            elif date_data["period"] == "year":
                date_data = self.parser.get_date_data("January " + date_str)
                if date_data:
                    return date_data["date_obj"]
        return date_data

    def parse(self, date_str: str):
        parsed_value = None
        if date_str and date_str.strip() != "":
            date_str = date_str.replace("day of", "")
            date_val = self._parse(date_str)
            if not date_val:
                date_str = re.sub(" ", "", date_str)
                date_str = re.sub("st|nd|rd|th", "", date_str)
                date_val = self._parse(date_str)
            if date_val:
                parsed_value = {
                    "formatted_value": date_str,
                    "raw_value": date_val.timestamp(),
                }
        else:
            parsed_value = {
                "formatted_value": date_str,
                "raw_value": date_str,
            }
        return parsed_value


class NumericValueParser:
    def __init__(
        self,
        units=[],
        include_plurals=False,
        locale="en_US",
    ):
        self.locale = locale
        if not include_plurals:
            unit_pattern = "|".join(re.escape(i) for i in units)
        else:
            unit_pattern = "|".join(re.escape(i) + "[s|(s)]?" for i in units)

        self.unit_pattern = re.compile(
            unit_pattern,
            re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE,
        )
        amount_pattern = r"""
            (?P<amount>{amount_pattern})\s?
            (?P<multiplier>({number_multipliers})\b)?
        """.format(
            amount_pattern=constants.AMOUNT_PATTERN,
            number_multipliers="|".join(
                re.escape(i) for i in constants.NUMBER_MULTIPLIERS
            ),
        )
        self.amount_pattern_re = re.compile(
            amount_pattern,
            re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE,
        )

    def convert_to_float(self, frac_str):
        try:
            return float(frac_str)
        except ValueError:
            num, denom = frac_str.split("/")
            try:
                leading, num = num.split(" ")
                amount_match = self.amount_pattern_re.search(leading.lower())
                if amount_match:
                    match_dict = amount_match.groupdict()
                    whole = float(match_dict["amount"].replace(",", ""))
                else:
                    whole = float(leading)
            except ValueError:
                whole = 0
            frac = float(num) / float(denom)
            return whole - frac if whole < 0 else whole + frac

    def parse(self, number_value_str):
        unit_match = self.unit_pattern.search(number_value_str)
        unit = None
        if unit_match:
            number_value_str = (
                number_value_str[0 : unit_match.span()[0]]
                + number_value_str[unit_match.span()[1] :]
            )
            unit = unit_match.group(0)

        if "/" in number_value_str:
            return self.convert_to_float(number_value_str), unit

        amount_match = self.amount_pattern_re.search(number_value_str.lower())
        if amount_match:
            match_dict = amount_match.groupdict()
            amount = float(match_dict["amount"].replace(",", ""))
            if (
                "multiplier" in match_dict
                and match_dict["multiplier"]
                and match_dict["multiplier"] != ""
            ):
                multiplier = constants.NUMBER_MULTIPLIERS[match_dict["multiplier"]]
                amount = amount * multiplier
        else:
            try:
                amount = w2n.word_to_num(number_value_str)
            except ValueError:
                amount = None

        return amount, unit


class MoneyParser:
    def __init__(
        self,
        locale="en_US",
    ):
        self.currencies = constants.CURRENCY_SYMBOLS
        self.currency_symbol_2_code = MoneyParser.reverse_map_currencies()
        self.locale = locale
        self.numeric_value_parser = NumericValueParser(
            units=self.currency_symbol_2_code.keys(),
            locale=locale,
        )

    @staticmethod
    def reverse_map_currencies():
        symbol_2_code = {}
        for k, v in constants.CURRENCY_SYMBOLS.items():
            for s in v:
                symbol_2_code[s.lower()] = k
        return symbol_2_code

    def parse(self, money_str):
        currency_code = None
        amount, currency_symbol = self.numeric_value_parser.parse(money_str)
        if currency_symbol:
            currency_code = self.currency_symbol_2_code[currency_symbol.lower()]

        if currency_code:
            try:
                formatted_value = Money(amount, currency_code).format(self.locale)
            except Exception:
                formatted_value = f"{currency_code} {'{:,.2f}'.format(amount)}"
        else:
            try:
                formatted_value = f"{amount:,.2f}"
            except Exception:
                formatted_value = ""

        parsed_value = {
            "formatted_value": formatted_value,
            "raw_value": amount,
            "currency_symbol": currency_symbol,
            "unit": currency_code,
        }
        # print(parsed_value)
        return parsed_value
