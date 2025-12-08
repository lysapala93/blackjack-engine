from .card import Card, SUITS, RANKS
from random import shuffle, randint
from .logger import logger


class Deck:
    def __init__(self, deck_size: int = 6):
        self._deck_size = deck_size
        self._deck = self._generate_deck()

        self._shuffled = False
        self._cut_position = None
        self._end_of_shoe_position = None
        self._end_game = False

        self._initial_cards = len(self._deck)

        return [
            Card(suit, rank)
            for _ in range(self._deck_size)
            for suit in SUITS
            for rank in RANKS
        ]

    # ---------------------------------------------
    # Properties
    # ---------------------------------------------
    @property
    def num_cards(self) -> int:
        return len(self._deck)

    @property
    def shuffled(self) -> bool:
        return self._shuffled

    @property
    def end_game(self) -> bool:
        return self._end_game

    def needs_shuffle(self) -> bool:
        if not self._set_end_of_shoe:
            return False

        if self.num_cards <= (52 * 6 - self._pos_end_of_shoe):
            self._end_game = True

            return True

    def draw(self) -> Card:
        if not self._deck:
            logger.error("Cannot draw from empty deck!")
            raise RuntimeError("Deck is empty")

        if not self._shuffled:
            logger.warning("Drawing from unshuffled deck!")

        card = self._deck.pop(0)

        # Check end of shoe
        if self._end_of_shoe_position is not None:
            if self.num_cards <= self._end_of_shoe_position:
                if not self._end_game:
                    logger.warning(
                        "End of shoe reached — reshuffle required after round."
                    )
                self._end_game = True

        return card

    def shuffle(self) -> str:
        shuffle(self._deck)
        self._shuffled = True
        logger.debug("Deck was shuffled successfully")
        logger.debug(f"Order of cards: {self._deck}")

        return f"Deck is shuffled"

    def set_cutcard(self, pos: int):
        if pos < 0 or pos >= self.num_cards:
            raise ValueError("Cut position out of bounds.")

        # Realistic casino cut:
        # slice top -> bottom
        top = self._deck[:pos]
        bottom = self._deck[pos:]
        self._deck = bottom + top

        self._cut_position = pos
        logger.debug(f"Deck cut at position {pos}.")
        return "Deck cut."

    def set_end_of_shoe(self, remaining_min: int = 50, remaining_max: int = 80):
        self._end_of_shoe_position = randint(remaining_min, remaining_max)
        logger.debug(
            f"End-of-shoe marker set at last {self._end_of_shoe_position} cards."
        )
        return None
