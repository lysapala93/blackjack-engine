from blackjack import Deck
from blackjack import Card
from blackjack import DiscardTray


class TestDiscard:

    def test_show_discard():
        deck = Deck()
        deck.shuffle()
        deck.set_cutcard(pos=37)
        deck.set_end_of_shoe()

        discard_tray = DiscardTray()

        hand = (deck.draw(),)
        hand = hand + deck.draw()

        discard_tray.discard(hand)

        assert discard_tray == hand

    def test_get_number_cards():
        discard_tray = DiscardTray()
        discard_tray.discard(
            (
                Card(suit="Hearts", rank="King"),
                Card(suit="Diamonds", rank="10"),
                Card(suit="Hearts", rank="7"),
                Card(suit="Diamonds", rank="7"),
            )
        )

        assert discard_tray.num_cards == 4

    def test_reshuffle_to_deck():
        deck = Deck()
        deck.shuffle()
        deck.set_cutcard(pos=42)
        deck.set_end_of_shoe()
        num_cards_begin = deck.num_cards_begin

        discard_tray = DiscardTray()
        card = ()
        for _ in deck.num_cards:
            card = card + deck.draw()
            if deck.end_game == True:
                discard_tray.add_deck(deck)
                break

        assert discard_tray.num_cards == 0
        assert deck.num_cards == num_cards_begin
