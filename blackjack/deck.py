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

    @property
    def num_cards(self) -> int:
        return len(self._deck)

    @property
    def deck_size(self) -> int:
        return self._deck_size

    @property
    def set_cutcard(self) -> bool:
        return self._set_cutcard

    @property
    def set_end_of_shoe(self) -> bool:
        return self._set_end_of_shoe

    @property
    def shuffled(self) -> bool:
        return self._shuffled

    @property
    def finished_round(self) -> bool:
        return self._end_game

    def draw(self) -> Card:
        if not self._deck:
            logger.error("Cannot draw from empty deck.")
            raise RuntimeError("Deck is empty")

        if not self._shuffled:
            logger.warning("Drawing from an unshuffled deck!")

        card = self._deck.pop(0)

        if self.needs_shuffle:
            logger.warning("End of shoe reached – reshuffle required after this round")

        return card

