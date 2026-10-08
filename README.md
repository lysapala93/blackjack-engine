# Blackjack Engine

A Python-based Blackjack simulation engine built as an explicit **phase state
machine**. The engine never blocks on `input()`/`print()` and never runs an
internal game loop — it only exposes a small, synchronous API
(`start`, `place_bet`, `current_actor`, `legal_actions`, `act`,
`last_round_results`). That means the exact same engine can be driven by:

- a human via the terminal (`blackjack/cli.py`), or
- a scripted agent / reinforcement-learning loop,

without any game logic being duplicated between the two.

## Features

- **Card & Deck Management**: Full card representation (suits, ranks, values, Ace as 1/11). Multi-deck shoe with realistic casino cut-card and end-of-shoe mechanics — the shoe is automatically reshuffled and re-cut once it runs low, mid-game, not just once at startup.
- **Hand Logic**: Score calculation with soft/hard Ace handling, blackjack/bust detection, split eligibility check, per-hand bet and stand state, and a `soft` property used for the dealer's soft-17 rule.
- **Player & Dealer**: Betting, budget/bankroll tracking, hit/stand, double down, split, and a configurable dealer rule (`hit_on_soft_17`). A participant holds a list of `hands` and plays them one at a time via `active_hand`.
- **Splitting**: Fully wired into the orchestrator — a player can hold several concurrent hands, each with its own bet. Configurable via `max_splittings` and `re_splitting`; split Aces automatically stand after one card, a 21 made from a split counts as a regular 21 (not a 3:2 blackjack), and each hand is settled separately.
- **Game Orchestrator**: A `Phase`/`Action` state machine that drives betting → dealing → player turns → dealer turns → payout → reshuffle automatically, only pausing when a player decision is required.
- **Insurance & Dealer Peek**: When the dealer shows an Ace (and `insurance=True`), each player may take insurance of up to half their bet (`Action.INSURANCE` for the maximum, `Action.DECLINE_INSURANCE`, or `game.take_insurance(player, amount)` for a custom amount). The dealer then peeks at the hole card when showing an Ace or a ten-value card: on blackjack the round ends immediately (insurance pays 2:1, a player blackjack pushes, everything else loses); otherwise insurance is forfeited and play continues.
- **Discard Tray**: Tracks discarded cards and feeds them back into the shoe on reshuffle.
- **CLI**: Playable terminal interface (`python blackjack.py`) built entirely on the public engine API.
- **Logging**: Structured logging for debugging and monitoring shoe/game state.

## Project Structure

```
blackjack-engine/
├── blackjack/
│   ├── card.py              # Card class: suit, rank, value
│   ├── deck.py               # Deck/shoe: shuffle, cut card, end-of-shoe, prepare_shoe()
│   ├── hand.py                # Hand: score, soft/bust/blackjack, per-hand bet, split
│   ├── player_dealer.py       # Participant base class (multi-hand) + Player and Dealer
│   ├── discard_tray.py        # Discarded-card tracking, feeds back into the shoe
│   ├── game_orchestrator.py   # Game (state machine), Phase, Action, RoundResult
│   ├── cli.py                 # Terminal interface, built on the Game API
│   ├── logger.py              # Logging configuration
│   └── __init__.py            # Package exports
├── tests/                     # Unit tests (pytest)
├── blackjack.py                # Entry point: `python blackjack.py` to play
├── pyproject.toml
└── README.md
```

## Installation

### Prerequisites
- Python 3.14+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Setup

```bash
git clone git@github.com:lysapala93/blackjack-engine.git
cd blackjack-engine

# with uv (installs deps into a managed venv automatically)
uv sync

# or with plain pip
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

## Playing interactively

```bash
# either of these:
python blackjack.py
uv run blackjack
```

You'll be prompted for player name(s) and a starting budget, then for the cut
card position of the new shoe. For each round you then enter a bet, followed by
hit/stand/double/split decisions (only the actions that are currently legal are
offered). If the dealer shows an Ace you are first asked whether to take
insurance (`i`) or not (`n`). If you split, each of your hands is played and shown separately. After
each round, results and updated budgets are printed and you're asked whether to
play another round.

## Using the engine programmatically

The engine is a state machine: call `start()`/`place_bet()`/`act()` and only
react when `current_actor` is not `None`.

```python
from blackjack import Game, Action

