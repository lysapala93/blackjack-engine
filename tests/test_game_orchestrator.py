from blackjack import Deck
from blackjack import *
from blackjack import Phase, Action
from blackjack import Card
import pytest


class TestGameOrchestration:

    def test_game_init(self):
        game = Game(
            players=[
                "Danny Ocean",
                "Linus Caldwell",
                "Rusty Ryan",
                "Virgil Malloy",
                "Saul Bloom",
            ],
            start_budget=10000,
        )

        players = game.players
        dealer = game.dealer
        deck = game.deck

        assert len(players) == 5
        assert all(isinstance(p, Player) for p in players)
        assert [p.name for p in players][0] == "Danny Ocean"
        assert all(p.budget == 10000 for p in players)

        assert isinstance(dealer, Dealer)
        assert len(deck) == 6 * 52

    def test_change_config_before_start(self):
        game = Game(
            players=["Danny Ocean"],
            start_budget=10000,
        )

        game.config(deck_size=5, start_budget=100000)

        assert len(game.deck) == 5 * 52
        assert game.players[0].budget == 100000

    def test_change_config_after_start_raises(self):
        game = Game(players=["Danny Ocean"], start_budget=10000)
        game.start()

        with pytest.raises(ArithmeticError) as e_info:
            game.config(deck_size=5)

    def test_first_round(self):
        game = Game(players=["Danny Ocean"], start_budget=10000)
        game.start()

        player = game.players[0]
        game.place_bet(player, 100)

        assert game.phase == Phase.PLAYER_TURN
        assert len(player.active_hand) == 2
        assert len(game.dealer.active_hand) == 2

        while game.current_actor is not None:
            game.act(Action.STAND)

        assert game.phase == Phase.BETTING  # round auto-settled and reset
        assert len(player.active_hand) == 0

    def test_splitting(self):
        game = Game(players=["Danny Ocean"], start_budget=5000)
        game.deck._deck = 52 * 6 * [Card(suit="Clubs", rank="Queen")]
        game.start()

        player = game.players[0]
        game.place_bet(player, 100)

        assert game.phase == Phase.PLAYER_TURN
        assert player.active_hand.hand == 2 * [Card(suit="Clubs", rank="Queen")]

        game.act(Action.SPLIT)

        assert len(player.hands) == 2

    def test_splitting_ace(self):
        game = Game(players=["Danny Ocean"], start_budget=5000)
        manipulated_deck = [
            Card(suit="Clubs", rank="Ace"),
            Card(suit="Clubs", rank="King"),
            Card(suit="Hearts", rank="Ace"),
            Card(suit="Hearts", rank="3"),
            Card(suit="Clubs", rank="9"),
            Card(suit="Spades", rank="Ace"),
            Card(suit="Diamonds", rank="Jack"),
        ]
        manipulated_deck.extend(game.deck._deck)
        game.deck._deck = manipulated_deck

        game._game_started = True
        game._deck.set_end_of_shoe(remaining_min=50, remaining_max=80)
        game._phase = Phase.BETTING

        player = game.players[0]
        game.place_bet(player, 100)

        assert game.phase == Phase.PLAYER_TURN
        assert player.active_hand.hand == [
            Card(suit="Clubs", rank="Ace"),
            Card(suit="Hearts", rank="Ace"),
        ]

        game.act(Action.SPLIT)

        assert player.hands[0].stand == True
        assert player.hands[1].stand == False

        game.act(Action.SPLIT)

        assert game.phase == Phase.BETTING
        assert len(game.last_round_results) == 3
        assert [result.player_hand.hand for result in game.last_round_results] == [
            [
                Card(suit="Clubs", rank="Ace"),
                Card(suit="Clubs", rank="9"),
            ],
            [
                Card(suit="Hearts", rank="Ace"),
                Card(suit="Diamonds", rank="Jack"),
            ],
            [
                Card(suit="Spades", rank="Ace"),
                Card(suit="Hearts", rank="2"),
            ],
        ]
        assert all(result.player_hand.stand for result in game.last_round_results)
        assert len(player.hands) == 1
        assert player.hands[0].hand == []

    def test_dealer_peek(self):
        game = Game(players=["Danny Ocean"], start_budget=10000)
        manipulated_deck = [
            Card(suit="Hearts", rank="5"),
            Card(suit="Diamonds", rank="Ace"),
            Card(suit="Spades", rank="10"),
            Card(suit="Hearts", rank="5"),
        ]

        manipulated_deck.extend(game.deck._deck)
        game.deck._deck = manipulated_deck

        game._game_started = True
        game._deck.set_end_of_shoe(remaining_min=50, remaining_max=80)
        game._phase = Phase.BETTING

        player = game.players[0]
        game.place_bet(player, 100)

        assert Action.INSURANCE in game.legal_actions()
