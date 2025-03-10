import re
from datetime import datetime
from pprint import pprint

import requests

from cc import cc
from constants import TBA_API_KEY

API_ENDPOINT = "https://www.thebluealliance.com/api/v3/"
CURRENT_YEAR = datetime.now().year

TEAM_NUMBER = input("Team number you wish to get data for (FRC): ")

category = input(
    "What data do you wish to get for team " + cc("GREEN", TEAM_NUMBER) + "? "
    + cc("CYAN", "\n- info\n- eventlist\n- matchlist\n- scout")
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
elif category == "matchlist":
    sorted_events = get_event_list(TEAM_NUMBER)
    EVENT = input(
        "Event code you wish to get match list for:\n"
        + "\n".join([cc('CYAN', f"- {str(event['key']).removeprefix(str(CURRENT_YEAR))} {cc('GRAY', '(' + event['name'] + ')')}") for event in sorted_events])
        + "\n> "
    )
    requestEndpoint = "team/frc" + TEAM_NUMBER + "/event/" + str(CURRENT_YEAR) + str(EVENT) + "/matches/simple"

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
elif category == "scout":
    sorted_events = get_event_list(TEAM_NUMBER)
    EVENT = input(
        "Event code you wish to scout for:\n"
        + "\n".join([cc('CYAN', f"- {str(event['key']).removeprefix(str(CURRENT_YEAR))} {cc('GRAY', '(' + event['name'] + ')')}") for event in sorted_events])
        + "\n> "
    )
    MATCH = input(
        "Match code you wish to scout for:\n[all, "
        + ", ".join([cc('CYAN', str(match).removeprefix(str(CURRENT_YEAR) + str(EVENT.lower()) + "_")) for match in get_match_keys(TEAM_NUMBER, EVENT)])
        + "]\n> "
    )
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

        # BLUE ALLIANCE
        print(cc("BLUE", f"BLUE ALLIANCE ({'WIN' if res['winning_alliance'] == 'blue' else 'LOSE'}):"))
        print(f"- Score: {res['alliances']['blue']['score']}")

        # AUTO
        print(cc("CYAN", f"Autonomous ({res['score_breakdown']['blue']['autoPoints']} pts):"))
        print(f"- Alliance corals placed: {res['score_breakdown']['blue']['autoCoralCount']} ({res['score_breakdown']['blue']['autoCoralPoints']} pts)")
        print(f"- Alliance mobility: {res['score_breakdown']['blue']['autoMobilityPoints']} pts")

        # TELEOP
        print(cc("CYAN", f"Teleop ({res['score_breakdown']['blue']['teleopPoints']} pts):"))
        print(f"- Alliance corals placed: {res['score_breakdown']['blue']['teleopCoralCount']} ({res['score_breakdown']['blue']['teleopCoralPoints']} pts)")
        print(
            f"- Alliance algae scored: {res['score_breakdown']['blue']['wallAlgaeCount']} processor, {res['score_breakdown']['blue']['netAlgaeCount']} net"
            f" ({res['score_breakdown']['blue']['algaePoints']} pts)")
        print(cc("CYAN", "Endgame:"))
        print(
            f"- Robot 1 ({cc('BLUE', res['alliances']['blue']['team_keys'][0].removeprefix('frc'))}) endgame: {cc('YELLOW', res['score_breakdown']['blue']['endGameRobot1'])}")
        print(
            f"- Robot 2 ({cc('BLUE', res['alliances']['blue']['team_keys'][1].removeprefix('frc'))}) endgame: {cc('YELLOW', res['score_breakdown']['blue']['endGameRobot2'])}")
        print(
            f"- Robot 3 ({cc('BLUE', res['alliances']['blue']['team_keys'][2].removeprefix('frc'))}) endgame: {cc('YELLOW', res['score_breakdown']['blue']['endGameRobot3'])}")
        print(cc("CYAN", "Penalties:"))

        # RED ALLIANCE
        print(cc("RED", f"RED ALLIANCE ({'WIN' if res['winning_alliance'] == 'red' else 'LOSE'}):"))
        print(f"- Score: {res['alliances']['red']['score']}")

        # AUTO
        print(cc("CYAN", f"Autonomous ({res['score_breakdown']['red']['autoPoints']} pts):"))
        print(f"- Alliance corals placed: {res['score_breakdown']['red']['autoCoralCount']} ({res['score_breakdown']['red']['autoCoralPoints']} pts)")
        print(f"- Alliance mobility: {res['score_breakdown']['red']['autoMobilityPoints']} pts")

        # TELEOP
        print(cc("CYAN", f"Teleop ({res['score_breakdown']['blue']['teleopPoints']} pts):"))
        print(f"- Alliance corals placed: {res['score_breakdown']['red']['teleopCoralCount']} ({res['score_breakdown']['red']['teleopCoralPoints']} pts)")
        print(
            f"- Alliance algae scored: {res['score_breakdown']['red']['wallAlgaeCount']} processor, {res['score_breakdown']['red']['netAlgaeCount']} net"
            f" ({res['score_breakdown']['red']['algaePoints']} pts)")
        print(cc("CYAN", "Endgame:"))
        print(
            f"- Robot 1 ({cc('RED', res['alliances']['red']['team_keys'][0].removeprefix('frc'))}) endgame: {cc('YELLOW', res['score_breakdown']['red']['endGameRobot1'])}")
        print(
            f"- Robot 2 ({cc('RED', res['alliances']['red']['team_keys'][1].removeprefix('frc'))}) endgame: {cc('YELLOW', res['score_breakdown']['red']['endGameRobot2'])}")
        print(
            f"- Robot 3 ({cc('RED', res['alliances']['red']['team_keys'][2].removeprefix('frc'))}) endgame: {cc('YELLOW', res['score_breakdown']['red']['endGameRobot3'])}")
        print(cc("CYAN", "Penalties:"))

else:
    print(cc("RED", "Invalid category."))
