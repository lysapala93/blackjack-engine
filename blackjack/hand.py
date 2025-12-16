from blackjack import Card
from .logger import logger
from itertools import product


class Hand:

    def __init__(self, role: str, name: str = None):

        match role:
            case "player":
                self._owner_hand: str = name

            case "dealer":
                self._owner_hand: str = "dealer"

            case _:
                raise ValueError(f'Unknown role "{role}", please use player or dealer')

        self._role = role
        self._hand: list[Card] = []

    # -----------------------------------------------
    # properties
    # -----------------------------------------------
    @property
    def role(self) -> str:
        return self._role

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name) -> None:
        self._name = name

        return None

    @property
    def score(self) -> int:
        if not self._hand:
            return 0

        values = [
            list(card.value) if isinstance(card.value, tuple) else [card.value]
            for card in self._hand
        ]

        possible_scores = {sum(combo) for combo in product(*values)}
        valid_scores = [s for s in possible_scores if s <= 21]

        return max(valid_scores) if valid_scores else min(possible_scores)
