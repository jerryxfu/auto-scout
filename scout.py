import requests

import constants
import main
from cc import cc


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

    MATCHES = main.get_match_keys(team_number, EVENT)
    MATCHES.append("all")
    MATCH = input(
        "Match code you wish to scout for:\n["
        + ", ".join([cc('CYAN', str(match).removeprefix(str(current_year) + str(EVENT.lower()) + "_")) for match in MATCHES])
        + "]\n> "
    )
    if MATCH not in [match.removeprefix(str(current_year) + str(EVENT.lower()) + "_") for match in MATCHES]:
        print(cc("RED", "Invalid match."))
        exit()
    if MATCH == "all":
        requestEndpoint = "team/frc" + str(team_number) + "/event/" + str(current_year) + str(EVENT) + "/matches"

        print(cc("GRAY", "Getting team " + str(team_number) + " match list at: " + requestEndpoint))
        res = requests.get(api_endpoint + requestEndpoint + "?X-TBA-Auth-Key=" + constants.TBA_API_KEY).json()

        # Sort the matches by their keys using the natural_key function
        sorted_matches = sorted(res, key=lambda match: main.natural_key(match["key"]))

        print(cc("CYAN", "QUALIFICATION MATCHES"))
        for match in sorted_matches:
            if "_qm" in match["key"]:
                print("- " + match["key"] + main.get_alliance_str(match["alliances"]))
        print(cc("CYAN", "PLAYOFF MATCHES"))
        for match in sorted_matches:
            if "_sf" in match["key"]:
                print("- " + match["key"] + main.get_alliance_str(match["alliances"]))
        print(cc("CYAN", "FINAL MATCHES"))
        for match in sorted_matches:
            if "_f" in match["key"]:
                print("- " + match["key"] + main.get_alliance_str(match["alliances"]))
    else:
        requestEndpoint = "match/" + str(current_year) + str(EVENT) + "_" + MATCH

        print(cc("GRAY", "Getting match " + str(current_year) + str(EVENT) + "_" + MATCH + " at: " + requestEndpoint))
        res = requests.get(api_endpoint + requestEndpoint + "?X-TBA-Auth-Key=" + constants.TBA_API_KEY).json()

        print(cc("CYAN", f"AutoScout {'QUALIFICATIONS' if 'qm' in res['event_key'] else 'PLAYOFFS' if 'sf' in res['event_key'] else 'FINALS'} MATCH "
                 + str(res['match_number'])) + str(main.get_alliance_str(res["alliances"]).replace("frc", "")))
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
