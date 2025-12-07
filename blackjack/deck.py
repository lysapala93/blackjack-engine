from .card import Card, SUITS, RANKS
from random import shuffle, randint
from .logger import logger


class Deck:
    def __init__(self, deck_size: int = 6):
        self._deck_size: int = deck_size
        self._set_cutcard: bool = False
        self._pos_cutcard: int = None
        self._set_end_of_shoe: bool = False
        self._pos_end_of_shoe: int = None
        self._deck: list[Card] = []
        self._shuffled: bool = False
        self._end_game: bool = False

        self._deck = self._generate_deck()

    def _generate_deck(self):
        return [
            Card(suit, rank)
            for _ in range(self._deck_size)
            for suit in SUITS
            for rank in RANKS
        ]
