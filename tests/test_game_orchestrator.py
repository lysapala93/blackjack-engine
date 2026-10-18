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
        # dealer shows a 6, so neither insurance nor a peek happens
        game = Game(players=["Danny Ocean"], start_budget=10000)
        game.start()
        game.deck._deck[:0] = [
            Card(suit="Hearts", rank="5"),
            Card(suit="Diamonds", rank="6"),
            Card(suit="Spades", rank="7"),
            Card(suit="Hearts", rank="8"),
        ]
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

    @staticmethod
    def _game_with(cards: list[tuple[str, str]]) -> Game:
        game = Game(players=["Danny Ocean"], start_budget=1000)
        stacked = [Card(suit=suit, rank=rank) for suit, rank in cards]
        stacked.extend(game.deck._deck)
        game.deck._deck = stacked
        game._game_started = True
        game._deck.set_end_of_shoe(remaining_min=50, remaining_max=80)
        return game

    def test_custom_insurance_amount(self):
        game = self._game_with(
            [("Hearts", "5"), ("Diamonds", "Ace"), ("Spades", "10"), ("Hearts", "King")]
        )
        player = game.players[0]
        game.place_bet(player, 100)

        with pytest.raises(ValueError):
            game.take_insurance(player, 51)
        game.take_insurance(player, 20)

        assert game.phase == Phase.BETTING
        assert player.budget == 940  # insurance 20 pays 60 back, main bet lost

    def test_insurance_wins_on_dealer_blackjack(self):
        # player 5, dealer Ace, player 10, dealer King -> dealer blackjack
        game = self._game_with(
            [("Hearts", "5"), ("Diamonds", "Ace"), ("Spades", "10"), ("Hearts", "King")]
        )
        player = game.players[0]
        game.place_bet(player, 100)
        assert game.phase == Phase.INSURANCE

        game.act(Action.INSURANCE)

        assert game.phase == Phase.BETTING
        assert player.budget == 1000  # main bet lost, insurance paid 2:1
        assert game.last_round_results[0].net == -100 + 100

    def test_insurance_lost_without_dealer_blackjack(self):
        game = self._game_with(
            [("Hearts", "5"), ("Diamonds", "Ace"), ("Spades", "10"), ("Hearts", "6")]
        )
        player = game.players[0]
        game.place_bet(player, 100)
        game.act(Action.INSURANCE)

        assert game.phase == Phase.PLAYER_TURN
        assert player.budget == 850  # 100 bet + 50 insurance
        assert Action.INSURANCE not in game.legal_actions()

    def test_peek_on_ten_card_ends_round_without_insurance(self):
        game = self._game_with(
            [("Hearts", "5"), ("Diamonds", "King"), ("Spades", "10"), ("Hearts", "Ace")]
        )
        player = game.players[0]
        game.place_bet(player, 100)

        assert game.phase == Phase.BETTING
        assert player.budget == 900

    def test_peek_on_ten_card_continues_without_blackjack(self):
        game = self._game_with(
            [("Hearts", "5"), ("Diamonds", "King"), ("Spades", "10"), ("Hearts", "7")]
        )
        game.place_bet(game.players[0], 100)

        assert game.phase == Phase.PLAYER_TURN

    def test_player_blackjack_pushes_dealer_blackjack(self):
        game = self._game_with(
            [
                ("Hearts", "Ace"),
                ("Diamonds", "King"),
                ("Spades", "10"),
                ("Hearts", "Ace"),
            ]
        )
        player = game.players[0]
        game.place_bet(player, 100)

        assert game.phase == Phase.BETTING
        assert player.budget == 1000


class TestBetLimits:

    @pytest.mark.parametrize("amount", [19, 1001])
    def test_bet_outside_limits_raises(self, amount):
        game = Game(
            players=["Danny Ocean"], start_budget=5000, min_bet=20, max_bet=1000
        )
        game.start()
        player = game.players[0]

        with pytest.raises(ValueError):
            game.place_bet(player, amount)

        assert player.budget == 5000
        assert player.active_hand.bet == 0
        assert game.phase == Phase.BETTING

    @pytest.mark.parametrize("amount", [20, 1000])
    def test_bet_on_limits_is_accepted(self, amount):
        game = Game(
            players=["Danny Ocean"], start_budget=5000, min_bet=20, max_bet=1000
        )
        game.start()
        # dealer shows a 6: no insurance/peek, so the round waits for the player
        game.deck._deck[:0] = [
            Card(suit="Hearts", rank="5"),
            Card(suit="Diamonds", rank="6"),
            Card(suit="Spades", rank="7"),
            Card(suit="Hearts", rank="8"),
        ]
        player = game.players[0]

        game.place_bet(player, amount)

        assert game.phase == Phase.PLAYER_TURN
        assert player.active_hand.bet == amount
        assert player.budget == 5000 - amount

    @pytest.mark.parametrize("min_bet, max_bet", [(0, 100), (-5, 100), (200, 100)])
    def test_invalid_limits_raise(self, min_bet, max_bet):
        with pytest.raises(ValueError):
            Game(
                players=["Danny Ocean"],
                start_budget=5000,
                min_bet=min_bet,
                max_bet=max_bet,
            )


