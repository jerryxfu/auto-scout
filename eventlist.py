import main
from cc import cc


def event_list(team_number: int, current_year: int):
    sorted_events = main.get_event_list(team_number, current_year)

    for event in sorted_events:
        print(
            f"- {event['name']} ({cc('GRAY', event['key'])}), {cc('FUCHSIA', event['city'])}, {cc('CYAN', event['country'])},"
            f" {cc('GREEN', event['start_date'])} to {cc('RED', event['end_date'])}"
        )
