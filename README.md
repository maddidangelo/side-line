# Side Line
### A plain-language betting literacy tool for people new to sports betting

## The problem

Sports betting content is written by and for people who already know the vocabulary. Odds, vig, parlays, implied probability — none of it is explained in a way that's accessible to someone placing their first bet, and most of the content that *does* exist is trying to sell picks, not build understanding.

This project is a data-driven tool that does the opposite: it never tells you what to bet. It teaches you to read the math yourself, so you can evaluate any bet critically — with a particular focus on making that math approachable for beginners and women, an audience that's often talked past rather than talked to in this space.

## What it does

**1. Odds Translator**
Converts American odds (`-150`, `+200`) into plain English: implied probability, and the break-even win rate you'd need to hit for the bet to pay off over time.

**2. Vig Revealer**
Takes both sides of a real matchup and shows that the implied probabilities always add up to *more* than 100% — visualizing exactly where the sportsbook's built-in profit margin (the "vig") is hiding.

**3. Parlay Reality Check**
Lets users stack multiple bets into a hypothetical parlay and watch the combined win probability collapse as legs are added — the gap between how safe a parlay *feels* and how safe it *is* is the single biggest misunderstanding new bettors have.

**4. Practice Betting Mode**
A virtual bankroll ($500 in practice dollars, no real money or signup) that lets users place bets on sample games at real odds and watch outcomes resolve. Rather than gamifying wins, the mode is built to surface the math beginners usually don't see in real time:
- A running **"vig paid"** counter, so the built-in house edge stops being an abstract concept and becomes a number that grows with every bet
- A **win rate vs. break-even rate** comparison, so users can see for themselves whether they're actually clearing the bar their odds required
- No streaks, no leaderboard, no push notifications, no framing of any outcome as a "win" worth repeating — the goal is to make the long-run math visible, not to make betting feel exciting

**5. (Planned) Historical Pattern Explorer**
Lets users query historical odds data for patterns — e.g., "how often do home underdogs of this size actually win?" — framed explicitly as education about *past* frequency, not a prediction of future outcomes.

## Design principles

- **No recommendations.** The tool explains odds; it never suggests a bet. This is a deliberate line — a tool that scores statistical "edges" and recommends action functions like a tipster service, which is the exact dynamic that leads new bettors to over-trust a number instead of their own judgment.
- **Plain language over jargon.** Every output is written the way you'd explain it to a friend, not the way a sportsbook displays it.
- **Grounded in real data**, not abstract examples — using live and historical odds makes the math concrete instead of theoretical.
- **Safe gambling is a visible, non-judgmental part of the design**, not a legal disclaimer buried in fine print. The National Council on Problem Gambling helpline (1-800-522-4700) is surfaced directly in the interface.
- **Practice betting is designed to teach, not to feel exciting.** Paper-trading tools work well for stocks, but betting is designed to feel thrilling regardless of long-run math — so the practice mode deliberately avoids streaks, leaderboards, and win-framing, and instead keeps the vig cost and break-even comparison visible on every bet, so the lesson (the math, not the feeling) stays front and center.

## Tech stack

- **Prototype (current):** Single-file HTML/CSS/vanilla JS — all odds math runs client-side, no backend needed to demo the core interaction
- **Data sources:**
  - [The Odds API](https://the-odds-api.com) — live sportsbook odds (free tier, 500 credits/month)
  - [Polymarket Gamma API](https://gamma-api.polymarket.com) — public prediction market prices, no key required
  - Kaggle historical odds datasets (e.g., [NFL scores and betting data](https://www.kaggle.com/datasets/tobycrabtree/nfl-scores-and-betting-data), [NBA Odds Data](https://www.kaggle.com/datasets/christophertreasure/nba-odds-data)) for the trend/pattern analysis
- **Planned:** Python backend (pandas for analysis) feeding a Streamlit app or this same HTML front end, so live/historical data replaces the hardcoded examples

## Files in this repo

| File | Purpose |
|---|---|
| `odds-literacy-tool.html` | Working prototype — odds translator, vig revealer, parlay checker |
| `prediction_market_vs_sportsbook.py` | Script pulling and comparing sportsbook odds vs. Polymarket prices |
| `README.md` | This file |

## Roadmap

- [x] Build a practice betting mode with virtual currency and vig tracking
- [ ] Connect the Historical Pattern Explorer to real Kaggle data
- [ ] Add a Brier score comparison between sportsbook and prediction market accuracy
- [ ] Build a simple, non-judgmental spending check-in feature
- [ ] Port to Streamlit or a lightweight Python backend for live data
- [ ] Replace sample games in practice mode with live odds from The Odds API
- [ ] User-test the language with people who have never placed a bet before

## Why this project

This started as a data analytics portfolio project and became something I actually care about: most tools in this space are built to keep people betting, not to help them understand what they're doing. This one is built the other way around — statistically rigorous, but designed to protect the user's judgment rather than replace it.
