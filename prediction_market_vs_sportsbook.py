"""
Prediction Markets vs. Sportsbooks: Who predicts NFL games better?

This script pulls:
  1. Sportsbook odds (moneyline) from The Odds API
  2. Prediction market prices from Polymarket's Gamma API (NFL game-winner markets)

Then converts both to implied probabilities so they can be compared on the
same scale, and sets you up to score accuracy with a Brier score once you
have actual game outcomes.

SETUP:
  pip install requests pandas

  Get a free API key at https://the-odds-api.com and paste it below.
  Polymarket's Gamma API needs no key.
"""

import requests
import pandas as pd
from datetime import datetime

# ---------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------
ODDS_API_KEY = "YOUR_API_KEY_HERE"  # <-- paste your free key from the-odds-api.com
SPORT_KEY = "americanfootball_nfl"


# ---------------------------------------------------------------
# 1. PULL SPORTSBOOK ODDS (The Odds API)
# ---------------------------------------------------------------
def get_sportsbook_odds():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT_KEY}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "h2h",       # moneyline / head-to-head
        "oddsFormat": "american",
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    print(f"Odds API credits remaining: {resp.headers.get('x-requests-remaining')}")
    return resp.json()


def american_to_implied_prob(american_odds):
    """Convert American odds to implied probability (0-1)."""
    if american_odds > 0:
        return 100 / (american_odds + 100)
    else:
        return -american_odds / (-american_odds + 100)


def parse_sportsbook_odds(raw_games):
    """Flatten into one row per game, averaging implied prob across books."""
    rows = []
    for game in raw_games:
        home = game["home_team"]
        away = game["away_team"]
        commence = game["commence_time"]

        home_probs, away_probs = [], []
        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market["key"] != "h2h":
                    continue
                for outcome in market["outcomes"]:
                    prob = american_to_implied_prob(outcome["price"])
                    if outcome["name"] == home:
                        home_probs.append(prob)
                    elif outcome["name"] == away:
                        away_probs.append(prob)

        if home_probs and away_probs:
            rows.append({
                "home_team": home,
                "away_team": away,
                "commence_time": commence,
                "sportsbook_home_prob": sum(home_probs) / len(home_probs),
                "sportsbook_away_prob": sum(away_probs) / len(away_probs),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------
# 2. PULL PREDICTION MARKET PRICES (Polymarket Gamma API)
# ---------------------------------------------------------------
def get_polymarket_nfl_events():
    url = "https://gamma-api.polymarket.com/events"
    params = {
        "tag_slug": "nfl",
        "closed": "false",
        "limit": 50,
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


def parse_polymarket_events(events):
    """Pull out game-winner markets and their current 'Yes' price (= implied prob)."""
    rows = []
    for event in events:
        title = event.get("title", "")
        for market in event.get("markets", []):
            question = market.get("question", "")
            outcomes = market.get("outcomePrices")  # JSON string like '["0.62","0.38"]'
            if not outcomes:
                continue
            rows.append({
                "event_title": title,
                "market_question": question,
                "outcome_prices": outcomes,
                "end_date": market.get("endDate"),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------
# 3. RUN IT
# ---------------------------------------------------------------
if __name__ == "__main__":
    print("Pulling sportsbook odds...")
    raw_odds = get_sportsbook_odds()
    sportsbook_df = parse_sportsbook_odds(raw_odds)
    sportsbook_df.to_csv("sportsbook_odds.csv", index=False)
    print(f"Saved {len(sportsbook_df)} games to sportsbook_odds.csv")

    print("\nPulling Polymarket NFL markets...")
    raw_events = get_polymarket_nfl_events()
    polymarket_df = parse_polymarket_events(raw_events)
    polymarket_df.to_csv("polymarket_odds.csv", index=False)
    print(f"Saved {len(polymarket_df)} markets to polymarket_odds.csv")

    print("\nNext steps:")
    print("1. Open both CSVs and manually match games by team names / dates")
    print("   (team naming conventions differ between the two sources).")
    print("2. Once games finish, record the actual outcome (1 = home won, 0 = away won).")
    print("3. Compute Brier score for each source: mean((predicted_prob - actual)^2)")
    print("   Lower Brier score = better calibrated predictions.")
