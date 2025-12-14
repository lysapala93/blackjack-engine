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
from .player import Player
from .dealer import Dealer
from .game import Game
from .discard_tray import DiscardTray

__all__ = ["Card", "Deck", "Hand", "Player", "Dealer", "Game", "DiscardTray"]
