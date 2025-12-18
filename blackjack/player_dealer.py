from abc import ABC, abstractmethod
from blackjack import Hand, Deck


class Participiant(ABC):

    def __init__(self, role: str, name: str | None = None):
        self._role: str = role
        self._standing: bool = False
        self._hand: Hand = Hand(self._role)
        self._name: str = self._hand.name

    @abstractmethod
    def hit(self, deck: "Deck") -> "Deck":
        pass

    @abstractmethod
    def stand(self) -> None:
        pass

    @property
    @abstractmethod
    def role(self) -> str:
        pass

    @property
    @abstractmethod
    def standing(self) -> None:
        pass

    @property
    @abstractmethod
    def hand(self) -> "Hand":
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class Dealer(Participiant):

    def __init__(self):
        super().__init__(role="dealer")

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


class Player(Participiant):
    def __init__(self, name: str, starting_budget: int):
        super().__init__(role="player", name=name)
        self._budget: int = starting_budget
