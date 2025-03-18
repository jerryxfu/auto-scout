import re
from datetime import datetime
from pprint import pprint

import requests

import eventlist
import eventmatches
import matchlist
import scout
from cc import cc
from constants import TBA_API_KEY

API_ENDPOINT = "https://www.thebluealliance.com/api/v3/"
CURRENT_YEAR = datetime.now().year

TEAM_NUMBER = input("Team number you wish to get data for (FRC): ")

if not TEAM_NUMBER.isdigit():
    print(cc("RED", "Team number must be numeric."))
    exit()

TEAM_NUMBER = int(TEAM_NUMBER)

category = input(
    "What data do you wish to get for team " + cc("GREEN", str(TEAM_NUMBER)) + "? "
    + cc("CYAN", "\n- info\n- eventlist\n- matchlist\n- eventmatches\n- scout")
    + "\n> "
)


def natural_key(s):
    # Convert each numeric part to an integer, leave other parts as lower-case strings
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]


def get_event_list(_team, _year):
    _requestEndpoint = "team/frc" + _team + "/events/" + str(_year) + "/simple"

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


def get_match_row(_match, _event_key, _year):
    match_key = _match["key"].removeprefix(str(_year) + str(_event_key.lower()) + "_").upper()
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
    requestEndpoint = "team/frc" + str(TEAM_NUMBER)

    print(cc("GRAY", "Getting team " + str(TEAM_NUMBER) + " info at: " + requestEndpoint))
    res = requests.get(API_ENDPOINT + requestEndpoint + "?X-TBA-Auth-Key=" + TBA_API_KEY).json()
    pprint(res)
elif category == "eventlist":
    eventlist.event_list(team_number=TEAM_NUMBER, current_year=CURRENT_YEAR)

# Get the list of matches for a team at an event
elif category == "matchlist":
    matchlist.match_list(api_endpoint=API_ENDPOINT, team_number=TEAM_NUMBER, current_year=CURRENT_YEAR)

# Get the list of all matches at an event
elif category == "eventmatches":
    eventmatches.event_matches(api_endpoint=API_ENDPOINT, team_number=TEAM_NUMBER, current_year=CURRENT_YEAR)

elif category == "scout":
    scout.scout(api_endpoint=API_ENDPOINT, team_number=TEAM_NUMBER, current_year=CURRENT_YEAR)

else:
    print(cc("RED", "Invalid category."))
