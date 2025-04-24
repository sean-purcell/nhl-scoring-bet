import sys
import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict

# constants
START_DATE = sys.argv[1]
END_DATE = sys.argv[2]
TEAM_PICKS = {
    "Lovina": ["CAR", "COL", "EDM", "TOR", "WPG"],
    "Paul": ["CAR", "COL", "FLA", "TBL", "VGK"],
    "Sean": ["EDM", "FLA", "VGK", "WSH", "WPG"],
}

PLAYER_PICKS = {
    "Lovina": ["C. McDavid", "K. Connor", "L. Draisaitl", "N. Kucherov", "N. MacKinnon"],
    "Paul": ["B. Point", "C. Makar", "J. Eichel", "N. Kucherov", "N. MacKinnon"], 
    "Sean": ["C. McDavid", "J. Eichel", "K. Connor", "L. Draisaitl", "N. MacKinnon"],
}

TEAMS = set(team for picks in TEAM_PICKS.values() for team in picks)
PLAYERS = set(player for picks in PLAYER_PICKS.values() for player in picks)
SCHED_URL = "https://api-web.nhle.com/v1/schedule/{}"
GAME_URL = "https://api-web.nhle.com/v1/wsc/game-story/{}"
DATE_FORMAT = "%Y-%m-%d"

PDESC = {
    "1": "1st",
    "2": "2nd",
    "3": "3rd",
    "4": "OT",
    "5": "SO"
}

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
            scorer = goal.get("name", {}).get("default", "")
            assists = [assist.get("name", {}).get("default", "") for assist in goal.get("assists", [])]
            players = [(scorer, scorer in PLAYERS)] + [(assist, assist in PLAYERS) for assist in assists]
            
            if any(relevant for _, relevant in players):
                goals.append({
                    "period": PDESC[pnum],
                    "time": goal["timeInPeriod"],
                    "players": players,
                })

    away = story["awayTeam"]
    home = story["homeTeam"]
    def name(team):
        return team["name"]["default"]

    if "score" in away and "score" in home:
        scores = [away["score"], home["score"]]
    else:
        scores = None

    winner = None
    if story["gameState"] == "OFF":
        if scores[0] > scores[1]:
            winner = away["abbrev"]
        else:
            winner = home["abbrev"]

    return {
        "date": story["gameDate"],
        "id": game_id,
        "names": [name(away), name(home)],
        "abbrevs": [away["abbrev"], home["abbrev"]],
        "scores": scores,
        "goals": goals,
        "winner": winner,
    }

def main():
    dates = defaultdict(list)
    team_wins = defaultdict(int)
    player_points = defaultdict(int)
    games = []
    for game in relevant_game_ids():
        summary = game_summary(game)
        dates[summary["date"]].append(summary)
        winner = summary["winner"]
        if winner is not None:
            if winner in TEAMS:
                team_wins[winner] += 1
        for goal in summary["goals"]:
            for (player, relevant) in goal["players"]:
                if relevant:
                    player_points[player] += 1

    people = []
    for person in TEAM_PICKS:
        wins = sum(team_wins[team] for team in TEAM_PICKS[person])
        points = sum(player_points[player] for player in PLAYER_PICKS[person])
        people.append({"name": person, "wins": wins, "points": points, "total": 2*wins + points})

    output = {
        "games": list({ "date": date, "games": games} for (date, games) in sorted(dates.items())),
        "team_wins": list({"team": team, "wins": wins} for (team, wins) in sorted(team_wins.items())),
        "player_points": list({"player": player, "points": points} for (player, points) in sorted(player_points.items())),
        "people": people,
    }

    print(json.dumps(output))

if __name__ == "__main__":
    main()

