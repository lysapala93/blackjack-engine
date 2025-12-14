from .card import Card
from typing import Union


class DiscardTray:
    def __init__(self):
        self._discard_deck: list[Card] = []

    def discard(self, cards: list[Card] | Card):
        if isinstance(cards, list):
            self._discard_deck.extend(cards)
        elif isinstance(cards, Card):
            self._discard_deck.append(cards)
        else:
            raise ValueError(
                f"Get type {type(cards)}, but expected is a list of Cards or a Card object"
            )

        return None

    def reset(self):
        cards = self._discard_deck.copy()
        self._discard_deck.clear()

        return cards

    def __len__(self):
        return len(self._discard_deck)

    def __repr__(self):
        return f"DiscardTray(len({len(self)}))"