game = Game(
    players=["Alice", "Bob"],
    start_budget=1000,
    deck_size=6,
    hit_on_soft_17=False,
    max_splittings=3,     # max number of hands a player may end up with
    re_splitting=True,    # allow splitting an already-split hand again
    insurance=True,       # offer insurance when the dealer shows an Ace
)
game.start()

for player in game.players:
    game.place_bet(player, 50)          # dealing happens automatically once everyone has bet

while game.current_actor is not None:
    actor = game.current_actor
    hand = actor.active_hand            # the hand currently being played
    legal = game.legal_actions()        # e.g. [Action.HIT, Action.STAND, Action.DOUBLE, Action.SPLIT]
                                        # or [Action.INSURANCE, Action.DECLINE_INSURANCE] in Phase.INSURANCE
    game.act(Action.STAND if Action.STAND in legal else legal[0])

# dealer turn + payout already ran automatically; one result per hand
for result in game.last_round_results:
    print(result.player.name, result.hand_index, result.player_score, "->", result.net)
```

### Working with cards directly

```python
from blackjack import Card

card = Card("Hearts", "King")
print(card.suit, card.rank, card.value)   # Hearts King 10

ace = Card("Spades", "Ace")
print(ace.value)                          # (1, 11) — resolved by Hand scoring
```

## Testing

```bash
uv run pytest            # all tests
uv run pytest -v         # verbose
uv run pytest tests/test_game_orchestrator.py   # a single file
```

## Architecture

### Phase state machine (`game_orchestrator.py`)
`Game` moves through `Phase.BETTING → [Phase.INSURANCE →] [Phase.DEALER_PEEK →]
Phase.PLAYER_TURN → Phase.ROUND_END → Phase.BETTING`. The insurance phase only
occurs when the dealer shows an Ace; the peek happens for an Ace or ten-value
up-card and, if the dealer has blackjack, skips straight to payout. Only three calls are needed to drive it end to end:
`place_bet()`, `act()`, and reading `current_actor`/`legal_actions()` in
between. Dealing, the dealer's turn, payout, and shoe reshuffling all happen
automatically inside these calls — there is no hidden `while True` loop and
no blocking I/O anywhere in the engine, which is what makes it safe to drive
from an automated agent.

### Deck & shoe (`deck.py`)
`Deck.prepare_shoe()` shuffles, applies a cut card (random position by
default, casino-style top→bottom cut), and arms a random end-of-shoe
threshold (50–80 cards remaining) in one step. It's called once at
`Game.start()` and again automatically whenever the shoe is collected and
refilled from the discard tray — so reshuffling keeps working for the entire
session, not just before the first round.

### Hand (`hand.py`)
Calculates all possible Ace-adjusted totals and picks the best legal score.
Exposes `bust`, `blackjack`, `soft` (used for the dealer's optional
hit-on-soft-17 rule), `splitting_possible`, plus the per-hand `bet`,
`stand` and `from_split` state the orchestrator relies on when a player
holds several hands at once.

### Splitting (`player_dealer.py` + `game_orchestrator.py`)
`Hand.split()` returns two new hands (each flagged `from_split` and carrying
a copy of the original bet); `Participant.split()` replaces the active hand
with them in place and draws one card for each, so a player who splits again
keeps the hands they already hold. The orchestrator charges the extra wager,
caps the number of hands with `max_splittings`, honours `re_splitting`, and
auto-stands split Aces as well as any hand that reaches 21 or busts.
`current_actor` only advances to the next player once *all* of that player's
hands are finished, and payout settles every hand individually — producing
one `RoundResult` per hand, distinguished by `hand_index`.

## Dependencies

- **numpy** (≥2.3.5): declared dependency, currently unused by the engine — reserved for future statistics/simulation work.
- **pytest** (≥9.0.1): testing framework.

## License

MIT License — see [LICENSE](LICENSE) for details.

## Roadmap / Known limitations

- **Surrender**: not implemented.
- **Broke players in a multi-player game**: currently the whole session ends
  once any player can't afford the next bet, instead of sitting them out.
- **Reinforcement learning**: the engine's `current_actor` / `legal_actions()`
  / `act()` API is designed to be RL-friendly; a `Gymnasium`-style env
  wrapper and baseline agents (random / basic strategy) are the natural next
  layer on top.
- **Statistics**: card-counting / distribution statistics from the discard
  tray, and per-player win/loss tracking, are not implemented yet.
