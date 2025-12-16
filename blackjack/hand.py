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
