from blackjack import Card
from .logger import logger
from itertools import product


class Hand:
    """
    Represents a blackjack hand for a player or dealer.

    This class manages the cards in a hand, calculates the score, checks for
    blackjack or bust, and supports additional actions like splitting and revealing.
    It provides both internal game logic and "visible" methods for display purposes
    (e.g., showing the dealer's hand with hidden cards).

    Attributes:
        _owner_hand (str): Name of the hand owner. Always "dealer" for the dealer.
        _role (str): Role of the hand, either "player" or "dealer".
        _hand (list[Card]): List of current cards in the hand.
        _revealed (bool): Indicates whether the dealer's hand has been revealed.

    Properties:
        role (str): Role of the hand ("player" or "dealer").
        name (str): Name of the hand owner.
        score (int): Current blackjack score of the hand.
        visible_score (int | None): Score visible to the player (accounts for dealer's hidden card).
        hand (list[Card]): All cards in the hand.
        visible_hand (list[Card | None]): Cards visible to the player.
        blackjack (bool): True if the hand is a blackjack (21 with two cards).
        bust (bool): True if the score exceeds 21.
        splitting_possible (bool): True if the hand can be split (two cards of the same value).

    Methods:
        add(card: Card) -> None:
            Adds a card to the hand.

        discard() -> list[Card]:
            Empties the hand and returns the cards.

        split() -> tuple[Hand, Hand]:
            Splits the hand into two new hands, if possible.

        reveal() -> None:
            Reveals the dealer's hand.

    Magic Methods:
        __repr__() -> str:
            Detailed debug representation of the hand.

        __str__() -> str:
            Player-friendly string representation of the hand.

        __len__() -> int:
            Returns the number of cards in the hand.

        __contains__(card: Card) -> bool:
            Checks if a card is in the hand.

        __iter__():
            Iterates over the cards in the hand.

    Internal Methods:
        _calculate_score() -> int:
            Calculates the blackjack score of the hand, accounting for aces.
    """

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

    def split(self) -> tuple["Hand", "Hand"]:
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

    # ----------------------------------------------
    # Magic Methods
    # ----------------------------------------------

    def __repr__(self) -> str:
        cards_str = ", ".join(
            str(card) if card else "Hidden" for card in self.visible_hand
        )

        return f"<Hand(owner={self._name}, role={self._role}, cards=[{cards_str}], score={self.visible_score})>"

    def __str__(self) -> str:
        cards_str = ", ".join(str(card) for card in self.visible_hand if card)
        return f"{self._name}'s Hand: [{cards_str}] Score: {self.visible_score}"

    def __len__(self) -> int:
        return len(self._hand)

    def __contains__(self, card: Card) -> bool:
        return card in self._hand

    def __iter__(self):
        return iter(self._hand)
