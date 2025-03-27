import pandas as pd
import requests

import constants
import main
from cc import cc


### Missing logic

def print_alliance_results(match, alliance):
    # ALLIANCE
    print(f"- Score: {match['alliances'][alliance]['score']}")

    # AUTO
    print(cc(alliance.upper(), f"Autonomous ({match['score_breakdown'][alliance]['autoPoints']} pts):"))
    print(f"- Alliance corals placed: {match['score_breakdown'][alliance]['autoCoralCount']} ({match['score_breakdown'][alliance]['autoCoralPoints']} pts)")
    print(f"- Alliance mobility: {match['score_breakdown'][alliance]['autoMobilityPoints']} pts")
    print(
        f"- Robot 1 ({cc(alliance.upper(), match['alliances'][alliance]['team_keys'][0].removeprefix('frc'))}) leave: {cc('YELLOW', match['score_breakdown'][alliance]['autoLineRobot1'])}")
    print(
        f"- Robot 2 ({cc(alliance.upper(), match['alliances'][alliance]['team_keys'][1].removeprefix('frc'))}) leave: {cc('YELLOW', match['score_breakdown'][alliance]['autoLineRobot2'])}")
    print(
        f"- Robot 3 ({cc(alliance.upper(), match['alliances'][alliance]['team_keys'][2].removeprefix('frc'))}) leave: {cc('YELLOW', match['score_breakdown'][alliance]['autoLineRobot3'])}")

    # TELEOP
    print(cc(alliance.upper(), f"Teleop ({match['score_breakdown'][alliance]['teleopPoints']} pts):"))
    print(
        f"- Alliance corals placed: {match['score_breakdown'][alliance]['teleopCoralCount']} ({match['score_breakdown'][alliance]['teleopCoralPoints']} pts)")
    print(
        f"- Alliance algae scored: {match['score_breakdown'][alliance]['wallAlgaeCount']} processor, {match['score_breakdown'][alliance]['netAlgaeCount']} net"
        f" ({match['score_breakdown'][alliance]['algaePoints']} pts)")

    # ENDGAME
    print(cc(alliance.upper(), "Endgame:"))
    print(
        f"- Robot 1 ({cc(alliance.upper(), match['alliances'][alliance]['team_keys'][0].removeprefix('frc'))}) endgame: {cc('YELLOW', match['score_breakdown'][alliance]['endGameRobot1'])}")
    print(
        f"- Robot 2 ({cc(alliance.upper(), match['alliances'][alliance]['team_keys'][1].removeprefix('frc'))}) endgame: {cc('YELLOW', match['score_breakdown'][alliance]['endGameRobot2'])}")
    print(
        f"- Robot 3 ({cc(alliance.upper(), match['alliances'][alliance]['team_keys'][2].removeprefix('frc'))}) endgame: {cc('YELLOW', match['score_breakdown'][alliance]['endGameRobot3'])}")
    print(cc(alliance.upper(), "Penalties:"))


def scout(api_endpoint: str, team_number: int, current_year: int):
    sorted_events = main.get_event_list(team_number, current_year)
    EVENT = input(
        "Event code you wish to scout for:\n"
        + "\n".join([cc('CYAN', f"- {str(event['key']).removeprefix(str(current_year))} {cc('GRAY', '(' + event['name'] + ')')}") for event in sorted_events])
        + "\n> "
    )
    if EVENT not in [event["key"].removeprefix(str(current_year)) for event in sorted_events]:
        print(cc("RED", "Invalid event code."))
        exit()

    requestEndpoint = "event/" + str(current_year) + str(EVENT) + "/matches"

    print(cc("GRAY", "Getting team " + EVENT + " match list at: " + requestEndpoint))
    res = requests.get(api_endpoint + requestEndpoint + "?X-TBA-Auth-Key=" + constants.TBA_API_KEY).json()

    # Sort the matches by their keys using the natural_key function
    sorted_matches = sorted(res, key=lambda match: main.natural_key(match["key"]))

    data = []
    print(cc("CYAN", "QUALIFICATION MATCHES"))
    for match in sorted_matches:
        if "_qm" in match["key"]:
            print("- " + match["key"] + main.get_alliance_str(match["alliances"]))
            print(cc("CYAN", f"AutoScout {'QUALIFICATIONS' if 'qm' in match['event_key'] else 'PLAYOFFS' if 'sf' in match['event_key'] else 'FINALS'} MATCH "
                     + str(match['match_number'])) + str(main.get_alliance_str(match["alliances"]).replace("frc", "")))
            print(cc("BLUE", f"BLUE ALLIANCE ({'WIN' if match['winning_alliance'] == 'blue' else 'LOSE'}):"))
            print_alliance_results(match, "blue")
            print_alliance_results(match, "red")
            # scout_match(team_number, match)

    print(cc("CYAN", "PLAYOFF MATCHES"))
    for match in sorted_matches:
        if "_sf" in match["key"]:
            print("- " + match["key"] + main.get_alliance_str(match["alliances"]))
            print(cc("CYAN", f"AutoScout {'QUALIFICATIONS' if 'qm' in match['event_key'] else 'PLAYOFFS' if 'sf' in match['event_key'] else 'FINALS'} MATCH "
                     + str(match['match_number'])) + str(main.get_alliance_str(match["alliances"]).replace("frc", "")))
            print(cc("BLUE", f"BLUE ALLIANCE ({'WIN' if match['winning_alliance'] == 'blue' else 'LOSE'}):"))
            print_alliance_results(match, "blue")
            print_alliance_results(match, "red")
            # scout_match(team_number, match)

    print(cc("CYAN", "FINAL MATCHES"))
    for match in sorted_matches:
        if "_f" in match["key"]:
            print("- " + match["key"] + main.get_alliance_str(match["alliances"]))
            print(cc("CYAN", f"AutoScout {'QUALIFICATIONS' if 'qm' in match['event_key'] else 'PLAYOFFS' if 'sf' in match['event_key'] else 'FINALS'} MATCH "
                     + str(match['match_number'])) + str(main.get_alliance_str(match["alliances"]).replace("frc", "")))
            print(cc("BLUE", f"BLUE ALLIANCE ({'WIN' if match['winning_alliance'] == 'blue' else 'LOSE'}):"))
            print_alliance_results(match, "blue")
            print_alliance_results(match, "red")
            # scout_match(team_number, match)

    columns = ["Team", "Auto leave", "Consistency", "End game", "Consistency"]
    df = pd.DataFrame(data, columns=columns)
    print(cc("YELLOW", "Converting data types..."))
    df.convert_dtypes()
    print(cc("YELLOW", "Applying colors..."))
    df = main.style_df(df.style)
    df.to_excel("output/event_matches_" + str(current_year) + EVENT + ".xlsx", index=False)
    print(cc("GREEN", "Excel file generated at output/event_matches_" + str(current_year) + EVENT + ".xlsx"))
