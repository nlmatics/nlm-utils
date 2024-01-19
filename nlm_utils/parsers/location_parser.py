import re

import nlm_utils.parsers.constants as constants

# General Settings
ENABLE_LOCATION_CACHE = True


class LocationParser:
    def __init__(
        self,
    ):
        # State Names Pattern
        final_str = ""
        for s_name in constants.US_STATES_DICT.values():
            state_str = ""
            for tok in s_name.split():
                state_str = f"{tok}" if not state_str else f"{state_str}\\s+{tok}"
            final_str = f"{state_str}" if not final_str else f"{final_str}|{state_str}"
        state_reg_exp = fr"(?i)\b(?:{final_str})\b"
        self.state_regexp_pattern = re.compile(state_reg_exp)

        # State abbreviations pattern
        abbr_str = ""
        for s_abbr in constants.US_STATES_DICT.keys():
            abbr_str = f"{s_abbr}" if not abbr_str else f"{abbr_str}|{s_abbr}"
        abbr_str_exp = fr"\b(?:{abbr_str})\b"
        self.abbr_regexp_pattern = re.compile(abbr_str_exp)

        self.location_cache = {}

    @staticmethod
    def pre_process_location_str(location_str):
        for country, abbreviations in constants.COUNTRY_ABBREVIATIONS:
            for abbr in abbreviations:
                new_str = ""
                try:
                    new_str = re.sub(fr"{abbr}$", country, location_str)
                except Exception:
                    pass
                if location_str != new_str:
                    location_str = new_str
                    break
        return location_str

    def parse(self, location_str):
        parsed_loc_str = location_str
        if location_str and isinstance(location_str, str):  # Consider only string type
            processed_loc_str = self.pre_process_location_str(location_str)
            if processed_loc_str in self.location_cache:
                parsed_loc_str = self.location_cache[processed_loc_str]
            else:
                loc_data = self.state_regexp_pattern.findall(processed_loc_str)
                if loc_data:
                    parsed_loc_str = loc_data[0].title()
                else:
                    loc_data = self.abbr_regexp_pattern.findall(processed_loc_str)
                    parsed_loc_str = (
                        constants.US_STATES_DICT[loc_data[0]]
                        if loc_data
                        else location_str
                    )

                if ENABLE_LOCATION_CACHE:
                    self.location_cache[processed_loc_str] = parsed_loc_str
        parsed_value = {
            "formatted_value": parsed_loc_str,
        }
        return parsed_value
