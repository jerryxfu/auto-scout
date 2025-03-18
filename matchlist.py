import pandas as pd
import requests

import constants
import main
from cc import cc


def match_list(api_endpoint: str, team_number: int, current_year: int):
    sorted_events = main.get_event_list(team_number, current_year)
    EVENT = input(
        "Event code you wish to get match list for:\n"
        + "\n".join([cc('CYAN', f"- {str(event['key']).removeprefix(str(current_year))} {cc('GRAY', '(' + event['name'] + ')')}") for event in sorted_events])
        + "\n> "
    )
    if EVENT not in [event["key"].removeprefix(str(current_year)) for event in sorted_events]:
        print(cc("RED", "Invalid event code."))
        exit()

    requestEndpoint = "team/frc" + str(team_number) + "/event/" + str(current_year) + str(EVENT) + "/matches/simple"

    print(cc("GRAY", "Getting team " + str(team_number) + " match list at: " + requestEndpoint))
    res = requests.get(api_endpoint + requestEndpoint + "?X-TBA-Auth-Key=" + constants.TBA_API_KEY).json()

    # Sort the matches by their keys using the natural_key function
    sorted_matches = sorted(res, key=lambda match: main.natural_key(match["key"]))

    print(cc("CYAN", "QUALIFICATION MATCHES"))
    print(cc("YELLOW", f"Generating ") + cc("GREEN", "Excel") + cc("YELLOW", " file..."))
    data = []
    for match in sorted_matches:
        if "_qm" in match["key"]:
            print("- " + match["key"] + main.get_alliance_str(match["alliances"]))
            match_data = main.get_match_row(match, EVENT, current_year)
            data.append(match_data)
    print(cc("CYAN", "PLAYOFF MATCHES"))
    for match in sorted_matches:
        if "_sf" in match["key"]:
            print("- " + match["key"] + main.get_alliance_str(match["alliances"]))
            match_data = main.get_match_row(match, EVENT, current_year)
            data.append(match_data)
    print(cc("CYAN", "FINAL MATCHES"))
    for match in sorted_matches:
        if "_f" in match["key"]:
            print("- " + match["key"] + main.get_alliance_str(match["alliances"]))
            match_data = main.get_match_row(match, EVENT, current_year)
            data.append(match_data)

    columns = ["Match", "Red 1", "Red 2", "Red 3", "Blue 1", "Blue 2", "Blue 3", "Red Score", "Blue Score"]
    df = pd.DataFrame(data, columns=columns)
    print(cc("YELLOW", "Converting data types..."))
    df.convert_dtypes()
    print(cc("YELLOW", "Applying colors..."))
    df = main.style_df(df.style)
    df.to_excel("output/match_list_" + EVENT + "_" + str(team_number) + ".xlsx", index=False)
    print(cc("GREEN", "Excel file generated at output/match_list_" + EVENT + "_" + str(team_number) + ".xlsx"))
