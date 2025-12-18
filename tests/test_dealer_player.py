from blackjack import Dealer, Player, Deck, Card
from random import randint


class TestDealer:
    def test_hit(self):
        deck = Deck()

        dealer = Dealer()
        for _ in range(2):
            dealer.hit(deck)

        assert len(dealer.hand) == 2
        assert dealer.hand.hand == [
            Card(suit="Hearts", rank="2"),
            Card(suit="Hearts", rank="3"),
        ]

    def test_stand(self):
        deck = Deck()

        dealer = Dealer()
        dealer.hit(deck)
        dealer.stand()

        assert dealer.standing is True


class TestPlayer:
    def test_bet(self):
        deck = Deck()
        deck.shuffle()
        deck.set_cutcard(randint(0, len(deck)))
        deck.set_end_of_shoe()

        player = Player(budget=10000, name="Ocean")
        bet = player.bet(amout=500)

        assert player.budget == 9500
        assert bet == 500

    def test_hit(self):
        deck = Deck()

        player = Player(budget=10000, name="Ocean")
        for _ in range(2):
            player.hit(deck)

        assert player.hand.hand == [
            Card(suit="Hearts", rank="2"),
            Card(suit="Hearts", rank="3"),
        ]

    def test_stay(self):
        deck = Deck()

        player = Player(budget=10000, name="Ocean")
        for _ in range(2):
            player.hit(deck)
        player.stand()

        assert player.standing is True
