from datetime import datetime
from pprint import pprint

import requests

from cc import cc
from constants import TBA_API_KEY

API_ENDPOINT = "https://www.thebluealliance.com/api/v3/"
CURRENT_YEAR = datetime.now().year

TEAM_NUMBER = input("Team number you wish to get data for (FRC): ")

category = input(
    "What data do you wish to get for team " + cc("GREEN", TEAM_NUMBER) + "? " + cc("CYAN", "[info, event-list, events, match-list, matches, match]") + ": ")

if category == "info":
    requestEndpoint = "team/frc" + TEAM_NUMBER

    print(cc("GRAY", "Getting team " + TEAM_NUMBER + " info at: " + requestEndpoint))
    res = requests.get(API_ENDPOINT + requestEndpoint + "?X-TBA-Auth-Key=" + TBA_API_KEY).json()
    pprint(res)
elif category == "event-list":
    requestEndpoint = "team/frc" + TEAM_NUMBER + "/events/" + str(CURRENT_YEAR) + "/simple"

    print(cc("GRAY", "Getting team " + TEAM_NUMBER + " event list at: " + requestEndpoint))
    res = requests.get(API_ENDPOINT + requestEndpoint + "?X-TBA-Auth-Key=" + TBA_API_KEY).json()
    sorted_events = sorted(res, key=lambda x: x["start_date"])  # sorts by start date

    for event in sorted_events:
        print(
            f"- {event['name']} ({cc('GRAY', event['key'])}), {cc('FUCHSIA', event['city'])}, {cc('CYAN', event['country'])},"
            f" {cc('GREEN', event['start_date'])} to {cc('RED', event['end_date'])}"
        )
elif category == "events":
    requestEndpoint = "team/frc" + TEAM_NUMBER + "/events/" + str(CURRENT_YEAR)

    print(cc("GRAY", "Getting team " + TEAM_NUMBER + " events at: " + requestEndpoint))
    res = requests.get(API_ENDPOINT + requestEndpoint + "?X-TBA-Auth-Key=" + TBA_API_KEY).json()
    pprint(res)
elif category == "match-list":
    EVENT = input("Event code you wish to get match list for: ")
    requestEndpoint = "team/frc" + TEAM_NUMBER + "/event/" + str(CURRENT_YEAR) + str(EVENT) + "/matches/keys"

    print(cc("GRAY", "Getting team " + TEAM_NUMBER + " match list at: " + requestEndpoint))
    res = requests.get(API_ENDPOINT + requestEndpoint + "?X-TBA-Auth-Key=" + TBA_API_KEY).json()

    sorted_matches = sorted(res)  # only sorts character by character. to improve

    print(cc("BLUE", "QUALIFICATION MATCHES"))
    for match in sorted_matches:
        if "_qm" in match:
            print("- " + match)
    print(cc("BLUE", "PLAYOFF MATCHES"))
    for match in sorted_matches:
        if "_sf" in match:
            print("- " + match)
    print(cc("BLUE", "FINAL MATCHES"))
    for match in sorted_matches:
        if "_f" in match:
            print("- " + match)
