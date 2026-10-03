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
        self._name: str = name
        self._hands: list[Hand] = [Hand(role)]
        self._active_hand: int = 0

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
        self.active_hand.add(card)

    def stand(self) -> None:
        """
        Sets the participant's status to stand (no more cards will be drawn).
        """
        self.active_hand.stand = True
        self._advance_active_hand()

    def split(self, deck: Deck) -> None:
        """
        Splits the active hand into two hands and draws a new card for each.

        The two new hands replace the active hand in place, so a player who
        splits again later keeps the hands they already hold.

        Args:
            deck (Deck): The deck from which the card is drawn.
        """
        new_hands = list(self.active_hand.split())
        self._hands[self._active_hand : self._active_hand + 1] = new_hands

        for hand in new_hands:
            hand.add(deck.draw())

    def reset_for_new_round(self) -> None:
        """Clears turn-taking state so the participant can act again next round."""
        self._standing = False

    # ---------------------------------------------#
    # Getters                                     #
    # ---------------------------------------------#

    @property
    def role(self) -> str:
        """Returns the role of the participant."""
        return self._role

    @property
    def standing(self) -> bool:
        """Returns whether every hand of the participant is finished."""
        return all(hand.stand for hand in self._hands)

    @property
    def hands(self) -> list[Hand]:
        """Returns all hands of the participant."""
        return self._hands

    @property
    def active_hand(self) -> Hand:
        """Returns the active hand"""
        return self._hands[self._active_hand]

    @property
    def name(self) -> str:
        """Returns the participant's name."""
        return self._name

    @active_hand.setter
    def active_hand(self, hand: int) -> None:
        """Setter for the active hand."""
        self._active_hand = hand


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

    def __repr__(self) -> str:
        return f"<Participant(Role={self.role}, Hand={self.active_hand})>"


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

    def place_bet(self, amount: int) -> None:
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
        self.active_hand.bet += amount

    @property
    def budget(self) -> int:
        """Returns the player's current budget."""
        return self._budget

    def charge(self, amount: int) -> None:
        """
        Charges the budget of the player without touching any hand's bet.

        Used for follow-up wagers (e.g. the second hand of a split) where the
        bet has already been recorded on the hand itself.

        Args:
            amount (int): The amount to be charged. Must be >= 0.

        Raises:
            ValueError: If the amount is negative or exceeds the player's budget.
        """
        if amount < 0:
            raise ValueError("Charged amount must be >= 0")
        if amount > self._budget:
            raise ValueError("Not enough budget to cover this charge")
        self._budget -= amount
        logger.debug(
            f"Budget was charged by the amount of {amount} (before: {self._budget+amount}; now: {self.budget})"
        )

    def add_winnings(self, amount: int) -> None:
        """
        Credits the player's budget with payout winnings (or a returned push/bet).

        Args:
            amount (int): The amount to credit. Must be >= 0.
        """
        if amount < 0:
            raise ValueError("Winnings amount must be >= 0")
        self._budget += amount

    def __repr__(self):
        return f"<Participant(Name={self._name}, Role={self._role}, Budget={self._budget} Hand={self._hand})>"
