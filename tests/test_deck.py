from blackjack import Deck
from blackjack import Card


class TestDeckBasic:
    def test_decksize(self):
        shoe = Deck(size=6)

        assert shoe.size == 6 * 52

    def test_draw(self):
        shoe = Deck(size=6)
        card = shoe.draw()

        assert type(card) == Card
        assert card.suit == "Hearts"
        assert card.rank == "2"
        assert shoe.size == (6 * 52) - 1

    def test_shuffle(self):
        shoe = Deck(size=6)
        shoe.shuffle()
        card = shoe.draw()

        assert card.suit != "Hearts"
        assert card.rank != "2"

    def test_cut_card(self):
        shoe = Deck(size=6)
        shoe.shuffle()
        card_before_cutcard_set = shoe.card[0]
        shoe.set_cutcard(pos=57)

        assert card_before_cutcard_set == shoe.card[-57]

    def test_end_of_shoe(self):
        shoe = Deck(size=6)
        shoe.shuffle()
        shoe.set_cutcard(pos=10)

        for _ in range(10):
            shoe.draw()

        assert shoe.size == 6 * 52
