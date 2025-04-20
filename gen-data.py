import sys
import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict

# Constants
START_DATE = sys.argv[1]
END_DATE = sys.argv[2]
TEAM_PICKS = {
    "Sean": ["WPG", "VGK", "EDM", "WSH", "FLA"],
    "Paul": ["TBL", "CAR", "VGK", "COL", "FLA"], 
    "Lovina": ["EDM", "TOR", "COL", "WPG", "CAR"]
}

PLAYER_PICKS = {
    "Sean": ["C. McDavid", "L. Draisaitl", "N. MacKinnon", "K. Connor", "J. Eichel"],
    "Paul": ["N. Kucherov", "B. Point", "J. Eichel", "N. MacKinnon", "C. Makar"],
    "Lovina": ["C. McDavid", "N. MacKinnon", "L. Draisaitl", "K. Connor", "N. Kucherov"]
}

TEAMS = set(team for picks in TEAM_PICKS.values() for team in picks)
PLAYERS = set(player for picks in PLAYER_PICKS.values() for player in picks)
SCHED_URL = "https://api-web.nhle.com/v1/schedule/{}"
GAME_URL = "https://api-web.nhle.com/v1/wsc/game-story/{}"
DATE_FORMAT = "%Y-%m-%d"

def fetch(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise f"Error fetching data for {url}: {response.status_code}"

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
        for goal in period.get("goals", []):
            print(goal)
            name = goal.get("name", {}).get("default", "")
            if name in PLAYERS:
                goals.append({"period": PDESC[pnum], "time": goal["timeInPeriod"], "player": name, "goalsToDate": goal.get("goalsToDate")})

    away = story["awayTeam"]
    home = story["homeTeam"]
    def name(team):
        return team["name"]["default"]

    if "score" in away and "score" in home:
        scores = [away["score"], home["score"]]
    else:
        scores = None

    return {
        "date": story["gameDate"],
        "id": game_id,
        "names": [name(away), name(home)],
        "abbrevs": [away["abbrev"], home["abbrev"]],
        "scores": scores,
        "goals": goals
    }

def main():
    games = relevant_game_ids()
    dates = defaultdict(list)
    for game in relevant_game_ids():
        summary = game_summary(game)
        dates[summary["date"]].append(summary)

    gamesPlayed = { team: 0 for team in TEAMS }
    result = []
    for (date, games) in sorted(dates.items()):
        for game in games:
            for team in TEAMS:
                if team in game["abbrevs"]:
                    gamesPlayed[team] += 1
        played = list(gamesPlayed.items())
        result.append({"date": date, "played": played, "games": games})
        started = any(x["scores"] is not None for x in games)
        if not started:
            break
    print(json.dumps(result))

if __name__ == "__main__":
    main()

