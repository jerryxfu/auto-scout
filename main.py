import re
from datetime import datetime
from pprint import pprint

import pandas as pd
import requests

from cc import cc
from constants import TBA_API_KEY

API_ENDPOINT = "https://www.thebluealliance.com/api/v3/"
CURRENT_YEAR = datetime.now().year

TEAM_NUMBER = input("Team number you wish to get data for (FRC): ")

if not TEAM_NUMBER.isdigit():
    print(cc("RED", "Team number must be numeric."))
    exit()

category = input(
    "What data do you wish to get for team " + cc("GREEN", TEAM_NUMBER) + "? "
    + cc("CYAN", "\n- info\n- eventlist\n- matchlist\n- eventmatches\n- scout")
    + "\n> "
)


def natural_key(s):
    # Convert each numeric part to an integer, leave other parts as lower-case strings
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]


def get_event_list(_team):
    _requestEndpoint = "team/frc" + _team + "/events/" + str(CURRENT_YEAR) + "/simple"

    print(cc("GRAY", "Getting team " + _team + " event list at: " + _requestEndpoint))
    _res = requests.get(API_ENDPOINT + _requestEndpoint + "?X-TBA-Auth-Key=" + TBA_API_KEY).json()
    return sorted(_res, key=lambda x: x["start_date"])  # sorts by start date


def get_match_keys(_team, _event):
    _requestEndpoint = "team/frc" + _team + "/event/" + str(CURRENT_YEAR) + str(_event) + "/matches/keys"

    print(cc("GRAY", "Getting team " + _team + " match list at: " + _requestEndpoint))
    _res = requests.get(API_ENDPOINT + _requestEndpoint + "?X-TBA-Auth-Key=" + TBA_API_KEY).json()

    # Extract and sort match keys
    _sorted_match_keys = sorted(_res, key=natural_key)

    return _sorted_match_keys


def get_alliance_str(_match):
    return (cc("BLUE", " (" + ", ".join(_match["blue"]["team_keys"]) + ")")
            + " vs " + cc("RED", "(" + ", ".join(_match["red"]["team_keys"]) + ")"))


def get_match_row(_match):
    match_key = _match["key"].removeprefix(str(CURRENT_YEAR) + str(EVENT.lower()) + "_").upper()
    red_alliance = [int(team.removeprefix('frc')) for team in _match["alliances"]["red"]["team_keys"]]
    blue_alliance = [int(team.removeprefix('frc')) for team in _match["alliances"]["blue"]["team_keys"]]
    red_score = _match["alliances"]["red"]["score"]
    blue_score = _match["alliances"]["blue"]["score"]

    return [match_key, *red_alliance, *blue_alliance, red_score, blue_score]


def style_df(_df_styler):
    _df_styler = _df_styler.map(lambda x: 'background-color: #ebf1de', subset=["Match"])
    _df_styler = _df_styler.map(lambda x: 'background-color: #f2dcdb', subset=["Red 1", "Red 2", "Red 3"])
    _df_styler = _df_styler.map(lambda x: 'background-color: #dce6f1', subset=["Blue 1", "Blue 2", "Blue 3"])
    _df_styler = _df_styler.map(lambda x: 'background-color: #f2dcdb', subset=["Red Score"])
    _df_styler = _df_styler.map(lambda x: 'background-color: #b8cce4', subset=["Blue Score"])
    return _df_styler


if category == "info":
    requestEndpoint = "team/frc" + TEAM_NUMBER

    print(cc("GRAY", "Getting team " + TEAM_NUMBER + " info at: " + requestEndpoint))
    res = requests.get(API_ENDPOINT + requestEndpoint + "?X-TBA-Auth-Key=" + TBA_API_KEY).json()
    pprint(res)
