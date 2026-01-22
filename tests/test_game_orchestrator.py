from blackjack import *
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
            starting_budget=10000,
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
            starting_budget=10000,
        )

        game.config(deck_size=5, starting_budget=100000)

        assert len(game.deck) == 5 * 52
        assert game.players[0].budget == 100000

    def test_change_config_after_start_raises(self):
        game = Game(players=["Danny Ocean"], starting_budget=10000)
        game.start()

        with pytest.raises(ArithmeticError) as e_info:
            game.config(deck_size=5)
