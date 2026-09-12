"""
Blackjack Simulator Package

Provides classes for simulating Blackjack games:
- Deck
- Hand
- Player
- Dealer
- Game
- DiscardTray
"""

# Expose main classes at the package level
from .card import Card
from .deck import Deck
from .hand import Hand
from .player_dealer import Player
from .player_dealer import Dealer
from .discard_tray import DiscardTray
from .game_orchestrator import Game, Phase, Action, RoundResult

__all__ = [
    "Card",
    "Deck",
    "Hand",
    "Player",
    "Dealer",
    "Game",
    "Phase",
    "Action",
    "RoundResult",
    "DiscardTray",
]