elif category == "eventlist":
    # requestEndpoint = "team/frc" + TEAM_NUMBER + "/events/" + str(CURRENT_YEAR) + "/simple"
    #
    # print(cc("GRAY", "Getting team " + TEAM_NUMBER + " event list at: " + requestEndpoint))
    # res = requests.get(API_ENDPOINT + requestEndpoint + "?X-TBA-Auth-Key=" + TBA_API_KEY).json()
    # sorted_events = sorted(res, key=lambda x: x["start_date"])  # sorts by start date
    sorted_events = get_event_list(TEAM_NUMBER)

    for event in sorted_events:
        print(
            f"- {event['name']} ({cc('GRAY', event['key'])}), {cc('FUCHSIA', event['city'])}, {cc('CYAN', event['country'])},"
            f" {cc('GREEN', event['start_date'])} to {cc('RED', event['end_date'])}"
        )
# Get the list of matches for a team at an event
elif category == "matchlist":
    sorted_events = get_event_list(TEAM_NUMBER)
    EVENT = input(
        "Event code you wish to get match list for:\n"
        + "\n".join([cc('CYAN', f"- {str(event['key']).removeprefix(str(CURRENT_YEAR))} {cc('GRAY', '(' + event['name'] + ')')}") for event in sorted_events])
        + "\n> "
    )
    if EVENT not in [event["key"].removeprefix(str(CURRENT_YEAR)) for event in sorted_events]:
        print(cc("RED", "Invalid event code."))
        exit()

    requestEndpoint = "team/frc" + TEAM_NUMBER + "/event/" + str(CURRENT_YEAR) + str(EVENT) + "/matches/simple"

    print(cc("GRAY", "Getting team " + TEAM_NUMBER + " match list at: " + requestEndpoint))
    res = requests.get(API_ENDPOINT + requestEndpoint + "?X-TBA-Auth-Key=" + TBA_API_KEY).json()

    # Sort the matches by their keys using the natural_key function
    sorted_matches = sorted(res, key=lambda match: natural_key(match["key"]))

    print(cc("CYAN", "QUALIFICATION MATCHES"))
    print(cc("YELLOW", f"Generating ") + cc("GREEN", "Excel") + cc("YELLOW", " file..."))
    data = []
    for match in sorted_matches:
        if "_qm" in match["key"]:
            print("- " + match["key"] + get_alliance_str(match["alliances"]))
            match_data = get_match_row(match)
            data.append(match_data)
    print(cc("CYAN", "PLAYOFF MATCHES"))
    for match in sorted_matches:
        if "_sf" in match["key"]:
            print("- " + match["key"] + get_alliance_str(match["alliances"]))
            match_data = get_match_row(match)
            data.append(match_data)
    print(cc("CYAN", "FINAL MATCHES"))
    for match in sorted_matches:
        if "_f" in match["key"]:
            print("- " + match["key"] + get_alliance_str(match["alliances"]))
            match_data = get_match_row(match)
            data.append(match_data)

    columns = ["Match", "Red 1", "Red 2", "Red 3", "Blue 1", "Blue 2", "Blue 3", "Red Score", "Blue Score"]
    df = pd.DataFrame(data, columns=columns)
    print(cc("YELLOW", "Converting data types..."))
    df.convert_dtypes()
    print(cc("YELLOW", "Applying colors..."))
    df = style_df(df.style)
    df.to_excel("output/match_list_" + EVENT + "_" + TEAM_NUMBER + ".xlsx", index=False)
    print(cc("GREEN", "Excel file generated at output/match_list_" + EVENT + "_" + TEAM_NUMBER + ".xlsx"))

