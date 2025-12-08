from blackjack import Deck
from blackjack import Card


class TestDeckBasic:
    def test_decksize(self):
        shoe = Deck(deck_size=6)

        assert shoe.num_cards == 6 * 52

    def test_first_card(self):
        shoe = Deck(deck_size=6)

        assert shoe._deck[0] == Card("Hearts", "2")

    def test_draw(self):
        shoe = Deck(deck_size=6)
        card = shoe.draw()

        assert type(card) == Card
        assert card.suit == "Hearts"
        assert card.rank == "2"
        assert shoe.num_cards == (6 * 52) - 1

    def test_shuffle(self):
        shoe = Deck(deck_size=6)
        shoe.shuffle()
        card = shoe.draw()

        assert card.suit != "Hearts"
        assert card.rank != "2"

    def test_cut_card(self):
        shoe = Deck(deck_size=6)
        shoe.shuffle()
        card_before_cutcard_set = shoe._deck[0]
        shoe.set_cutcard(pos=57)

        assert card_before_cutcard_set == shoe._deck[-57]

    def test_end_of_shoe(self):
        shoe = Deck(deck_size=6)
        shoe.shuffle()
        shoe.set_end_of_shoe()

        for _ in range(shoe._pos_end_of_shoe):
            shoe.draw()

        assert shoe.needs_shuffle() == True
