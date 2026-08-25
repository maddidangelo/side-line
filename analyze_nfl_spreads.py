"""
Clean spreadspoke_scores.csv and compute historical patterns:
  - How often favorites of different spread sizes actually cover
  - How often favorites (of any size) actually win outright
  - Home favorite vs. away favorite performance
  - Split by regular season vs. playoffs

Outputs a JSON file (nfl_patterns.json) that the Historical Pattern
Explorer tab in odds-literacy-tool can load and display.
"""

import pandas as pd
import numpy as np
import json

df = pd.read_csv("spreadspoke_scores.csv")

# ---------------------------------------------------------------
# 1. CLEAN
# ---------------------------------------------------------------

# Map every historical franchise name to the single abbreviation
# this dataset consistently uses for that franchise (it already
# back-fills relocations/renames onto one code).
TEAM_TO_ABBR = {
    "Arizona Cardinals": "ARI", "Phoenix Cardinals": "ARI", "St. Louis Cardinals": "ARI",
    "Atlanta Falcons": "ATL",
    "Baltimore Colts": "IND", "Indianapolis Colts": "IND",
    "Baltimore Ravens": "BAL",
    "Boston Patriots": "NE", "New England Patriots": "NE",
    "Buffalo Bills": "BUF",
    "Carolina Panthers": "CAR",
    "Chicago Bears": "CHI",
    "Cincinnati Bengals": "CIN",
    "Cleveland Browns": "CLE",
    "Dallas Cowboys": "DAL",
    "Denver Broncos": "DEN",
    "Detroit Lions": "DET",
    "Green Bay Packers": "GB",
    "Houston Oilers": "TEN", "Tennessee Oilers": "TEN", "Tennessee Titans": "TEN",
    "Houston Texans": "HOU",
    "Jacksonville Jaguars": "JAX",
    "Kansas City Chiefs": "KC",
    "Las Vegas Raiders": "LVR", "Los Angeles Raiders": "LVR", "Oakland Raiders": "LVR",
    "Los Angeles Chargers": "LAC", "San Diego Chargers": "LAC",
    "Los Angeles Rams": "LAR", "St. Louis Rams": "LAR",
    "Miami Dolphins": "MIA",
    "Minnesota Vikings": "MIN",
    "New Orleans Saints": "NO",
    "New York Giants": "NYG",
    "New York Jets": "NYJ",
    "Philadelphia Eagles": "PHI",
    "Pittsburgh Steelers": "PIT",
    "San Francisco 49ers": "SF",
    "Seattle Seahawks": "SEA",
    "Tampa Bay Buccaneers": "TB",
    "Washington Commanders": "WAS", "Washington Football Team": "WAS", "Washington Redskins": "WAS",
}

df["home_abbr"] = df["team_home"].map(TEAM_TO_ABBR)
df["away_abbr"] = df["team_away"].map(TEAM_TO_ABBR)

# Drop rows with no line (preseason data gaps, pick'em games, missing scores)
df = df.dropna(subset=["spread_favorite", "score_home", "score_away"])
df = df[df["team_favorite_id"] != "PICK"]

# Figure out whether the favorite was the home or away team
df["favorite_is_home"] = df["team_favorite_id"] == df["home_abbr"]
df["favorite_is_away"] = df["team_favorite_id"] == df["away_abbr"]
df = df[df["favorite_is_home"] | df["favorite_is_away"]]  # drop any unresolved rows

df["favorite_score"] = np.where(df["favorite_is_home"], df["score_home"], df["score_away"])
df["underdog_score"] = np.where(df["favorite_is_home"], df["score_away"], df["score_home"])
df["spread_abs"] = df["spread_favorite"].abs()

df["favorite_won"] = df["favorite_score"] > df["underdog_score"]
df["margin"] = df["favorite_score"] - df["underdog_score"]
df["favorite_covered"] = df["margin"] > df["spread_abs"]
df["push"] = df["margin"] == df["spread_abs"]

print(f"Cleaned dataset: {len(df)} games with valid spreads, {df['schedule_season'].min()}-{df['schedule_season'].max()}")

# ---------------------------------------------------------------
# 2. BUCKET BY SPREAD SIZE
# ---------------------------------------------------------------

bins = [0, 3, 6.5, 9.5, 13.5, 100]
labels = ["Pick'em (0.5–3)", "Small favorite (3.5–6.5)", "Moderate favorite (7–9.5)",
          "Large favorite (10–13.5)", "Heavy favorite (14+)"]
df["spread_bucket"] = pd.cut(df["spread_abs"], bins=bins, labels=labels, right=True)

bucket_stats = []
for label in labels:
    sub = df[df["spread_bucket"] == label]
    n = len(sub)
    if n == 0:
        continue
    win_rate = sub["favorite_won"].mean()
    cover_rate = sub["favorite_covered"].mean()
    bucket_stats.append({
        "bucket": label,
        "games": int(n),
        "favorite_win_rate": round(win_rate * 100, 1),
        "favorite_cover_rate": round(cover_rate * 100, 1),
    })

# ---------------------------------------------------------------
# 3. HOME VS AWAY FAVORITES
# ---------------------------------------------------------------

home_fav = df[df["favorite_is_home"]]
away_fav = df[df["favorite_is_away"]]

home_away_stats = {
    "home_favorite": {
        "games": int(len(home_fav)),
        "win_rate": round(home_fav["favorite_won"].mean() * 100, 1),
        "cover_rate": round(home_fav["favorite_covered"].mean() * 100, 1),
    },
    "away_favorite": {
        "games": int(len(away_fav)),
        "win_rate": round(away_fav["favorite_won"].mean() * 100, 1),
        "cover_rate": round(away_fav["favorite_covered"].mean() * 100, 1),
    },
}

# ---------------------------------------------------------------
# 4. REGULAR SEASON VS PLAYOFFS
# ---------------------------------------------------------------

reg = df[df["schedule_playoff"] == False]
playoffs = df[df["schedule_playoff"] == True]

season_type_stats = {
    "regular_season": {
        "games": int(len(reg)),
        "favorite_win_rate": round(reg["favorite_won"].mean() * 100, 1),
        "favorite_cover_rate": round(reg["favorite_covered"].mean() * 100, 1),
    },
    "playoffs": {
        "games": int(len(playoffs)),
        "favorite_win_rate": round(playoffs["favorite_won"].mean() * 100, 1),
        "favorite_cover_rate": round(playoffs["favorite_covered"].mean() * 100, 1),
    },
}

# ---------------------------------------------------------------
# 5. OVERALL SUMMARY
# ---------------------------------------------------------------

overall = {
    "total_games_analyzed": int(len(df)),
    "seasons_covered": f"{int(df['schedule_season'].min())}\u2013{int(df['schedule_season'].max())}",
    "favorite_win_rate_overall": round(df["favorite_won"].mean() * 100, 1),
    "favorite_cover_rate_overall": round(df["favorite_covered"].mean() * 100, 1),
    "push_rate": round(df["push"].mean() * 100, 1),
}

output = {
    "overall": overall,
    "by_spread_size": bucket_stats,
    "by_home_away": home_away_stats,
    "by_season_type": season_type_stats,
}

with open("nfl_patterns.json", "w") as f:
    json.dump(output, f, indent=2)

print(json.dumps(output, indent=2))