# Get the list of all matches at an event
elif category == "eventmatches":
    sorted_events = get_event_list(TEAM_NUMBER)
    EVENT = input(
        "Event code you wish to get match list for:\n"
        + "\n".join([cc('CYAN', f"- {str(event['key']).removeprefix(str(CURRENT_YEAR))} {cc('GRAY', '(' + event['name'] + ')')}") for event in sorted_events])
        + "\n> "
    )
    if EVENT not in [event["key"].removeprefix(str(CURRENT_YEAR)) for event in sorted_events]:
        print(cc("RED", "Invalid event code."))
        exit()

    requestEndpoint = "event/" + str(CURRENT_YEAR) + str(EVENT) + "/matches/simple"
    print(cc("GRAY", "Getting " + str(CURRENT_YEAR) + str(EVENT) + " match list at: " + requestEndpoint))
    res = requests.get(API_ENDPOINT + requestEndpoint + "?X-TBA-Auth-Key=" + TBA_API_KEY).json()

    # Sort the matches by their keys using the natural_key function
    sorted_matches = sorted(res, key=lambda match: natural_key(match["key"]))

    print(cc("CYAN", "QUALIFICATION MATCHES"))
    print(cc("YELLOW", f"Generating ") + cc("GREEN", "Excel") + cc("YELLOW", " file..."))
    data = []
    for match in sorted_matches:
        if "_qm" in match["key"]:
            print("- " + match["key"] + get_alliance_str(match["alliances"]))
            match_data = get_match_row(match)
            data.append(match_data)
    print(cc("CYAN", "PLAYOFF MATCHES"))
    for match in sorted_matches:
        if "_sf" in match["key"]:
            print("- " + match["key"] + get_alliance_str(match["alliances"]))
            match_data = get_match_row(match)
            data.append(match_data)
    print(cc("CYAN", "FINAL MATCHES"))
    for match in sorted_matches:
        if "_f" in match["key"]:
            print("- " + match["key"] + get_alliance_str(match["alliances"]))
            match_data = get_match_row(match)
            data.append(match_data)

    columns = ["Match", "Red 1", "Red 2", "Red 3", "Blue 1", "Blue 2", "Blue 3", "Red Score", "Blue Score"]
    df = pd.DataFrame(data, columns=columns)
    print(cc("YELLOW", "Converting data types..."))
    df.convert_dtypes()
    print(cc("YELLOW", "Applying colors..."))
    df = style_df(df.style)
    df.to_excel("output/event_matches_" + str(CURRENT_YEAR) + EVENT + ".xlsx", index=False)
    print(cc("GREEN", "Excel file generated at output/event_matches_" + str(CURRENT_YEAR) + EVENT + ".xlsx"))

