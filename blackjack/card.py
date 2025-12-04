"""
card.py

This module defines the Card class used in the Blackjack Simulator. It includes
Informations about the card itself (color, value) and interprets also the value
of picture cards.
"""

from typing import Union, Tuple
from .logger import logger

SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]
VALUE = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "Jack": 10,
    "Queen": 10,
    "King": 10,
    "Ace": (1, 11),
}


