from blackjack import Hand
from blackjack import Card
from blackjack import Deck
from blackjack import DiscardTray
import pytest


class TestHand:
    def test_role(self):
        hand_player = Hand(role="player", name="Ocean")
        hand_dealer = Hand(role="dealer")

        assert hand_player.role == "player"
        assert hand_dealer.role == "dealer"

    def test_role_negative(self):
        with pytest.raises(
            ValueError, match=r'Unknown role "superman", please use player or dealer'
        ):
            Hand(role="superman", name="Batman")

    def test_value_hand(self):
        hand_player = Hand(role="player", name="Ocean")
        cards = [Card(suit="Spades", rank="7"), Card(suit="Hearts", rank="Jack")]
        for card in cards:
            hand_player.add(card)

        assert hand_player.score == 17

    def test_draw_from_deck(self):
        hand_player = Hand(role="player", name="Ocean")
        deck = Deck()

        deck.shuffle()
        initial_size = len(deck)
        deck.draw()

        hand_player.add(deck.draw())
        hand_player.add(deck.draw())

        assert len(deck) == initial_size - 3

    def test_ace_value(self):
        hand_player = Hand(role="player", name="Ocean")
        cards = [Card(suit="Spades", rank="7"), Card(suit="Spades", rank="Ace")]

        for card in cards:
            hand_player.add(card)
        score_before = hand_player.score
        hand_player.add(Card(suit="Hearts", rank="4"))
        score_after = hand_player.score

        assert score_before == 18
        assert score_after == 12

    def test_blackjack(self):
        hand_player = Hand(role="player", name="Ocean")
        cards = [Card(suit="Spades", rank="Jack"), Card(suit="Spades", rank="Ace")]

        for card in cards:
            hand_player.add(card)

        assert hand_player.blackjack
        assert not hand_player.bust

    def test_twentyone(self):
        hand_player = Hand(role="player", name="Ocean")
        cards = [
            Card(suit="Spades", rank="Jack"),
            Card(suit="Spades", rank="9"),
            Card(suit="Hearts", rank="2"),
        ]

        for card in cards:
            hand_player.add(card)

        assert not hand_player.blackjack
        assert not hand_player.bust
        assert hand_player.score == 21

    def test_bust(self):
        hand_player = Hand(role="player", name="Ocean")
        cards = [
            Card(suit="Spades", rank="Jack"),
            Card(suit="Spades", rank="9"),
            Card(suit="Hearts", rank="3"),
        ]

        for card in cards:
            hand_player.add(card)

        assert not hand_player.blackjack
        assert hand_player.bust

    def test_discard(self):
        hand_player = Hand(role="player", name="Ocean")
        deck = Deck()
        discard_tray = DiscardTray()

        deck.shuffle()
        initial_size = len(deck)
        first_discard = deck.draw()
        discard_tray.discard(first_discard)
        hand_player.add(deck.draw())
        hand_player.add(deck.draw())

        hand_player_cards = hand_player.hand.copy()

        discard_tray.discard(hand_player.discard())

        assert len(deck) == initial_size - 3
        assert len(discard_tray) == 3
        assert all(
            hand_player_card in discard_tray._discard_deck
            for hand_player_card in hand_player_cards
        )
        assert first_discard in discard_tray._discard_deck
        assert hand_player.score == 0
        assert not hand_player.blackjack
        assert not hand_player.bust


class TestHandPlayer:
    def test_hand(self):
        hand_player = Hand(role="player", name="Ocean")
        cards = [Card(suit="Spades", rank="7"), Card(suit="Hearts", rank="Ace")]
        for card in cards:
            hand_player.add(card)

        assert hand_player.hand == cards

    def test_split(self):
        hand_player = Hand(role="player", name="Ocean")
        cards = [Card(suit="Spades", rank="10"), Card(suit="Hearts", rank="Jack")]
        for card in cards:
            hand_player.add(card)

        assert hand_player.splitting_possible

        hand_1, hand_2 = hand_player.split()

        assert Card(suit="Spades", rank="10") in hand_1.hand
        assert Card(suit="Hearts", rank="Jack") in hand_2.hand
        assert hand_player.hand == []


class TestHandDealer:
    def test_hand(self):
        hand_dealer = Hand(role="dealer")
        cards = [Card(suit="Spades", rank="Jack"), Card(suit="Spades", rank="Ace")]
        for card in cards:
            hand_dealer.add(card)

        assert hand_dealer.hand == [Card(suit="Spades", rank="Jack"), "hidden"]

    def test_hand_revealed(self):
        hand_dealer = Hand(role="dealer")
        cards = [Card(suit="Spades", rank="Jack"), Card(suit="Spades", rank="Ace")]
        for card in cards:
            hand_dealer.add(card)
        hand_dealer.reveal()

        assert hand_dealer.cards == cards