elif category == "scout":
    sorted_events = get_event_list(TEAM_NUMBER)
    EVENT = input(
        "Event code you wish to scout for:\n"
        + "\n".join([cc('CYAN', f"- {str(event['key']).removeprefix(str(CURRENT_YEAR))} {cc('GRAY', '(' + event['name'] + ')')}") for event in sorted_events])
        + "\n> "
    )
    if EVENT not in [event["key"].removeprefix(str(CURRENT_YEAR)) for event in sorted_events]:
        print(cc("RED", "Invalid event code."))
        exit()

    MATCHES = get_match_keys(TEAM_NUMBER, EVENT)
    MATCHES.append("all")
    MATCH = input(
        "Match code you wish to scout for:\n["
        + ", ".join([cc('CYAN', str(match).removeprefix(str(CURRENT_YEAR) + str(EVENT.lower()) + "_")) for match in MATCHES])
        + "]\n> "
    )
    if MATCH not in [match.removeprefix(str(CURRENT_YEAR) + str(EVENT.lower()) + "_") for match in MATCHES]:
        print(cc("RED", "Invalid match."))
        exit()
    if MATCH == "all":
        requestEndpoint = "team/frc" + TEAM_NUMBER + "/event/" + str(CURRENT_YEAR) + str(EVENT) + "/matches"

        print(cc("GRAY", "Getting team " + TEAM_NUMBER + " match list at: " + requestEndpoint))
        res = requests.get(API_ENDPOINT + requestEndpoint + "?X-TBA-Auth-Key=" + TBA_API_KEY).json()

        # Sort the matches by their keys using the natural_key function
        sorted_matches = sorted(res, key=lambda match: natural_key(match["key"]))

        print(cc("CYAN", "QUALIFICATION MATCHES"))
        for match in sorted_matches:
            if "_qm" in match["key"]:
                print("- " + match["key"] + get_alliance_str(match["alliances"]))
        print(cc("CYAN", "PLAYOFF MATCHES"))
        for match in sorted_matches:
            if "_sf" in match["key"]:
                print("- " + match["key"] + get_alliance_str(match["alliances"]))
        print(cc("CYAN", "FINAL MATCHES"))
        for match in sorted_matches:
            if "_f" in match["key"]:
                print("- " + match["key"] + get_alliance_str(match["alliances"]))
    else:
        requestEndpoint = "match/" + str(CURRENT_YEAR) + str(EVENT) + "_" + MATCH

        print(cc("GRAY", "Getting match " + str(CURRENT_YEAR) + str(EVENT) + "_" + MATCH + " at: " + requestEndpoint))
        res = requests.get(API_ENDPOINT + requestEndpoint + "?X-TBA-Auth-Key=" + TBA_API_KEY).json()

        print(cc("CYAN", f"AutoScout {'QUALIFICATIONS' if 'qm' in res['event_key'] else 'PLAYOFFS' if 'sf' in res['event_key'] else 'FINALS'} MATCH "
                 + str(res['match_number'])) + str(get_alliance_str(res["alliances"]).replace("frc", "")))
        print(cc("BLUE", f"BLUE ALLIANCE ({'WIN' if res['winning_alliance'] == 'blue' else 'LOSE'}):"))


        def print_alliance_results(alliance):
            # ALLIANCE
            print(f"- Score: {res['alliances'][alliance]['score']}")

            # AUTO
            print(cc(alliance.upper(), f"Autonomous ({res['score_breakdown'][alliance]['autoPoints']} pts):"))
            print(f"- Alliance corals placed: {res['score_breakdown'][alliance]['autoCoralCount']} ({res['score_breakdown'][alliance]['autoCoralPoints']} pts)")
            print(f"- Alliance mobility: {res['score_breakdown'][alliance]['autoMobilityPoints']} pts")
            print(
                f"- Robot 1 ({cc(alliance.upper(), res['alliances'][alliance]['team_keys'][0].removeprefix('frc'))}) leave: {cc('YELLOW', res['score_breakdown'][alliance]['autoLineRobot1'])}")
            print(
                f"- Robot 2 ({cc(alliance.upper(), res['alliances'][alliance]['team_keys'][1].removeprefix('frc'))}) leave: {cc('YELLOW', res['score_breakdown'][alliance]['autoLineRobot2'])}")
            print(
                f"- Robot 3 ({cc(alliance.upper(), res['alliances'][alliance]['team_keys'][2].removeprefix('frc'))}) leave: {cc('YELLOW', res['score_breakdown'][alliance]['autoLineRobot3'])}")

            # TELEOP
            print(cc(alliance.upper(), f"Teleop ({res['score_breakdown'][alliance]['teleopPoints']} pts):"))
            print(
                f"- Alliance corals placed: {res['score_breakdown'][alliance]['teleopCoralCount']} ({res['score_breakdown'][alliance]['teleopCoralPoints']} pts)")
            print(
                f"- Alliance algae scored: {res['score_breakdown'][alliance]['wallAlgaeCount']} processor, {res['score_breakdown'][alliance]['netAlgaeCount']} net"
                f" ({res['score_breakdown'][alliance]['algaePoints']} pts)")

            # ENDGAME
            print(cc(alliance.upper(), "Endgame:"))
            print(
                f"- Robot 1 ({cc(alliance.upper(), res['alliances'][alliance]['team_keys'][0].removeprefix('frc'))}) endgame: {cc('YELLOW', res['score_breakdown'][alliance]['endGameRobot1'])}")
            print(
                f"- Robot 2 ({cc(alliance.upper(), res['alliances'][alliance]['team_keys'][1].removeprefix('frc'))}) endgame: {cc('YELLOW', res['score_breakdown'][alliance]['endGameRobot2'])}")
            print(
                f"- Robot 3 ({cc(alliance.upper(), res['alliances'][alliance]['team_keys'][2].removeprefix('frc'))}) endgame: {cc('YELLOW', res['score_breakdown'][alliance]['endGameRobot3'])}")
            print(cc(alliance.upper(), "Penalties:"))


        print_alliance_results("blue")
        print_alliance_results("red")

else:
    print(cc("RED", "Invalid category."))
