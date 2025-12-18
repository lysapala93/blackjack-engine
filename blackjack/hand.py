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
        self._revealed: bool = False

    # -----------------------------------------------
    # properties
    # -----------------------------------------------
    @property
    def role(self) -> str:
        return self._role

    @property
    def name(self) -> str:
        return self._owner_hand

    @name.setter
    def name(self, name) -> None:
        self._owner_hand = name

        return None

    @property
    def score(self) -> int:
        if not self._hand:
            return 0

        return self._calculate_score()

    @property
    def visible_score(self) -> int | None:
        if self.role == "dealer" and not self._revealed:
            if not self._hand:
                return 0
            value = self._hand[0].value
            return min(value) if isinstance(value, tuple) else value

        return self.score

    @property
    def hand(self) -> list[Card]:
        return self._hand

    @property
    def visible_hand(self) -> list[Card | None]:
        if self._role == "dealer" and not self._revealed:
            if not self._hand:
                return []
            return [self._hand[0], None]
        else:
            return self._hand

    @property
    def blackjack(self):
        return len(self.hand) == 2 and self.score == 21

    @property
    def bust(self):
        return self.score > 21

    @property
    def splitting_possible(self) -> bool:
        return (
            len(self.hand) == 2
            and self.hand[0].value == self.hand[1].value
            and self.role == "player"
        )

    # ----------------------------------------------
    # functions
    # ----------------------------------------------
    def add(self, card: Card) -> None:
        self._hand.append(card)

        return None

    def discard(self) -> None:
        cards = self._hand.copy()
        self._hand.clear()

        return cards

    def split(self):
        if not self.splitting_possible:
            raise ValueError(f"Splitting with hand {self.hand} not possible")

        hand_1 = Hand(role="player", name=self._owner_hand)
        hand_2 = Hand(role="player", name=self._owner_hand)

        hand_1.add(self._hand[0])
        hand_2.add(self._hand[1])

        self._hand.clear()

        return hand_1, hand_2

    def reveal(self) -> None:
        self._revealed = True

    def _calculate_score(self) -> int:
        values = [
            list(card.value) if isinstance(card.value, tuple) else [card.value]
            for card in self._hand
        ]
        possible_scores = {sum(combo) for combo in product(*values)}
        valid_scores = [s for s in possible_scores if s <= 21]

        return max(valid_scores) if valid_scores else min(possible_scores)
