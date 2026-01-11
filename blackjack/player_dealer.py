from abc import ABC, abstractmethod
from blackjack import Hand, Deck


class Participiant(ABC):

    def __init__(self, role: str, name: str | None = None):
        self._role: str = role
        self._standing: bool = False
        self._hand: Hand = Hand(self._role, name)
        self._name: str = self._hand.name

    def hit(self, deck: "Deck") -> None:
        card = deck.draw()
        self._hand.add(card)

    def stand(self) -> None:
        self._standing = True

    @property
    def role(self) -> str:
        return self._role

    @property
    def standing(self) -> bool:
        return self._standing

    @property
    def hand(self) -> "Hand":
        return self._hand

    @property
    def name(self) -> str:
        return self._name


class Dealer(Participiant):

    def __init__(self):
        super().__init__(role="dealer")


class Player(Participiant):
    def __init__(self, name: str, starting_budget: int):
        super().__init__(role="player", name=name)
        self._budget: int = starting_budget

    def bet(self, amount: int) -> int:
        self._budget -= amount

        return amount

    @property
    def budget(self) -> int:
        return self._budget
