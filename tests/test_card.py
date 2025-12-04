from blackjack import Card
import pytest


class TestCardBasic:
    def test_set_card(self):
        card = Card(suit="Clubs", rank="Jack")

        assert card.suit == "Clubs"
        assert card.rank == "Jack"
        assert card.value == 10

    def test_str(self):
        card = Card(suit="Diamonds", rank="8")

        assert str(card) == "8 of Diamonds"
        assert repr(card) == "Card(rank=8, suit=Diamonds)"

    def test_error(self):
        with pytest.raises(ValueError):
            Card(suit="Clubz", rank="Jack")

    def test_pictures(self):
        pictures = ["Jack", "Queen", "King"]
        for picture in pictures:
            assert Card(suit="Hearts", rank=picture).value == 10

    def test_all_combinations(self):
        from blackjack.card import SUITS, RANKS

        for suit in SUITS:
            for rank in RANKS:
                card = Card(suit=suit, rank=rank)
                assert card.suit == suit
                assert card.rank == rank


class TestCardAce:
    def test_callback(self):
        card = Card(suit="Hearts", rank="Ace")

        assert card.suit == "Hearts"
        assert card.rank == "Ace"
        assert card.value == (1, 11)