class TestRoundRules:

    @staticmethod
    def _game_with(cards: list[str], **kwargs) -> Game:
        game = Game(
            players=["Danny Ocean"], start_budget=5000, insurance=False, **kwargs
        )
        game.start()
        game.deck._deck[:0] = [Card(suit="Hearts", rank=rank) for rank in cards]
        return game

    def test_natural_blackjack_needs_no_action(self):
        # player: Ace + King, dealer: 5 + 9 -> 14, draws a 10 and busts
        game = self._game_with(["Ace", "5", "King", "9", "10"])
        player = game.players[0]

        game.place_bet(player, 100)

        assert game.current_actor is None
        assert game.phase == Phase.BETTING
        assert player.budget == 5000 + 150

    def test_split_without_resplitting_hands_are_playable(self):
        # player: 8 + 8, dealer: 5 + 9, split cards: 2, 3
        game = self._game_with(["8", "5", "8", "9", "2", "3"], re_splitting=False)
        player = game.players[0]
        game.place_bet(player, 100)

        game.act(Action.SPLIT)

        assert game.phase == Phase.PLAYER_TURN
        assert len(player.hands) == 2
        assert not any(hand.stand for hand in player.hands)
        assert Action.HIT in game.legal_actions()

    def test_no_resplit_when_re_splitting_disabled(self):
        # player: 8 + 8, dealer: 5 + 9, first split hand draws another 8
        game = self._game_with(["8", "5", "8", "9", "8", "3"], re_splitting=False)
        game.place_bet(game.players[0], 100)

        game.act(Action.SPLIT)

        assert Action.SPLIT not in game.legal_actions()

    def test_max_splittings_caps_number_of_hands(self):
        game = self._game_with(
            ["8", "5", "8", "9", "8", "8", "8", "8"], max_splittings=2
        )
        player = game.players[0]
        game.place_bet(player, 100)

        game.act(Action.SPLIT)

        assert len(player.hands) == 2
        assert Action.SPLIT not in game.legal_actions()


class TestEvenMoney:

    @staticmethod
    def _game_with(cards: list[str], **kwargs) -> Game:
        # deal order: player, dealer, player, dealer (dealer up-card is cards[1])
        game = Game(players=["Danny Ocean"], start_budget=5000, **kwargs)
        game.start()
        game.deck._deck[:0] = [Card(suit="Hearts", rank=rank) for rank in cards]
        return game

    def test_even_money_offered_for_blackjack_against_dealer_ace(self):
        game = self._game_with(["Ace", "Ace", "King", "7"])
        game.place_bet(game.players[0], 100)

        assert game.current_actor is game.players[0]
        assert Action.EVEN_MONEY in game.legal_actions()

    def test_even_money_pays_one_to_one_when_dealer_has_blackjack(self):
        game = self._game_with(["Ace", "Ace", "King", "Queen"])
        player = game.players[0]
        game.place_bet(player, 100)

        game.act(Action.EVEN_MONEY)

        assert game.phase == Phase.BETTING
        assert player.budget == 5000 + 100
        assert game.last_round_results[0].net == 100

    def test_even_money_pays_one_to_one_when_dealer_has_no_blackjack(self):
        game = self._game_with(["Ace", "Ace", "King", "7"])
        player = game.players[0]
        game.place_bet(player, 100)

        game.act(Action.EVEN_MONEY)

        assert game.phase == Phase.BETTING
        assert player.budget == 5000 + 100
        assert game.last_round_results[0].net == 100

    def test_even_money_offered_when_insurance_is_disabled(self):
        game = self._game_with(["Ace", "Ace", "King", "7"], insurance=False)
        game.place_bet(game.players[0], 100)

        assert Action.EVEN_MONEY in game.legal_actions()

    def test_even_money_not_offered_when_disabled(self):
        game = self._game_with(["Ace", "Ace", "King", "7"], even_money=False)
        game.place_bet(game.players[0], 100)

        assert Action.EVEN_MONEY not in game.legal_actions()

    def test_even_money_not_offered_without_player_blackjack(self):
        game = self._game_with(["9", "Ace", "King", "7"])
        game.place_bet(game.players[0], 100)

        assert Action.EVEN_MONEY not in game.legal_actions()


class TestBrokePlayers:

    @staticmethod
    def _game(**kwargs) -> Game:
        game = Game(players=["Danny Ocean", "Rusty Ryan"], start_budget=1000, min_bet=20, **kwargs)
        game.start()
        # dealer shows a 6: no insurance/peek
        game.deck._deck[:0] = [
            Card(suit="Hearts", rank=rank) for rank in ["5", "6", "7", "8", "9", "10"]
        ]
        return game

    def test_broke_player_sits_out_and_round_starts_without_him(self):
        game = self._game()
        broke, rich = game.players
        broke._budget = 10

        with pytest.raises(ValueError):
            game.place_bet(broke, 10)
        game.place_bet(rich, 100)

        assert game.phase == Phase.PLAYER_TURN
        assert game.round_players == [rich]
        assert game.current_actor is rich
        assert len(broke.active_hand) == 0

    def test_broke_player_has_no_round_result(self):
        game = self._game()
        broke, rich = game.players
        broke._budget = 10

        game.place_bet(rich, 100)
        game.act(Action.STAND)

        assert game.phase == Phase.BETTING
        assert [result.player for result in game.last_round_results] == [rich]
        assert broke.budget == 10
        assert game.round_players == []

    def test_player_whose_bet_leaves_him_broke_still_plays(self):
        game = self._game()
        first, second = game.players
        game.place_bet(first, 1000)

        assert game.phase == Phase.BETTING
        game.place_bet(second, 100)
        assert game.round_players == [first, second]

    def test_game_over_only_when_nobody_can_afford_minimum(self):
        game = self._game()
        first, second = game.players

        first._budget = 10
        assert not game.game_over

        second._budget = 19
        assert game.game_over
