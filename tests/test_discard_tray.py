from blackjack import Deck
from blackjack import Card
from blackjack import DiscardTray


class TestDiscard:

    def test_show_discard(self):
        deck = Deck()
        deck.shuffle()
        deck.set_cutcard(pos=37)
        deck.set_end_of_shoe()

        discard_tray = DiscardTray()

        hand = []
        hand.append(deck.draw())
        hand.append(deck.draw())

        discard_tray.discard(hand)

        assert discard_tray._discard_deck == hand

    def test_get_number_cards(self):
        discard_tray = DiscardTray()
        discard_tray.discard(
            [
                Card(suit="Hearts", rank="King"),
                Card(suit="Diamonds", rank="10"),
                Card(suit="Hearts", rank="7"),
                Card(suit="Diamonds", rank="7"),
            ]
        )

        assert len(discard_tray) == 4

    def test_reshuffle_to_deck(self):
        deck = Deck()
        deck.shuffle()
        deck.set_cutcard(pos=42)
        deck.set_end_of_shoe()
        num_cards_begin = len(deck)

        discard_tray = DiscardTray()
        card = list()
        for _ in range(len(deck)):
            card.append(deck.draw())
            discard_tray.discard(card)
            card.clear()
            if deck.end_game == True:
                cards = discard_tray.reset()
                deck.collect_discard_pile(cards)
                break

        assert len(discard_tray) == 0
        assert len(deck) == num_cards_begin
