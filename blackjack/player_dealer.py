from __future__ import annotations
from abc import ABC, abstractmethod
from blackjack import Hand, Deck


class Participant(ABC):
    """
    Base class for all participants in a Blackjack game.

    Attributes:
        _role (str): The participant's role (e.g., "dealer", "player").
        _standing (bool): Indicates whether the participant has chosen to stand.
        _hand (Hand): The participant's hand.
        _name (str): The participant's name.
    """

    def __init__(self, role: str, name: str | None = None):
        """
        Initializes a participant with a role and an optional name.

        Args:
            role (str): The role of the participant.
            name (str | None): Optional name of the participant.
        """
        self._role: str = role
        self._standing: bool = False
        self._hand: Hand = Hand(role, name)
        self._name: str = self._hand.name

    # ---------------------------------------------#
    # Core Mechanisms                             #
    # ---------------------------------------------#

    def hit(self, deck: Deck) -> None:
        """
        Draws a card from the deck and adds it to the participant's hand.

        Args:
            deck (Deck): The deck from which the card is drawn.
        """
        card = deck.draw()
        self._hand.add(card)

    def stand(self) -> None:
        """
        Sets the participant's status to stand (no more cards will be drawn).
        """
        self._standing = True

    # ---------------------------------------------#
    # Getters                                     #
    # ---------------------------------------------#

    @property
    def role(self) -> str:
        """Returns the role of the participant."""
        return self._role

    @property
    def standing(self) -> bool:
        """Returns whether the participant has chosen to stand."""
        return self._standing

    @property
    def hand(self) -> Hand:
        """Returns the participant's hand."""
        return self._hand

    @property
    def name(self) -> str:
        """Returns the participant's name."""
        return self._name

    # ---------------------------------------------#
    # Magic Methods                               #
    # ---------------------------------------------#

    def __repr__(self) -> str:
        if self._role == "dealer":
            return f"<Participant(Role={self._role}, Hand={self.hand})>"


class Dealer(Participant):
    """
    Dealer class for the Blackjack game.
    Inherits from Participant.
    """

    def __init__(self):
        """
        Initializes a dealer with the role 'dealer'.
        """
        super().__init__(role="dealer")


class Player(Participant):
    """
    Player class for the Blackjack game.
    Inherits from Participant and manages the player's budget.
    """

    def __init__(self, name: str, starting_budget: int):
        """
        Initializes a player with a name and starting budget.

        Args:
            name (str): The player's name.
            starting_budget (int): The player's starting budget.
        """
        super().__init__(role="player", name=name)
        self._budget: int = starting_budget

    def place_bet(self, amount: int) -> int:
        """
        Places a bet and reduces the player's budget accordingly.

        Args:
            amount (int): The amount to bet.

        Returns:
            int: The amount placed in the pot.

        Raises:
            ValueError: If the amount is <= 0 or exceeds the player's budget.
        """
        if amount <= 0:
            raise ValueError("Bet amount must be greater than zero")
        if amount > self._budget:
            raise ValueError("Not enough budget to place this bet")

        self._budget -= amount
        return amount

    @property
    def budget(self) -> int:
        """Returns the player's current budget."""
        return self._budget

    def __repr__(self):
        return super().__repr__()
