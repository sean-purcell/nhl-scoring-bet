import sys
import requests
import json
from datetime import datetime, timedelta

# Constants
START_DATE = sys.argv[1]
END_DATE = sys.argv[2]
TEAMS = ["TOR", "FLA", "EDM"]
PLAYERS = ["W. Nylander", "S. Reinhart", "L. Draisaitl" ]
SCHED_URL = "https://api-web.nhle.com/v1/schedule/{}"
GAME_URL = "https://api-web.nhle.com/v1/wsc/game-story/{}"
DATE_FORMAT = "%Y-%m-%d"

def fetch(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise f"Error fetching data for {date}: {response.status_code}"

def filter_games_by_teams(schedule, teams):
    """Filter games involving specific teams."""
    game_ids = []
    for game_day in schedule.get("gameWeek", []):
        for game in game_day.get("games", []):
            home_team = game["homeTeam"]["abbrev"]
            away_team = game["awayTeam"]["abbrev"]
            if any(team in (home_team, away_team) for team in teams):
                game_ids.append(game["id"])
    return game_ids

def relevant_game_ids():
    current_date = datetime.strptime(START_DATE, DATE_FORMAT)
    end_date = datetime.strptime(END_DATE, DATE_FORMAT)
    all_game_ids = []

    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        schedule = fetch(SCHED_URL.format(date_str))
        if schedule:
            game_ids = filter_games_by_teams(schedule, TEAMS)
            all_game_ids.extend(game_ids)
        current_date = datetime.strptime(schedule.get("nextStartDate"), DATE_FORMAT)

    return all_game_ids

def game_summary(game_id):
    story = fetch(GAME_URL.format(game_id))

    goals = []

    for period in story.get("summary", {}).get("scoring", []):
        pnum = str(period["periodDescriptor"]["number"])
        if pnum == "4":
            pnum = "OT"
        for goal in period.get("goals", []):
            name = goal.get("name", {}).get("default", "")
            if name in PLAYERS:
                goals.append({"period": pnum, "time": goal["timeInPeriod"], "player": name})

    away = story["awayTeam"]
    home = story["homeTeam"]
    return {
        "date": story["gameDate"],
        "away": away["name"]["default"],
        "home": home["name"]["default"],
        "awayScore": away.get("score"),
        "homeScore": home.get("score"),
        "goals": goals
    }

def main():
    games = relevant_game_ids()
    for game in relevant_game_ids():
        summary = game_summary(game)
        print(json.dumps(summary))

if __name__ == "__main__":
    main()
