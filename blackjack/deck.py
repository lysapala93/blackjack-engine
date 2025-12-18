from .card import Card, SUITS, RANKS
from .discard_tray import DiscardTray
from random import shuffle, randint
from .logger import logger


class Deck:
    def __init__(self, deck_size: int = 6):
        self._deck_size = deck_size
        self._deck = self._generate_deck()

        self._shuffled = False
        self._cut_position = None
        self._end_of_shoe_threshold = None
        self._end_game = False

        self._initial_cards = len(self._deck)

    # ---------------------------------------------
    # Deck generation
    # ---------------------------------------------
    def _generate_deck(self) -> list[Card]:
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
    def shuffled(self) -> bool:
        return self._shuffled

    @property
    def end_game(self) -> bool:
        return self._end_game

    # ---------------------------------------------
    # Core logic
    # ---------------------------------------------
    def draw(self) -> Card:
        if not self._deck:
            logger.error("Cannot draw from empty deck!")
            raise RuntimeError("Deck is empty")

        if not self._shuffled:
            logger.warning("Drawing from unshuffled deck!")

        card = self._deck.pop(0)

        # Check end of shoe
        if self._end_of_shoe_threshold is not None:
            if len(self) <= self._end_of_shoe_threshold:
                if not self._end_game:
                    logger.warning(
                        "End of shoe reached — reshuffle required after round."
                    )
                self._end_game = True

        return card

    def _reset(self) -> None:
        self._shuffled = False
        self._cut_position = None
        self._end_of_shoe_threshold = None
        self._end_game = False

        return None

    def collect_discard_pile(self, discard: list[Card]) -> None:
        self._deck.extend(discard)

        self._reset()

        return None

    # ---------------------------------------------
    # Shuffle mechanics
    # ---------------------------------------------
    def shuffle(self) -> None:
        shuffle(self._deck)
        self._shuffled = True
        logger.debug("Deck shuffled.")

    def set_cutcard(self, pos: int) -> str:
        if pos < 0 or pos >= len(self):
            raise ValueError("Cut position out of bounds.")

        # Realistic casino cut:
        # slice top -> bottom
        top = self._deck[:pos]
        bottom = self._deck[pos:]
        self._deck = bottom + top

        self._cut_position = pos
        logger.debug(f"Deck cut at position {pos}.")
        return "Deck cut."

    def set_end_of_shoe(self, remaining_min: int = 50, remaining_max: int = 80) -> None:
        self._end_of_shoe_threshold = randint(remaining_min, remaining_max)
        logger.debug(
            f"End-of-shoe marker set at last {self._end_of_shoe_threshold} cards."
        )
        return None

    # ----------------------------------------
    # Magic Methods
    # -----------------------------------------

    def __len__(self) -> int:
        return len(self._deck)

    def __repr__(self) -> str:
        shoe_size = (
            len(self) - self._end_of_shoe_threshold
            if self._end_of_shoe_threshold is not None
            else "not set"
        )
        return f"Deck(Number_of_Cards={len(self)}, shuffled={self.shuffled}, shoe_size={shoe_size})"

    def __str__(self) -> str:
        return self.__repr__()
